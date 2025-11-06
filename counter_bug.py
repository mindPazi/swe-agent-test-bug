# counter.py
import threading

counter = 0

def increment():
    """
    Increment the global counter.
    Bug: Race condition - multiple threads access and modify counter without synchronization
    Expected: counter should be 1000 after 1000 increments
    Actual: counter will be less than 1000 due to race condition
    """
    global counter
    temp = counter
    temp += 1
    counter = temp

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
    print(f"Expected: 1000")
    if counter < 1000:
        print(f"ERROR: Race condition detected! Counter is {counter} instead of 1000")
    
if __name__ == "__main__":
    run_test()
