#custom logger for each runner/bot

import os
from datetime import datetime

class BotLogger:

    def __init__(self, fields, filepath):
        folder = filepath.rsplit("/", 1)[0]
        os.makedirs(folder, exist_ok=True)

        self.filepath = filepath
        self.file = open(self.filepath, "a", encoding="utf-8")

        #write the header for easier data reading (i.e. for pandas df later)
        self.file.write(",".join(fields) + "\n")
        self.file.flush()


    def log(self, data):
        ts = datetime.now()
        line = f"{data}"
        # print(line)
        self.file.write(line + "\n")
        self.file.flush()


    def close(self):
        self.file.close()