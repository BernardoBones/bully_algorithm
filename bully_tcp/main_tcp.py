import sys
from processo_tcp import ProcessoTCP

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main_tcp.py <id> <port>")
        sys.exit(1)

    id = int(sys.argv[1])
    port = int(sys.argv[2])

    peers = [
        ("127.0.0.1", 5001, 1),
        ("127.0.0.1", 5002, 2),
        ("127.0.0.1", 5003, 3),
    ]

    processo = ProcessoTCP(id, "127.0.0.1", port, peers)

    # Se for o processo com menor ID, inicia eleição (pode mudar a regra)
    if id == 1:
        processo.iniciar_eleicao()

    # Mantém o programa rodando
    import time
    while True:
        time.sleep(1)
