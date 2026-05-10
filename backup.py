import shutil
import time

def backup():
    name = f"backup_{int(time.time())}.db"
    shutil.copy("punk.db", name)
