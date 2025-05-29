#!/bin/bash
# run_tcp.sh - roda 3 processos TCP do Bully Algorithm

python3 bully_tcp/main_tcp.py 1 5001 &
python3 bully_tcp/main_tcp.py 2 5002 &
python3 bully_tcp/main_tcp.py 3 5003 &

echo "3 processos TCP rodando em background"
