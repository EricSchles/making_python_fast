#How to make Python Blazing Fast with multiprocessing

The multiprocessing module is as close to threads as we currently get in python.  To understand how to use it to make Python code run fast we'll introduce some design patterns.

The main goal of this is to get around the Global Interpreter Lock (GIL) or really any piece of code that will be blocking.  Code that blocks must complete before the next piece of code can execute.  Thus if our code blocks, we can solve multiple problems at once, even in the face of multiple cores (thus we could work on multiple problems at once).  To get around the GIL we're going to need to write code in a funny way, but the results will be well worth it.  

There are some rules of thumb for writing our code to avoid the GIL:

* avoid for loops - use while loops instead
* avoid return statements - use generators or multiprocessing to store state instead

##Example 1

Let's start out with a simple worked example - taking the sum of a bunch of numbers.  As we'll see, the performance gains for this simple example won't be very big, (if they exist at all), but that's because we are doing a small amount of computation for each element.  Let's start off with the a comparison in how we do summation the standard way in python and the multiprocessing way.

```
def for_loop_get_sum(listing):
    summation = 0
    for i in listing:
        summation += i
    return summation
```

```
from multiprocessing import Pool,Manager

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
        try:
        	next_elem = next(get_elem)
        except:
        	next_elem = False
    return dicter["current_sum"]
```

The first piece of code should look familiar, you just start off by looping through each element in your list and add them to a storage for the sum.  

In the second piece of code we are making use of multiprocessing's manager to store the state of the `current_sum`, getting the next element in our list via a generator (until there are no more elements to get), and using `pool.apply_async` to actually do the summation.  This may seem like a lot more "work", but it does pay off, in certain situations, in a very pronounced way.  

Let's dig into what a generator does to understand how they work in this context.  A generator returns the next element in the iteration, rather than starting at the beginning of the iteration.  In our example, we only care about getting the next elementing and applying our summation function to that element, so this works for our context.  Most of the time you don't need to load in elements one at a time, unless they are really big objects that don't fit in memory.  So, for a lot of introductory or even intermediate programmers, generators feel foreign or unnecessary.  In the context of solving "big" problems, they are certainly the right thing to do.  You may have heard of the buzz word, lazy evaulation.  Generators do essentially that.  And allow you access to a primitive to do lazy evaulation for yourself, rather than relaying on the methods of others.  

Okay, now let's dig into the `pool.apply_async` method.  This method, allows us to call a function on multiple inputs, without receiving the result of the previous iteration.  There are lots of contexts when this is very useful, and plenty where this is a bad idea.  For instance, in recursion, where the current value depends on the previous value's result, we wouldn't want to necessarily use an `apply_async`.  In this case, blocking is a good thing.  But there are even tricks around that and some circumstances where doing things asynchronously can still have performance gains.  Getting the sum of two numbers is a perfect example where you can do things asynchronously, this is because the addition operator is commutative - `4+5 = 5+4`.  Whenever your computation exhibits this commutativity, asynchronously application may be a good idea.  

So enough talk!  Let's see if we've made any difference at all:

```
#** Code from above is executed here**
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
```

Let's check out our results :)
```
For  5
standard for loop
3.0994415283203125e-06
multiprocessing version
0.07303714752197266
making use of the built-in sum
2.86102294921875e-06

For  50
standard for loop
8.106231689453125e-06
multiprocessing version
0.027490854263305664
making use of the built-in sum
3.814697265625e-06

For  500
standard for loop
6.604194641113281e-05
multiprocessing version
0.05739903450012207
making use of the built-in sum
1.4066696166992188e-05

For  1000
standard for loop
0.00014591217041015625
multiprocessing version
0.39519476890563965
making use of the built-in sum
2.4080276489257812e-05

For  10000
standard for loop
0.002064943313598633
multiprocessing version
1.9227430820465088
making use of the built-in sum
0.0001709461212158203

For  10000000
standard for loop
0.7831029891967773
multiprocessing version
0.5512580871582031
making use of the built-in sum
0.5721879005432129

For  100000000
standard for loop
9.163938999176025
multiprocessing version
6.650573968887329
making use of the built-in sum
6.139198064804077
```

I want to draw your attention to the last two entries - when our lists get big multiprocessing really starts to hold it's own.  In fact, we're neck and neck with the builtin sum written in C (which is a real accomplishment for native python code).  

##Example 2

