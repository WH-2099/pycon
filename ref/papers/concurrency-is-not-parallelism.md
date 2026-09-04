---
conversion: "Official Go talk page converted with Pandoc; slide-specific HTML may remain."
retrieved: "2026-09-04"
source: "https://go.dev/talks/2012/waza.slide"
title: "Concurrency is not Parallelism"
---

<!-- rumdl-disable-file -->

<div class="section slides layout-widescreen">

# Concurrency is not Parallelism

### Waza Jan 11, 2012

<div class="presenter">

Rob Pike

</div>

### Video

This talk was presented at Heroku's Waza conference in January 2012.

<a href="http://vimeo.com/49718712" target="_blank">Watch the talk on Vimeo</a>

<span class="pagenumber">2</span>

### The modern world is parallel

Multicore.

Networks.

Clouds of CPUs.

Loads of users.

Our technology should help.\
That's where concurrency comes in.

<span class="pagenumber">3</span>

### Go supports concurrency

Go provides:

- concurrent execution (goroutines)
- synchronization and messaging (channels)
- multi-way concurrent control (select)

<span class="pagenumber">4</span>

### Concurrency is cool! Yay parallelism!!

NO! A fallacy.

When Go was announced, many were confused by the distinction.

"I ran the prime sieve with 4 processors and it got slower!"

<span class="pagenumber">5</span>

### Concurrency

Programming as the composition of independently executing processes.

(Processes in the general sense, not Linux processes. Famously hard to define.)

<span class="pagenumber">6</span>

### Parallelism

Programming as the simultaneous execution of (possibly related) computations.

<span class="pagenumber">7</span>

### Concurrency vs. parallelism

Concurrency is about dealing with lots of things at once.

Parallelism is about doing lots of things at once.

Not the same, but related.

Concurrency is about structure, parallelism is about execution.

Concurrency provides a way to structure a solution to solve a problem that may (but not necessarily) be parallelizable.

<span class="pagenumber">8</span>

### An analogy

Concurrent: Mouse, keyboard, display, and disk drivers.

Parallel: Vector dot product.

<span class="pagenumber">9</span>

### Concurrency plus communication

Concurrency is a way to structure a program by breaking it into pieces that can be executed independently.

Communication is the means to coordinate the independent executions.

This is the Go model and (like Erlang and others) it's based on CSP:

C. A. R. Hoare: Communicating Sequential Processes (CACM 1978)

<span class="pagenumber">10</span>

### Gophers

This is too abstract. Let's get concrete.

<span class="pagenumber">11</span>

### Our problem

Move a pile of obsolete language manuals to the incinerator.

<div class="image">

![](waza/gophersimple1.jpg)

</div>

With only one gopher this will take too long.

<span class="pagenumber">12</span>

### More gophers!

<div class="image">

![](waza/gophersimple3.jpg)

</div>

More gophers are not enough; they need more carts.

<span class="pagenumber">13</span>

### More gophers and more carts

<div class="image">

![](waza/gophersimple2.jpg)

</div>

This will go faster, but there will be bottlenecks at the pile and incinerator.\
Also need to synchronize the gophers.\
A message (that is, a communication between the gophers) will do.

<span class="pagenumber">14</span>

### Double everything

Remove the bottleneck; make them really independent.

<div class="image">

![](waza/gophersimple4.jpg)

</div>

This will consume input twice as fast.

<span class="pagenumber">15</span>

### Concurrent composition

<div class="image">

![](waza/gophersimple4.jpg)

</div>

The concurrent composition of two gopher procedures.

<span class="pagenumber">16</span>

### Concurrent composition

This design is not automatically parallel!

What if only one gopher is moving at a time?\
Then it's still concurrent (that's in the design), just not parallel.

However, it's automatically parallelizable!

Moreover the concurrent composition suggests other models.

<span class="pagenumber">17</span>

### Another design

<div class="image">

![](waza/gophercomplex0.jpg)

</div>

