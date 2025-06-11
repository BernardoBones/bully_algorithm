import socket
import threading
import time
import logging
from datetime import datetime as dt
from utils import criar_mensagem, parse_mensagem, ELECTION, OK, COORDINATOR

LEADER_QUERY = "LEADER_QUERY"
PING = "PING"
PONG = "PONG"

class ProcessoTCP:
    def __init__(self, id, host, port, peers, log_level=logging.INFO):
        self.id = id
        self.host = host
        self.port = port
        self.peers = peers
        self.lider = None
        self.recebeu_ok = False
        self.lock = threading.Lock()

        self.logger = logging.getLogger(str(self.id))
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(f"[%(asctime)s][%(name)s][%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

        threading.Thread(target=self.ouvir, daemon=True).start()
        threading.Thread(target=self.monitorar_lider, daemon=True).start()
        threading.Thread(target=self.consultar_lideres, daemon=True).start()

    def ouvir(self):
        while True:
            conn, addr = self.server.accept()
            msg = conn.recv(1024).decode()
            conn.close()
            tipo, origem_id = parse_mensagem(msg)
            self.logger.debug(f"recebeu {tipo} de [{origem_id}]")

            if tipo == ELECTION:
                self.enviar_mensagem(origem_id, OK)
                self.iniciar_eleicao()

            elif tipo == OK:
                with self.lock:
                    self.recebeu_ok = True

            elif tipo == COORDINATOR:
                with self.lock:
                    if self.lider is None or origem_id > self.lider:
                        self.lider = origem_id
                        self.logger.info(f"reconhece [{origem_id}] como o novo líder")
                    else:
                        self.logger.debug(f"ignora líder [{origem_id}] porque já conhece líder maior [{self.lider}]")

            elif tipo == LEADER_QUERY:
                with self.lock:
                    if self.lider == self.id:
                        self.enviar_mensagem(origem_id, COORDINATOR)

            elif tipo == PING:
                self.enviar_mensagem(origem_id, PONG)

            elif tipo == PONG:
                pass

    def enviar_mensagem(self, destino_id, tipo):
        for peer in self.peers:
            if peer[2] == destino_id:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((peer[0], peer[1]))
                        s.sendall(criar_mensagem(tipo, self.id).encode())
                    self.logger.debug(f"enviou {tipo} para [{destino_id}]")
                except ConnectionRefusedError:
                    self.logger.warning(f"falha ao enviar {tipo} para [{destino_id}]")
                break

    def iniciar_eleicao(self):
        with self.lock:
            if self.lider is not None and self.lider > self.id:
                self.logger.debug(f"já existe líder maior [{self.lider}], não inicia eleição")
                return
            self.recebeu_ok = False

        self.logger.info("iniciou eleição")
        maiores = [p for p in self.peers if p[2] > self.id]
        if not maiores:
            self.anunciar_lider()
            return

        for peer in maiores:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer[0], peer[1]))
                    s.sendall(criar_mensagem(ELECTION, self.id).encode())
                self.logger.debug(f"enviou ELECTION para [{peer[2]}]")
            except ConnectionRefusedError:
                self.logger.warning(f"não conseguiu contatar [{peer[2]}]")

        espera = 3
        inicio = time.time()
        while time.time() - inicio < espera:
            with self.lock:
                if self.recebeu_ok:
                    self.logger.info("recebeu OK, aguardando líder")
                    return
                if self.lider is not None and self.lider > self.id:
                    self.logger.info(f"líder maior [{self.lider}] detectado, aborta eleição")
                    return
            time.sleep(0.1)

        self.anunciar_lider()

    def anunciar_lider(self):
        with self.lock:
            self.lider = self.id
        self.logger.info("se declara líder")
        for peer in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer[0], peer[1]))
                    s.sendall(criar_mensagem(COORDINATOR, self.id).encode())
                self.logger.debug(f"enviou COORDINATOR para [{peer[2]}]")
            except ConnectionRefusedError:
                self.logger.warning(f"falha ao anunciar líder para [{peer[2]}]")

    def monitorar_lider(self):
        while True:
            time.sleep(5)
            with self.lock:
                lider_atual = self.lider
            if lider_atual is not None and lider_atual != self.id:
                lider_info = next((p for p in self.peers if p[2] == lider_atual), None)
                if lider_info:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(2)
                            s.connect((lider_info[0], lider_info[1]))
                            s.sendall(criar_mensagem(PING, self.id).encode())
                            s.recv(1024)  # espera resposta PONG
                    except (ConnectionRefusedError, socket.timeout):
                        self.logger.warning(f"líder [{lider_atual}] não respondeu, iniciando eleição")
                        with self.lock:
                            self.lider = None
                        self.iniciar_eleicao()

    def consultar_lideres(self):
        time.sleep(2)
        respostas = []

        for peer in self.peers:
            if peer[2] == self.id:
                continue
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((peer[0], peer[1]))
                    s.sendall(criar_mensagem(LEADER_QUERY, self.id).encode())
                    msg = s.recv(1024).decode()
                    tipo, origem_id = parse_mensagem(msg)
                    if tipo == COORDINATOR:
                        respostas.append(origem_id)
            except Exception:
                pass

        if respostas:
            with self.lock:
                self.lider = max(respostas)
            self.logger.info(f"descobriu líder atual como [{self.lider}] ao iniciar")
        else:
            self.logger.info("não encontrou líder, iniciando eleição")
            self.iniciar_eleicao()