import socket
import threading
import time
from utils import criar_mensagem, parse_mensagem, ELECTION, OK, COORDINATOR

class ProcessoUDP:
    def __init__(self, id, host, port, peers):
        self.id = id
        self.host = host
        self.port = port
        self.peers = peers
        self.lider = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        threading.Thread(target=self.ouvir, daemon=True).start()

    def ouvir(self):
        while True:
            msg, addr = self.sock.recvfrom(1024)
            tipo, origem_id = parse_mensagem(msg.decode())
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
                    self.sock.sendto(criar_mensagem(tipo, self.id).encode(), (peer[0], peer[1]))
                    print(f"[{self.id}] enviou {tipo} para [{destino_id}]")
                except Exception as e:
                    print(f"[{self.id}] erro ao enviar {tipo} para [{destino_id}]: {e}")
                break

    def iniciar_eleicao(self):
        print(f"[{self.id}] iniciou eleição.")
        maiores = [p for p in self.peers if p[2] > self.id]
        if not maiores:
            self.anunciar_lider()
            return

        for peer in maiores:
            try:
                self.sock.sendto(criar_mensagem(ELECTION, self.id).encode(), (peer[0], peer[1]))
                print(f"[{self.id}] enviou ELECTION para [{peer[2]}]")
            except Exception as e:
                print(f"[{self.id}] erro ao enviar ELECTION para [{peer[2]}]: {e}")

        time.sleep(3)
        if self.lider is None or self.lider < self.id:
            self.anunciar_lider()

    def anunciar_lider(self):
        self.lider = self.id
        print(f"[{self.id}] se declara líder.")
        for peer in self.peers:
            try:
                self.sock.sendto(criar_mensagem(COORDINATOR, self.id).encode(), (peer[0], peer[1]))
                print(f"[{self.id}] enviou COORDINATOR para [{peer[2]}]")
            except Exception as e:
                print(f"[{self.id}] erro ao anunciar líder para [{peer[2]}]: {e}")
