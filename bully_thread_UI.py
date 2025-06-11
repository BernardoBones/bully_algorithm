import threading
import time
import random
import logging
import tkinter as tk

# Configuração do logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Process:
    def __init__(self, pid, processes, canvas, x, y):
        self.pid = pid
        self.processes = processes
        self.coordinator = None
        self.active = True
        self.canvas = canvas
        self.x = x
        self.y = y
        self.oval = canvas.create_oval(x, y, x+50, y+50, fill="green")
        self.text = canvas.create_text(x+25, y+25, text=str(pid), fill="white")

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
        self.canvas.itemconfig(self.oval, fill="blue")

    def receive_coordinator(self, coordinator_pid):
        if not self.active:
            return
        self.coordinator = coordinator_pid
        logging.debug(f"Processo {self.pid} reconhece {coordinator_pid} como coordenador.")
        if self.pid != coordinator_pid:
            self.canvas.itemconfig(self.oval, fill="green")

    def fail(self):
        self.active = False
        logging.info(f"Processo {self.pid} falhou.")
        self.canvas.itemconfig(self.oval, fill="red")

    def recover(self):
        self.active = True
        logging.info(f"Processo {self.pid} se recuperou e iniciou uma nova eleição.")
        self.canvas.itemconfig(self.oval, fill="green")
        self.start_election()

def simulate_bully_algorithm():
    root = tk.Tk()
    root.title("Bully Algorithm Simulation")
    canvas = tk.Canvas(root, width=600, height=400)
    canvas.pack()

    positions = [(50, 50), (150, 50), (250, 50), (350, 50), (450, 50)]
    processes = [Process(pid, [], canvas, x, y) for pid, (x, y) in zip([1, 2, 3, 4, 5], positions)]
    for p in processes:
        p.processes = processes

    threads = []
    for p in processes:
        t = threading.Thread(target=p.start_election)
        threads.append(t)
        t.start()

    def fail_process(id):
        processes[id].fail()

    def recover_process(id):
        processes[id].recover()

    # root.after(2000, fail_process(4))
    # root.after(7000, recover_process(4))

    
    root.after(2000, lambda: fail_process(4))
    root.after(2000, lambda: fail_process(3))
    root.after(7000, lambda: recover_process(3))
    root.after(14000, lambda: recover_process(4))


    root.mainloop()

    for t in threads:
        t.join()

if __name__ == "__main__":
    simulate_bully_algorithm()
