#!/bin/bash
# run_udp.sh - roda 3 processos UDP do Bully Algorithm

python3 bully_udp/main_udp.py 1 6001 &
python3 bully_udp/main_udp.py 2 6002 &
python3 bully_udp/main_udp.py 3 6003 &

echo "3 processos UDP rodando em background"
