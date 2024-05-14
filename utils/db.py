import json
import os
import sys
import threading


class JsonDB():
    def __init__(self, name, data):
        # if not os.path.isfile(name): open(name, "w").write("{}")
        self.lock = threading.Lock()
        self.name = name
        self.data = data

    def save(self):
        with self.lock:
            open(self.name, "w").write(json.dumps(self.data))