Three gophers in action, but with likely delays.\
Each gopher is an independently executing procedure,\
plus coordination (communication).

<span class="pagenumber">18</span>

### Finer-grained concurrency

Add another gopher procedure to return the empty carts.

<div class="image">

![](waza/gophercomplex1.jpg)

</div>

Four gophers in action for better flow, each doing one simple task.

If we arrange everything right (implausible but not impossible), that's four times faster than our original one-gopher design.

<span class="pagenumber">19</span>

### Observation

We improved performance by adding a concurrent procedure to the existing design.

More gophers doing more work; it runs better.

This is a deeper insight than mere parallelism.

<span class="pagenumber">20</span>

### Concurrent procedures

Four distinct gopher procedures:

- load books onto cart
- move cart to incinerator
- unload cart into incinerator
- return empty cart

Different concurrent designs enable different ways to parallelize.

<span class="pagenumber">21</span>

### More parallelization!

We can now parallelize on the other axis; the concurrent design makes it easy. Eight gophers, all busy.

<div class="image">

![](waza/gophercomplex2.jpg)

</div>

<span class="pagenumber">22</span>

### Or maybe no parallelization at all

Keep in mind, even if only one gopher is active at a time (zero parallelism), it's still a correct and concurrent solution.

<div class="image">

![](waza/gophercomplex2.jpg)

</div>

<span class="pagenumber">23</span>

### Another design

Here's another way to structure the problem as the concurrent composition of gopher procedures.

Two gopher procedures, plus a staging pile.

<div class="image">

![](waza/gophercomplex3.jpg)

</div>

<span class="pagenumber">24</span>

### Parallelize the usual way

Run more concurrent procedures to get more throughput.

<div class="image">

![](waza/gophercomplex4.jpg)

</div>

<span class="pagenumber">25</span>

### Or a different way

Bring the staging pile to the multi-gopher concurrent model:

<div class="image">

![](waza/gophercomplex5.jpg)

</div>

<span class="pagenumber">26</span>

### Full on optimization

Use all our techniques. Sixteen gophers hard at work!

<div class="image">

![](waza/gophercomplex6.jpg)

</div>

<span class="pagenumber">27</span>

### Lesson

There are many ways to break the processing down.

That's concurrent design.

Once we have the breakdown, parallelization can fall out and correctness is easy.

<span class="pagenumber">28</span>

### Back to Computing

In our book transport problem, substitute:

- book pile =\> web content
- gopher =\> CPU
- cart =\> marshaling, rendering, or networking
- incinerator =\> proxy, browser, or other consumer

It becomes a concurrent design for a scalable web service.\
Gophers serving web content.

<span class="pagenumber">29</span>

### A little background about Go

Not the place for a tutorial, just quick highlights.

<span class="pagenumber">30</span>

### Goroutines

A goroutine is a function running independently in the same address space as other goroutines

<div class="code">

    f("hello", "world") // f runs; we wait

</div>

<div class="code">

    go f("hello", "world") // f starts running
    g() // does not wait for f to return

</div>

Like launching a function with shell's `&` notation.

<span class="pagenumber">31</span>

### Goroutines are not threads

(They're a bit like threads, but they're much cheaper.)

Goroutines are multiplexed onto OS threads as required.

When a goroutine blocks, that thread blocks but no other goroutine blocks.

<span class="pagenumber">32</span>

### Channels

Channels are typed values that allow goroutines to synchronize and exchange information.

<div class="code">

    timerChan := make(chan time.Time)
    go func() {
        time.Sleep(deltaT)
        timerChan <- time.Now() // send time on timerChan
    }()
    // Do something else; when ready, receive.
    // Receive will block until timerChan delivers.
    // Value sent is other goroutine's completion time.
    completedAt := <-timerChan

</div>

<span class="pagenumber">33</span>

### Select

The `select` statement is like a `switch`, but the decision is based on ability to communicate rather than equal values.

