from app.models import Data
from app import db
from multiprocessing import Pool,Manager
import time

def generate(query):
    for elem in query:
        yield(elem)

def summation(elem,current_sum):
    current_sum += elem
    return current_sum
        
def get_sum():
    current_sum = 0
    query = db.session.query(Data).yield_per(100).enable_eagerloads(False)
    get_elem = generate(query)
    next_elem = next(get_elem)
    pool = Pool()
    while next_elem:
        current_sum = pool.apply_async(summation,args=(next_elem.datum,current_sum,)).get()
        try:
            next_elem = next(get_elem)
        except:
            next_elem = False
    return current_sum

def get_sum_without_generate():
    current_sum = 0
    query = db.session.query(Data).yield_per(100).enable_eagerloads(False)
    pool = Pool()
    for elem in query:
        current_sum = pool.apply_async(summation,args=(elem.datum,current_sum,)).get()
    return current_sum

def for_loop_get_sum(listing):
    summation = 0
    for i in listing:
        summation += i
    return summation

def time_comparison():
    print("get_sum_generator")
    start = time.clock()
    get_sum()
    print(time.clock() - start)
    print("get_sum_for loop")
    start = time.clock()
    get_sum_without_generate()
    print(time.clock() - start)
    
if __name__ == '__main__':
    time_comparison()
   
