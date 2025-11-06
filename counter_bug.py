import threading
import time

counter = 0

def increment():
    global counter
    temp = counter
    time.sleep(0.0001)
    counter = temp + 1

def run_test():
    global counter
    counter = 0
    threads = []
    for i in range(1000):
        t = threading.Thread(target=increment)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Counter value: {counter}")
    print("Expected: 1000")

run_test()
