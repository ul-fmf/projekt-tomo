class EventLogger:

    def __init__(self, file):
        self.file = open(file, 'w')

    def log(self, event):
        self.file.write(str(event) + "\n")

    def close(self):
        self.file.close()
        