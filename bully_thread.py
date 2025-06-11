import threading
import time
import random
import logging

# Configuração do logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Process:
    def __init__(self, pid, processes):
        self.pid = pid
        self.processes = processes
        self.coordinator = None
        self.active = True

    def start_election(self):
        if not self.active:
            return
        logging.info(f"Processo {self.pid} iniciou uma eleição.")
        higher = [p for p in self.processes if p.pid > self.pid and p.active]
        if not higher:
            self.become_coordinator()
        else:
            for p in higher:
                p.receive_election(self)

    def receive_election(self, sender):
        if not self.active:
            return
        logging.debug(f"Processo {self.pid} recebeu mensagem de eleição de {sender.pid}.")
        self.start_election()

    def become_coordinator(self):
        if not self.active:
            return
        self.coordinator = self.pid
        logging.info(f"Processo {self.pid} se tornou o coordenador.")
        for p in self.processes:
            p.receive_coordinator(self.pid)

    def receive_coordinator(self, coordinator_pid):
        if not self.active:
            return
        self.coordinator = coordinator_pid
        logging.debug(f"Processo {self.pid} reconhece {coordinator_pid} como coordenador.")

    def fail(self):
        self.active = False
        logging.info(f"Processo {self.pid} falhou.")

    def recover(self):
        self.active = True
        logging.info(f"Processo {self.pid} se recuperou e iniciou uma nova eleição.")
        self.start_election()

def simulate_bully_algorithm():
    processes = [Process(pid, []) for pid in [1, 2, 3, 4, 5]]
    for p in processes:
        p.processes = processes

    threads = []
    for p in processes:
        t = threading.Thread(target=p.start_election)
        threads.append(t)
        t.start()

    time.sleep(2)
    processes[4].fail()

    time.sleep(2)
    processes[3].fail()

    time.sleep(3)
    processes[3].recover()

    time.sleep(10)
    processes[4].recover()

    for t in threads:
        t.join()

if __name__ == "__main__":
    simulate_bully_algorithm()