If we view the operation we are doing, the sum through the lense of just doing a lot of commutative computation, then we can see the value of multiprocessing.  Treating the sum as some primitive we need apply to a set of data continuously, there is a real performance gain.  And in fact, as we build up this primitive on more and more layers of computation, this gain should become more pronounced.  Let's look at computing all the lists at once now rather than individually.  In order to do this in a multiprocessing context we'll need to update a few things.  Most of the methods are the same, but they are just included for clarity.

```
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

        def get_listing(sizes):
    for list_size in sizes:
        yield [random.randint(0,10000) for _ in range(list_size)],list_size
        
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
        try:
        	next_list,list_size = next(to_compute)
        except: 
        	next_list = False
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
    for i in list_sizes:
        sum([random.randint(0,10000) for _ in range(list_size)])
    print(time.time() - start)
```

The methods that have changed are `get_sum`,`get_listing`,get_sums`,and `summation`.  Now we do all our initialization in the `get_sums` method passing computation into an even more multiprocessed environment.  The major changes are now we pass `dicter` and `list_size` to `get_sum` and thus only need to worry about one global dictionary state, instead of one per computation.  The only disadvantage here, is now we must pass the list_size as a parameter in order to access the correct dictionary sum, because we are non-blocking.  Therefore we have no idea when each sum will be added to.  Passing the full dictionary and the list_size does add a little space complexity to our code, but the gains will translate into a faster overall computation.  Notice also, that we continue to use the while loop, generator design pattern - this allows us to process each list, independently of the others.  This too will translate into performance gains.  

Using just the original list sizes that we used in the last example, we already see that multiprocessing is the clear winner:

```
For [5,50,500,1000,10000,10000000,100000000]
standard for loop
258.19835019111633
multiprocessing version
245.44074892997742
making use of the built-in sum
273.82003593444824

For [10000000,10000000,10000000,10000000,10000000,10000000,10000000]
standard for loop
152.77153706550598
multiprocessing version
140.76755905151367
making use of the built-in sum
144.79858303070068

For [10000,10000,10000,10000,10000,10000,10000,10000]
standard for loop
0.16601991653442383
multiprocessing version
14.650493860244751
making use of the built-in sum
0.21192502975463867
```

There is quiet a bit of interesting stuff happening here.  For cases one and two - doing computation on large data sets, multiprocessing is the clear winner, it even trounces the built-in sum function.  For perspective I included processing on some reasonably small numbers - here we see that multiprocessing does terribly.  Given this context we can see, as our computation becomes more sophisticated and more and more of our computation can be moved into a multithreaded environment, the multiprocessing module will yield significant gains.  It's important to note that it's hard to reason about python code and getting the best performance.  Therefore, whenever possible we must be scientific about our processing time, running experiments, verifying results, and being "computer scientists", reasoning about computation.  For instance, if we compare the previous example with this one, we see a huge decline in performance. The fact that just generating our lists inside of a for-loop and then called the computation for each list, should not lead to a massive decline in performance.  

While this isn't intuitive, we can glean some learning about how to structure computation from this example.  Part of the reason for the difference can probably be attributed directly to how the lists are being generated.  Thus we can see that whenever possible, using preprocessing to initialize any data will always turn to massive gains in performance.  Generating on the fly or generating via generators will usually be less effective in the in memory context.  

However, it's important to note, that this is not the only context for data processing, or manipulating large data in python.  I must reiterate, up until this point, we've been using a "worked" example that doesn't come up often in most programming jobs.  What does come up a lot in practice is working with databases and doing data cleaning, processing and other kinds of work.  In the context of data stored in a database, multiprocessing has a lot of value.  However it will not always be the best solution.  

##Multiprocessing with Databases

For dealing with the database context, we'll be making use of postgres and a very minimal Flask app.  

To install postgres on MacOS - `brew install postgres`

To install postgres on Ubuntu - `sudo apt install postgresql`

Here's a list of commands for reference for postgres

* Listing all the users: `psql -l`
* Create user: `createuser -P -s -e -d username`
* Create DB: `createdb [database_name]`
* running postgresql: `psql [database_name]`
* delete DB: `dropdb [database_name]`


So we are going to create a new user:

`createuser -P -s -e -d eric_schles`

password: `1234`

And we'll create a database:

`createdb fake_data -U eric_schles`

```
from flask import Flask
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand

username,password = "eric_schles","1234"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://"+username+":"+password+"@localhost/backpage_ads"
db = SQLAlchemy(app)
migrate = Migrate(app,db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from app import models
```

