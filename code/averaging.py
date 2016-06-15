from multiprocessing import Pool,Manager
import time
import random
import statistics
from functools import partial

def generate(listing):
    for elem in listing:
        yield(elem)

def get_element(elem,dicter):
    return elem

def summation(elem,summ):
    summ += elem
    return summ

def get_average(listing):
    summ = 0
    get_elem = generate(listing)
    next_elem = next(get_elem)
    pool = Pool()
    while next_elem:
        summ = pool.apply_async(summation,args=(next_elem,summ,)).get()
        try:
            next_elem = next(get_elem)
        except:
            next_elem = False
    pool.close()
    pool.join()
    return summ

def for_loop_get_average(listing):
    summation = 0
    for i in listing:
        summation += i
    return float(summation)/len(listing)

def time_comparison(list_size):
    to_compute = [random.randint(0,10000) for _ in range(list_size)]
    print("standard for loop")
    start = time.clock()
    for_loop_ave = for_loop_get_average(to_compute)
    print(time.clock() - start)
    print("multiprocessing version")
    start = time.clock()
    multithreaded_ave = get_average(to_compute)
    print(time.clock() - start)
    print("making use of the built-in sum")
    start = time.clock()
    statistics_ave = statistics.mean(to_compute)
    print(time.clock() - start)
    print("Correctness check:")
    print("all three equal:",for_loop_ave == multithreaded_ave == statistics_ave)
    print("for_loop and builtin equal",for_loop_ave == statistics_ave)
    
if __name__ == '__main__':
    for size in [5,50,500,1000,10000,10000000,100000000]:
        print("For ",size)
        time_comparison(size)
        print()
