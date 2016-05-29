from multiprocessing import Pool,Manager
import time
import random

def generate(listing):
    for elem in listing:
        yield(elem)

def summation(elem,dicter):
    dicter["current_sum"] += elem
    
def get_sum(listing):
    manager = Manager()
    dicter = manager.dict()
    dicter["current_sum"] = 0
    get_elem = generate(listing)
    next_elem = next(get_elem)
    pool = Pool()
    while next_elem:
        pool.apply_async(summation,args=(next_elem,dicter,))
        try:next_elem = next(get_elem)
        except:next_elem = False
    return dicter["current_sum"]

def for_loop_get_sum(listing):
    summation = 0
    for i in listing:
        summation += i
    return summation

def time_comparison(list_size):
    to_compute = [random.randint(0,10000) for _ in range(list_size)]
    print("standard for loop")
    start = time.time()
    for_loop_get_sum(to_compute)
    print(time.time() - start)
    print("multiprocessing version")
    start = time.time()
    get_sum(to_compute)
    print(time.time() - start)
    print("making use of the built-in sum")
    start = time.time()
    sum(to_compute)
    print(time.time() - start)

if __name__ == '__main__':
    for size in [5,50,500,1000,10000,10000000,100000000]:
        print("For ",size)
        time_comparison(size)
        print()
