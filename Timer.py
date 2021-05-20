import time

class Timer:
    def __init__(self):
        self.begin = 0
        self.restart()
    
    def restart(self):
        self.begin = time.time()
    
    def getTimePassed(self):
        return (time.time() - self.begin)
