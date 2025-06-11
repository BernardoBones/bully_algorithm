class Process:
    def __init__(self, pid, processes):
        self.pid = pid
        self.processes = processes
        self.coordinator = None

    def start_election(self):
        print(f"Processo {self.pid} iniciou uma eleição.")
        higher = [p for p in self.processes if p.pid > self.pid]
        if not higher:
            self.become_coordinator()
        else:
            for p in higher:
                p.receive_election(self)

    def receive_election(self, sender):
        print(f"Processo {self.pid} recebeu mensagem de eleição de {sender.pid}.")
        self.start_election()

    def become_coordinator(self):
        self.coordinator = self.pid
        print(f"Processo {self.pid} se tornou o coordenador.")
        for p in self.processes:
            p.receive_coordinator(self.pid)

    def receive_coordinator(self, coordinator_pid):
        self.coordinator = coordinator_pid
        print(f"Processo {self.pid} reconhece {coordinator_pid} como coordenador.")


# Simulação
def simulate_bully_algorithm():
    processes = [Process(pid, []) for pid in [1, 2, 3, 4, 5]]
    for p in processes:
        p.processes = processes

    # processo 3 detecta falha do coordenador
    processes[2].start_election()

simulate_bully_algorithm()
