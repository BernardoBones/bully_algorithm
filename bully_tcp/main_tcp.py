import sys
import time
import logging
import os 
from processo_tcp import ProcessoTCP


print("🚀 Processo iniciado", flush=True)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main_tcp.py <id> <port>")
        sys.exit(1)

    id = int(sys.argv[1])
    port = int(sys.argv[2])

    peers = [
        ("processo1", 5001, 1),
        ("processo2", 5002, 2),
        ("processo3", 5003, 3),
        ("processo4", 5004, 4),
    ]

#     peers = [
#     ("127.0.0.1", 5001, 1),
#     ("127.0.0.1", 5002, 2),
#     ("127.0.0.1", 5003, 3),
#     ("127.0.0.1", 5003, 4),
# ]

    # LOG_LEVEL = logging.INFO

    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_LEVEL = getattr(logging, log_level_str, logging.INFO)
    
    processo = ProcessoTCP(id, "0.0.0.0", port, peers, log_level=LOG_LEVEL)
    # processo = ProcessoTCP(id, "127.0.0.1", port, peers, log_level=LOG_LEVEL)

    # Espera para o processo ficar pronto e consultar líder
    time.sleep(5)

    # Não precisa iniciar eleição manualmente,
    # pois o processo já consulta líder ao iniciar

    # Mantém o programa rodando
    while True:
        time.sleep(1)