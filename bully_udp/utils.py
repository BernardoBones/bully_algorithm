ELECTION = "ELECTION"
OK = "OK"
COORDINATOR = "COORDINATOR"

def criar_mensagem(tipo, origem_id):
    return f"{tipo}:{origem_id}"

def parse_mensagem(msg):
    tipo, origem = msg.split(":")
    return tipo, int(origem)
