import sys
from processo_udp import ProcessoUDP

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main_udp.py <id> <port>")
        sys.exit(1)

    id = int(sys.argv[1])
    port = int(sys.argv[2])

    peers = [
        ("127.0.0.1", 6001, 1),
        ("127.0.0.1", 6002, 2),
        ("127.0.0.1", 6003, 3),
    ]

    processo = ProcessoUDP(id, "127.0.0.1", port, peers)

    if id == 1:
        processo.iniciar_eleicao()

    # Mantém o programa rodando
    import time
    while True:
        time.sleep(1)