<div class="code">

    select {
    case v := <-ch1:
        fmt.Println("channel 1 sends", v)
    case v := <-ch2:
        fmt.Println("channel 2 sends", v)
    default: // optional
        fmt.Println("neither channel was ready")
    }

</div>

<span class="pagenumber">34</span>

### Go really supports concurrency

Really.

It's routine to create thousands of goroutines in one program.\
(Once debugged a program after it had created 1.3 million.)

Stacks start small, but grow and shrink as required.

Goroutines aren't free, but they're very cheap.

<span class="pagenumber">35</span>

### Closures are also part of the story

Make some concurrent calculations easier to express.

They are just local functions.\
Here's a non-concurrent example:

<div class="code">

    func Compose(f, g func(x float) float)
                      func(x float) float {
         return func(x float) float {
            return f(g(x))
        }
    }

    print(Compose(sin, cos)(0.5))

</div>

<span class="pagenumber">36</span>

### Some examples

Learn concurrent Go by osmosis.

<span class="pagenumber">37</span>

### Launching daemons

Use a closure to wrap a background operation.

This copies items from the input channel to the output channel:

<div class="code">

    go func() { // copy input to output
        for val := range input {
            output <- val
        }
    }()

</div>

The `for` `range` operation runs until channel is drained.

<span class="pagenumber">38</span>

### A simple load balancer (1)

A unit of work:

<div class="code">

    type Work struct {
        x, y, z int
    }

</div>

<span class="pagenumber">39</span>

### A simple load balancer (2)

A worker task

<div class="code">

    func worker(in <-chan *Work, out chan<- *Work) {
       for w := range in {
          w.z = w.x * w.y
          Sleep(w.z)
          out <- w
       }
    }

</div>

Must make sure other workers can run when one blocks.

<span class="pagenumber">40</span>

### A simple load balancer (3)

The runner

<div class="code">

    func Run() {
       in, out := make(chan *Work), make(chan *Work)
       for i := 0; i < NumWorkers; i++ {
           go worker(in, out)
       }
       go sendLotsOfWork(in)
       receiveLotsOfResults(out)
    }

</div>

Easy problem but also hard to solve concisely without concurrency.

<span class="pagenumber">41</span>

### Concurrency enables parallelism

The load balancer is implicitly parallel and scalable.

`NumWorkers` could be huge.

The tools of concurrency make it almost trivial to build a safe, working, scalable, parallel design.

<span class="pagenumber">42</span>

### Concurrency simplifies synchronization

No explicit synchronization needed.

The structure of the program is implicitly synchronized.

<span class="pagenumber">43</span>

### That was too easy

Let's do a more realistic load balancer.

<span class="pagenumber">44</span>

### Load balancer

<div class="image">

![](waza/gopherchart.jpg)

</div>

<span class="pagenumber">45</span>

### Request definition

The requester sends Requests to the balancer

<div class="code">

    type Request struct {
        fn func() int  // The operation to perform.
        c  chan int    // The channel to return the result.
    }

</div>

Note the return channel inside the request.\
Channels are first-class values.

<span class="pagenumber">46</span>

### Requester function

An artificial but illustrative simulation of a requester, a load generator.

<div class="code">

    func requester(work chan<- Request) {
        c := make(chan int)
        for {
            // Kill some time (fake load).
            Sleep(rand.Int63n(nWorker * 2 * Second))
            work <- Request{workFn, c} // send request
            result := <-c              // wait for answer
            furtherProcess(result)  
        }    
    }

</div>

<span class="pagenumber">47</span>

### Worker definition

A channel of requests, plus some load tracking data.

<div class="code">

    type Worker struct {
        requests chan Request // work to do (buffered channel)
        pending  int          // count of pending tasks
        index     int         // index in the heap
    }

</div>

<span class="pagenumber">48</span>

### Worker

Balancer sends request to most lightly loaded worker

<div class="code">

    func (w *Worker) work(done chan *Worker) {
        for {
            req := <-w.requests // get Request from balancer
            req.c <- req.fn()   // call fn and send result
            done <- w           // we've finished this request
        }
    }

