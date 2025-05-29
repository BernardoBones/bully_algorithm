.PHONY: tcp udp clean

# Variáveis
PYTHON=python3

# Rodar 3 processos TCP
tcp:
	$(PYTHON) bully_tcp/main_tcp.py 1 5001 &
	$(PYTHON) bully_tcp/main_tcp.py 2 5002 &
	$(PYTHON) bully_tcp/main_tcp.py 3 5003 &

# Rodar 3 processos UDP
udp:
	$(PYTHON) bully_udp/main_udp.py 1 6001 &
	$(PYTHON) bully_udp/main_udp.py 2 6002 &
	$(PYTHON) bully_udp/main_udp.py 3 6003 &

clean:
	# Finaliza todos os processos Python (CUIDADO: fecha todos os Python do usuário)
	killall python3 || true
