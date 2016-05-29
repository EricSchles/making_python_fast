from multiprocessing import Pool,Manager
import time
import random

def get_element(listing):
    for elem in listing:
        yield(elem)

def summation(elem,dicter,list_size):
    dicter[list_size] += elem
    
def get_sum(listing,dicter,list_size):
    dicter[list_size] = 0
    get_elem = generate(listing)
    next_elem = next(get_elem)
    pool = Pool()
    while next_elem:
        pool.apply_async(summation,args=(next_elem,dicter,list_size,))
        try:next_elem = next(get_elem)
        except:next_elem = False

def for_loop_get_sum(listing):
    summation = 0
    for i in listing:
        summation += i
    return summation

def get_listing(sizes):
    for list_size in sizes:
        yield [random.randint(0,10000) for _ in range(list_size)],list_size
        
def get_sums(sizes):
    to_compute = get_listing(sizes)
    next_list,list_size = next(to_compute)
    manager = Manager()
    dicter = manager.dict()
    pool = Pool()
    while next_list:
        pool.apply_async(get_sum,args=(next_list,dicter,list_size,))
        try:next_list,list_size = next(to_compute)
        except: next_list = False
    return dicter
    
def time_comparison(list_sizes):
    print("standard for loop")
    start = time.time()
    for list_size in list_sizes:
        for_loop_get_sum([random.randint(0,10000) for _ in range(list_size)])
    print(time.time() - start)
    print("multiprocessing version")
    start = time.time()
    get_sums(list_sizes)
    print(time.time() - start)
    print("making use of the built-in sum")
    start = time.time()
    for list_size in list_sizes:
        sum([random.randint(0,10000) for _ in range(list_size)])
    print(time.time() - start)

if __name__ == '__main__':
    time_comparison([5,50,500,1000,10000,10000000,100000000])
    time_comparison([10000000,10000000,10000000,10000000,10000000,10000000,10000000])
    time_comparison([10000,10000,10000,10000,10000,10000,10000,10000])
    # for size in [5,50,500,1000,10000,10000000,100000000]:
    #     print("For ",size)
    #     time_comparison(size)
    #     print()
