import random
import threading
import time

class Generator(threading.Thread):
    def __init__(self, a=0, b=50000, timeout_val = -1, vault_size=10):
        threading.Thread.__init__(self) 
        self.id = random.randint(4614, 46464)
        self.please_kill_me = False
        self.min = a
        self.max = b
        self.value = random.randint(self.min, self.max)
        self.time_count = 0
        self.timeout_in_seconds = timeout_val
        self.sleep_delay = 0.1

        self.vault = []
        self.vault_size = vault_size
        self.vault.append(self.value)

    def check_time(self):
        # Timeout not set
        if self.timeout_in_seconds != -1:
            return self.time_count <= self.timeout_in_seconds
        return False

    def run(self):
        self.start_time = time.time()

        while (self.check_time() or self.timeout_in_seconds < 0) and self.please_kill_me == False:
            self.value = random.randint(self.min, self.max)
            self.vault.append(self.value)
            self.vault = self.vault[:self.vault_size]
            
            self.time_count = time.time() - self.start_time
            time.sleep(self.sleep_delay)
        self.please_kill_me = True
        return 1
