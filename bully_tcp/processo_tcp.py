import socket
import threading
import time
from utils import criar_mensagem, parse_mensagem, ELECTION, OK, COORDINATOR

class ProcessoTCP:
    def __init__(self, id, host, port, peers):
        self.id = id
        self.host = host
        self.port = port
        self.peers = peers  # lista de (host, port, id)
        self.lider = None

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

        threading.Thread(target=self.ouvir, daemon=True).start()

    def ouvir(self):
        while True:
            conn, addr = self.server.accept()
            msg = conn.recv(1024).decode()
            conn.close()
            tipo, origem_id = parse_mensagem(msg)
            print(f"[{self.id}] recebeu {tipo} de [{origem_id}]")

            if tipo == ELECTION:
                self.enviar_mensagem(origem_id, OK)
                self.iniciar_eleicao()
            elif tipo == COORDINATOR:
                self.lider = origem_id
                print(f"[{self.id}] reconhece [{origem_id}] como o novo líder.")

    def enviar_mensagem(self, destino_id, tipo):
        for peer in self.peers:
            if peer[2] == destino_id:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((peer[0], peer[1]))
                        s.sendall(criar_mensagem(tipo, self.id).encode())
                    print(f"[{self.id}] enviou {tipo} para [{destino_id}]")
                except ConnectionRefusedError:
                    print(f"[{self.id}] falha ao enviar {tipo} para [{destino_id}]")
                break

    def iniciar_eleicao(self):
        print(f"[{self.id}] iniciou eleição.")
        maiores = [p for p in self.peers if p[2] > self.id]
        if not maiores:
            self.anunciar_lider()
            return

        for peer in maiores:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer[0], peer[1]))
                    s.sendall(criar_mensagem(ELECTION, self.id).encode())
                print(f"[{self.id}] enviou ELECTION para [{peer[2]}]")
            except ConnectionRefusedError:
                print(f"[{self.id}] não conseguiu contactar [{peer[2]}]")
        time.sleep(3)
        if self.lider is None or self.lider < self.id:
            self.anunciar_lider()

    def anunciar_lider(self):
        self.lider = self.id
        print(f"[{self.id}] se declara líder.")
        for peer in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer[0], peer[1]))
                    s.sendall(criar_mensagem(COORDINATOR, self.id).encode())
                print(f"[{self.id}] enviou COORDINATOR para [{peer[2]}]")
            except ConnectionRefusedError:
                print(f"[{self.id}] falha ao anunciar líder para [{peer[2]}]")