</div>

The channel of requests (`w.requests`) delivers requests to each worker. The balancer tracks the number of pending requests as a measure of load.\
Each response goes directly to its requester.

Could run the loop body as a goroutine for parallelism.

<span class="pagenumber">49</span>

### Balancer definition

The load balancer needs a pool of workers and a single channel to which requesters can report task completion.

<div class="code">

    type Pool []*Worker

    type Balancer struct {
        pool Pool
        done chan *Worker
    }

</div>

<span class="pagenumber">50</span>

### Balancer function

Easy!

<div class="code">

    func (b *Balancer) balance(work chan Request) {
        for {
            select {
            case req := <-work: // received a Request...
                b.dispatch(req) // ...so send it to a Worker
            case w := <-b.done: // a worker has finished ...
                b.completed(w)  // ...so update its info
            }
        }
    }

</div>

Just need to implement dispatch and completed.

<span class="pagenumber">51</span>

### A heap of channels

Make Pool an implementation of the `Heap` interface by providing a few methods such as:

<div class="code">

    func (p Pool) Less(i, j int) bool {
        return p[i].pending < p[j].pending
    }

</div>

Now we balance by making the `Pool` a heap tracked by load.

<span class="pagenumber">52</span>

### Dispatch

All the pieces are in place.

<div class="code">

    // Send Request to worker
    func (b *Balancer) dispatch(req Request) {
        // Grab the least loaded worker...
        w := heap.Pop(&b.pool).(*Worker)
        // ...send it the task.
        w.requests <- req
        // One more in its work queue.
        w.pending++
        // Put it into its place on the heap.
        heap.Push(&b.pool, w)
    }

</div>

<span class="pagenumber">53</span>

### Completed

<div class="code">

    // Job is complete; update heap
    func (b *Balancer) completed(w *Worker) {
        // One fewer in the queue.
        w.pending--
        // Remove it from heap.                  
        heap.Remove(&b.pool, w.index)
        // Put it into its place on the heap.
        heap.Push(&b.pool, w)
    }

</div>

<span class="pagenumber">54</span>

### Lesson

A complex problem can be broken down into easy-to-understand components.

The pieces can be composed concurrently.

The result is easy to understand, efficient, scalable, and correct.

Maybe even parallel.

<span class="pagenumber">55</span>

### One more example

We have a replicated database and want to minimize latency by asking them all and returning the first response to arrive.

<span class="pagenumber">56</span>

### Query a replicated database

<div class="code">

    func Query(conns []Conn, query string) Result {
        ch := make(chan Result, len(conns))  // buffered
        for _, conn := range conns {
            go func(c Conn) {
                ch <- c.DoQuery(query):
            }(conn)
        }
        return <-ch
    }

</div>

Concurrent tools and garbage collection make this an easy solution to a subtle problem.

(Teardown of late finishers is left as an exercise.)

<span class="pagenumber">57</span>

### Conclusion

Concurrency is powerful.

Concurrency is not parallelism.

Concurrency enables parallelism.

Concurrency makes parallelism (and scaling and everything else) easy.

<span class="pagenumber">58</span>

### For more information

Go: golang.org

Some history: swtch.com/~rsc/thread/

A previous talk (video): tinyurl.com/newsqueak1

Parallelism is not concurrency (Harper): tinyurl.com/pincharper

A concurrent window system (Pike): tinyurl.com/pikecws

Concurrent power series (McIlroy): tinyurl.com/powser

And finally, parallel but not concurrent:\
research.google.com/archive/sawzall.html

<span class="pagenumber">59</span>

### Thank you

<div class="presenter">

Rob Pike

<a href="mailto:r@golang.org" target="_blank">r@golang.org</a>

</div>

</div>

<div id="help">

Use the left and right arrow keys or click the left and right edges of the page to navigate between slides.\
(Press 'H' or navigate to hide this message.)

</div>
