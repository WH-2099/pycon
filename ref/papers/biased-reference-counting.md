---
conversion: "PDF converted with pdftotext -layout; page layout, code, and equations may be imperfect."
retrieved: "2026-09-04"
source: "https://iacoma.cs.uiuc.edu/iacoma-papers/pact18.pdf"
title: "Biased Reference Counting: Minimizing Atomic Operations in Garbage Collection"
---

<!-- rumdl-disable-file -->

                            Biased Reference Counting:
                Minimizing Atomic Operations in Garbage Collection
                                                       Jiho Choi, Thomas Shull, and Josep Torrellas
                                                               University of Illinois at Urbana-Champaign
                                                                        http://iacoma.cs.uiuc.edu

ABSTRACT                                                                                        November 1–4, 2018, Limassol, Cyprus. ACM, New York, NY, USA, 12 pages.
Reference counting (RC) is one of the two fundamental approaches                                https://doi.org/10.1145/3243176.3243195
to garbage collection. It has the desirable characteristics of low
memory overhead and short pause times, which are key in today’s                                 1   INTRODUCTION
interactive mobile platforms. However, RC has a higher execution                                High-level programming languages are widely used today. They
time overhead than its counterpart, tracing garbage collection. The                             provide programmers intuitive abstractions that hide many of the
reason is that RC implementations maintain per-object counters,                                 underlying computer system details, improving both programmer
which must be continually updated. In particular, the execution time                            productivity and portability. One of the pillars of high-level pro-
overhead is high in environments where low memory overhead is                                   gramming languages is automatic memory management. It frees
critical and, therefore, non-deferred RC is used. This is because the                           programmers from the obligation to explicitly deallocate resources,
counter updates need to be performed atomically.                                                by relying on the runtime to automatically handle memory man-
   To address this problem, this paper proposes a novel algorithm                               agement.
called Biased Reference Counting (BRC), which significantly im-                                    Garbage collection is the process of runtime monitoring the life-
proves the performance of non-deferred RC. BRC is based on the                                  time of objects and freeing them once they are no longer necessary.
observation that most objects are only accessed by a single thread,                             There are two main approaches to garbage collection: tracing [28]
which allows most RC operations to be performed non-atomically.                                 and reference counting (RC) [17]. Tracing garbage collection main-
BRC leverages this by biasing each object towards a specific thread,                            tains a root set of live objects and finds the set of objects reachable
and keeping two counters for each object — one updated by the                                   from this root set. Objects not reachable from the root set are consid-
owner thread and another updated by the other threads. This allows                              ered dead and their resources can be freed. RC garbage collection, on
the owner thread to perform RC operations non-atomically, while                                 the other hand, maintains a counter for each object, which tracks
the other threads update the second counter atomically.                                         the number of references currently pointing to the object. This
   We implement BRC in the Swift programming language run-                                      counter is actively updated as references are added and removed.
time, and evaluate it with client and server programs. We find that                             Once the counter reaches zero, the object can be collected.
BRC makes each RC operation more than twice faster in the com-                                     Most implementations of managed languages use tracing garbage
mon case. As a result, BRC reduces the average execution time of                                collection, as RC is believed to be slower. This belief stems from the
client programs by 22.5%, and boosts the average throughput of                                  fact that most of the tracing garbage collection can be done in the
server programs by 7.3%.                                                                        background, off the critical path, while RC is on the critical path.
                                                                                                However, many optimization techniques exist to limit the number
CCS CONCEPTS                                                                                    of RC operations and reduce the overhead on the critical path.
• Software and its engineering → Garbage collection; Soft-                                      Furthermore, RC has the desirable characteristics of low memory
ware performance; Runtime environments;                                                         overhead and short pause times.
                                                                                                   In garbage collection, memory overhead comes from two sources,
KEYWORDS                                                                                        namely garbage collector metadata, and objects that are dead but not
Reference counting; Garbage collection; Swift                                                   yet reclaimed by the garbage collector. While RC adds, as metadata,
                                                                                                one counter per object, RC can have low overall memory overhead
ACM Reference Format:                                                                           because it can be designed to free up objects very soon after they
Jiho Choi, Thomas Shull, and Josep Torrellas. 2018. Biased Reference Count-                     become dead.
ing:, Minimizing Atomic Operations in Garbage Collection. In International                         Pause times are times when the application is stopped, to allow
conference on Parallel Architectures and Compilation Techniques (PACT ’18),
                                                                                                the garbage collector to perform maintenance operations. RC can
                                                                                                be designed to have only short pause times — when individual
Permission to make digital or hard copies of all or part of this work for personal or
classroom use is granted without fee provided that copies are not made or distributed           objects are freed up.
for profit or commercial advantage and that copies bear this notice and the full citation          Overall, the combination of low memory overhead and short
on the first page. Copyrights for components of this work owned by others than the              pause times makes RC suitable for today’s interactive mobile plat-
author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or
republish, to post on servers or to redistribute to lists, requires prior specific permission   forms. For this reason, some languages such as Swift [8] use RC.
and/or a fee. Request permissions from permissions@acm.org.                                        Unfortunately, RC can have significant execution time overhead
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                                  when using algorithms that reclaim objects immediately after they
© 2018 Copyright held by the owner/author(s). Publication rights licensed to ACM.
ACM ISBN 978-1-4503-5986-3/18/11. . . $15.00                                                    become dead — i.e., non-deferred RC algorithms. For example, we
https://doi.org/10.1145/3243176.3243195                                                         find that the non-deferred RC algorithm used in Swift causes Swift
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                                  Jiho Choi, Thomas Shull, and Josep Torrellas


programs to spend 32% of their execution time performing RC              2 BACKGROUND
operations. Still, using non-deferred RC is highly desirable when
                                                                         2.1 Reference Counting
it is critical to keep memory overhead to a minimum, as in many
mobile platforms.                                                        The fundamental idea of RC [17] is to maintain a per-object counter
    We find that a major reason for this execution time overhead         denoting the current number of references to the object. These per-
of non-deferred RC is the use of atomic operations to adjust the         object counters are updated as references are created, reassigned,
reference counters of objects. Note that even if a Swift program         and deleted.
has little sharing and, in fact, even if it is single-threaded, it may      Figure 1 shows a simple program which highlights all possible RC
have to use atomic operations. This is because, like many program-       operations. The normal program commands are on the numbered
ming languages, Swift compiles components separately to allow            lines. The RC operations required for each command are on the
for maximum modularity. Separate compilation forces the compiler         lines directly above the command in gray and are not numbered.
to be conservative. Furthermore, Swift is compiled ahead of time,        A RC operation on an object obj is described by rc(obj). In this
so the compiler cannot leverage program information gathered             example, the reference counts of objects obj 1 , obj 2 , and obj 3 are
throughout execution to limit the use of atomic operations.              adjusted as different assignments execute.
    The goal of this paper is to reduce the execution time overhead
of non-deferred RC. To accomplish this goal, we propose to replace                             rc(obj1) = 1
                                                                                        1      var a = new obj1
the atomic RC operations with biased RC operations. Similar to                                 rc(obj1)++
biased locks [25], our biased operations leverage uneven sharing to                     2      var b = a
create asymmetrical execution times for RC operations based on                                 rc(obj1)--, rc(obj2) = 1
                                                                                        3      b = new obj2
the thread performing the operation. Each object is biased toward,                             rc(obj1)--,rc(obj3) = 1
or favors, a specific thread. This allows an object’s favored thread                           free(obj1)
to perform RC operations without atomic operations, at the cost of                      4      a = new obj3
slowing down all the other threads’ RC operations on that object.                           Figure 1: Basic RC operations.
    While biased RC operations are very effective in most cases,
sometimes multiple threads do try to adjust the reference counter           While the idea of RC is straightforward, it should be implemented
of the same object. To handle this, we exploit the fact that, unlike     carefully to ensure correctness. This is because it is possible to have
locking, RC does not require strong exclusivity. While only one          data races while adjusting reference counters in otherwise correct
thread is allowed to acquire a lock at any given time, it is possible    programs. Consider the code example in Figure 2. Note that in the
for multiple threads to perform RC operations on an object concur-       traditional sense there is no data race in this code. Each thread only
rently — if they use multiple counters and eventually merge the          reads shared variable g, and all writes are performed to thread-local
counters.                                                                variables. However, due to both threads adding another reference
    Based on these ideas, we propose a novel algorithm called Biased     to obj, it is possible for the reference counter of obj to be updated
Reference Counting (BRC), which significantly improves the perfor-       incorrectly without synchronization. In other words, it is possible
mance of non-deferred RC. BRC maintains two counters per object          for the rc(obj)++ corresponding to the commands on lines 2A
— one for the owner thread and another for the other threads. The        and 2B to race and produce incorrect results. Hence, updates to an
owner thread updates its counter without atomic operations; the          object’s reference counter must be done in a synchronized manner.
other threads update the other counter with atomic operations.
    We implement BRC in the Swift runtime. We run various client
                                                                                                 Initialization
and server Swift programs and analyze both their performance and
sharing patterns. Overall, we find that, on average, BRC improves                               rc(obj) = 1
                                                                                              1 var g = new obj;
the execution time of client programs by 22.5%, and the throughput
of server programs by 7.3%.                                                                 Thread A              Thread B
    The contributions of this paper are as follows:
                                                                                         rc(obj)++              rc(obj)++
• Characterizes the overheads of RC in Swift programs.                                2A var a = g;          2B var b = g;
• Characterizes the memory behavior and sharing patterns of Swift
                                                                                            Figure 2: Data race due to RC.
programs.
• Proposes BRC, a new algorithm to reduce the overhead of non-
deferred RC with an efficient biasing technique.                            There are several approaches to synchronizing RC operations.
• Implements BRC in the state-of-the-art Swift runtime.                  The most obvious approach is to add locks around the RC operations.
• Provides a detailed evaluation of BRC’s performance.                   This approach has two main drawbacks. First, the runtime must
                                                                         decide the number of locks to create. At one extreme, the runtime
                                                                         can use a single lock for all objects, but this would incur a lot of
                                                                         contention for the lock by threads trying to adjust the reference
                                                                         counters of different objects. At the other extreme, each object
                                                                         can have its own lock. However, this adds an extra overhead to
                                                                         each object header which can result in less locality and more cache
                                                                         misses. Another problem is that there is very little work done
Biased Reference Counting                                                                                        PACT ’18, November 1–4, 2018, Limassol, Cyprus


in between the lock’s acquisition and release – i.e., one simple                   Because of this, it is unnecessary to adjust obj 1 ’s reference counter
arithmetic operation to adjust the reference counter. This makes                   to reflect var b’s effect, so lines two and three need not adjust
processor stalls likely.                                                           rc(obj 1 ).
   An alternative approach is a lock-free approach using atomic                       Another optimization [21] is to look at sequential chains of RC
operations as shown in Algorithm 1. In this approach, the refer-                   operations on the same object, and find matching pairs of incre-
ence counter is updated using an atomic compare-and-swap (CAS)                     ments and decrements (potentially created by different references).
operation. If the CAS is successful, then the operation is complete.               These RC operations can also be removed, as they negate one an-
Otherwise, the process is repeated until the operation can complete                other.
successfully. This lock-free approach addresses the problems de-
scribed above for the lock-based approach. First, since there are no               2.3          Swift Programming Language
locks, there is no tradeoff between the contention for locks versus                The Swift Programming Language was introduced by Apple in
the memory overhead of locks. Second, this algorithm has only                      2014 [7] as an alternative programming language to Objective-C for
one synchronization operation (the CAS). Because of these benefits,                development for the Apple platform. Due to its support by Apple
modern RC implementations use lock-free algorithms.                                and incorporation into the Apple software ecosystem, Swift has
                                                                                   quickly become popular and is now the preferred programming
Algorithm 1 CAS-based increment operation                                          language for development on the Apple platform.
 1: procedure Increment(ob j )                                                        Like most modern programming languages, Swift has automatic
 2:    do                                                                          memory management. Because of its popularity in the mobile envi-
 3:       old := ob j .r c _count er                            ▷ read old value
 4:       new := old                                                               ronment, where memory overhead is a primary concern, Apple’s
 5:       new += 1                                               ▷ set new value   implementation of Swift uses non-deferred RC and uses the opti-
 6:    while !CAS (&ob j .r c _count er, old, new )                                mizations described in Section 2.2.2. Swift uses weak references
 7:                                                   ▷ Atomic update of counter
 8: end procedure                                                                  to avoid cyclic references, an approach popular in previous litera-
                                                                                   ture [11, 16].

                                                                                   3 MOTIVATION
2.2     RC Optimization
Previous works to optimize RC can be categorized into two groups:
                                                                                   3.1 Overhead of Reference Counting
works that defer reclamation of objects (deferred RC) and works                    To assess the overhead of state-of-the-art non-deferred RC, we mea-
that do not (non-deferred RC).                                                     sure the time spent performing RC operations in Swift programs.
                                                                                   Figure 3 shows, for a set of programs, the fraction of time spent
2.2.1 Deferred RC. These works postpone dead object reclamation,                   on RC operations for each program. The programs we evaluate
and divide execution into distinct mutation and collection phases.                 are explained in detail in Section 6. They include client programs
During mutation phases, RC operations are simplified and there is                  (Swift Bench, CryptoSwift, SwiftyJSON, Raytrace, GCBench-Single,
no reclamation of dead objects; during collection phases, the dead                 GCBench-Multi, and Regex-Redux) and server programs (Perfect-
objects are reclaimed.                                                             JSON, Perfect-Blog, Kitura-JSON, and Kitura-Blog).
    There are two groups of techniques: deferral and coalescing. In
deferral [12, 15, 18, 37–40], the mutation phase does not perform                                         1.00
                                                                                                                                        Rest of Execution
                                                                                           Normalized
RC operations for local pointer variables stored in the stack or
                                                                                                          0.75                          Reference Counting
registers. Then, the collection phase scans the stack and registers,
                                                                                                          0.50
                                                                                         Execution Time
and determines the objects that have a reference count equal to
zero, and therefore can be reclaimed.                                                                     0.25
    In coalescing [26, 32], the mutation phase only records the mod-                                      0.00    Swift Bench
ified pointer variables and their initial values. Then, the collection                                            CryptoSwift
                                                                                                                   SwiftyJSON
                                                                                                                     Raytrace
                                                                                                                    GC-Single
phase compares the initial and final values of the modified pointer                                                   GC-Multi
                                                                                                                 Regex-Redux
                                                                                                                    Client-Avg
                                                                                                                 Perfect-JSON
variables, and performs RC operations only on the objects pointed                                                 Perfect-Blog
                                                                                                                  Kitura-JSON
                                                                                                                   Kitura-Blog
                                                                                                                   Server-Avg
to initially and at the end. Dead objects are found and reclaimed
during the collection phase.                                                                        Figure 3: Overhead of RC in Swift programs.
    A hybrid approach [15] uses simple tracing garbage collection
                                                                                      As shown in the figure, performing RC operations takes on
for young objects and RC for old objects.
                                                                                   average 42% of the execution time in client programs, and 15% in
2.2.2 Optimizations of Non-deferred RC. These techniques remove                    server programs. The average across all programs can be shown to
unnecessary RC operations through static compiler analysis. Some                   be 32%. The Swift compiler does implement optimization techniques
proposals [14, 21–23, 30] eliminate the RC operations for a reference              to reduce the number of RC operations similar to those described
R to an object when R’s lifetime is completely nested in the lifetime              in Section 2.2.2. Without them, the overhead would be higher. The
of another reference to the same object. Figure 1 shows a simple                   RC overhead is lower in server programs than in client programs.
example of a candidate for this optimization. In this figure, the                  This is because server programs spend relatively less time in Swift
lifetime of the reference to obj 1 created on line 2 is completely                 code and RC operations; they spend relatively more time in runtime
nested in the lifetime of the reference to obj 1 created on line 1.                functions for networking and I/O written in C++.
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                                          Jiho Choi, Thomas Shull, and Josep Torrellas


   To estimate the contribution of using atomic operations to this                       Program                   Objects          RC operations
                                                                                         Name                Priv (%) Shar (%)   Priv (%) Shar (%)
overhead, we remove the CAS operation from the RC code. Hence,
                                                                                         Swift
the Swift runtime performs RC without safeguards. As explained                           Benchmark           100.00   0.00       100.00   0.00
in Section 2.1, not using atomic operations is incorrect, and may                        CryptoSwift         100.00   0.00       100.00   0.00

                                                                               Client
result in either memory leaks or objects being prematurely freed.                        SwiftyJSON          100.00   0.00       100.00   0.00
                                                                                         Raytrace            100.00   0.00       100.00   0.00
As a result, we are able to run only a subset of the programs with-                      GCBench-Single      100.00   0.00       100.00   0.00
out crash. We will show later that, on average, not using atomic                         GCBench-Multi       99.84    0.16       99.68    0.32
                                                                                         Regex-Redux         99.99    0.01       51.13    48.87
operations reduces the average execution time of the programs by                         Average             99.98    0.02       92.97    7.03
25%. This means that the large majority of the RC overhead in these                      Perfect-JSON        94.74    5.26       83.99    16.01
programs is due to the use of the CAS operations.                                        Perfect-Blog        94.58    5.42       95.33    4.67

                                                                               Server
   This large overhead is due to two reasons. First, CAS instructions                    Kitura-JSON         91.41    8.59       84.29    15.71
                                                                                         Kitura-Blog         91.59    8.41       83.32    16.68
are more expensive than normal updates. The reason is that there                         Average             93.08    6.92       86.73    13.27
is a memory fence associated with a CAS instruction. This limits
                                                                                        Table 1: Sharing patterns of Swift programs.
the amount of instruction overlapping performed by the hardware,
preventing the out-of-order capabilities of modern cores from being
                                                                           BRC allows these two modes of execution by maintaining sepa-
effectively utilized. Second, due to contention, it may be necessary
                                                                        rate counters for the owner (or biased) thread and for the non-owner
to execute a CAS instruction multiple times before completing
                                                                        threads. The first counter, called the Biased counter, counts the num-
successfully. Note that we run all of our experiments on a modern
                                                                        ber of references to the object added by the owner thread minus
Intel Haswell processor, which has an efficient CAS implementation.
                                                                        those removed by the owner thread. The second counter, called the
                                                                        Shared counter, maintains the active reference count for all non-
3.2    Sharing Patterns of Swift Programs                               owner threads combined. Since the first counter is only accessed by
Since the use of atomic operations greatly affects performance, we      the owner thread, it can be accessed without atomic operations. The
evaluate how often in practice they are necessary for correctness.      second counter may be accessed by multiple threads concurrently.
To do so, we modify the runtime so that, for each RC operation, we      Therefore, it requires atomic operations to prevent data races. The
record which thread is invoking the operation and which object’s        biasing information is maintained on a per-object basis. This allows
reference counter is being updated. We classify objects as private      each object to be biased toward the thread most likely to update its
or shared. An object is classified as private if all of its reference   reference counter.
counter updates throughout its lifetime come from one single thread.       In BRC, an object can be deallocated only when the sum of its two
Otherwise, the object is classified as shared.                          counters is zero. Hence, the two counters first need to be merged.
   Table 1 shows our results. Each row corresponds to a different       Since only the owner thread can read the biased counter reliably,
program. Columns 3 and 4 show the percentage of objects that we         the owner thread is responsible for merging the counters. To merge
classify as private or shared. Columns 5 and 6 show the percentage      the counters, the owner thread first atomically accumulates the
of reference counter updates that go to objects classified as private   biased counter into the shared counter. Next, the owner sets a
or shared. We can see that, on average, over 99% of the objects         flag to indicate that the two counters have been merged. Once the
in client programs, and over 93% of those in server programs are        counters are merged, if the shared counter is zero, the object may
private objects. Similarly, about 93% of the RC operations in client    be deallocated; otherwise, the owner unbiases the object, and all
programs, and about 87% of those in server programs are to private      subsequent reference counter updates will be performed on the
objects. This means that the large majority of RC operations are to     shared counter. When the shared counter reaches zero, the object
private objects, and one could skip the corresponding atomic oper-      may be deallocated.
ation. However, as argued in Section 1, the Swift compiler does not        In the following, we describe the changes that BRC introduces
know this because Swift compiles components separately. Hence,          to the object header, list the invariants in the BRC algorithm, show
Swift is forced to use atomic operations always for correctness.        a few examples of counter transitions, and then describe the BRC
                                                                        algorithm in detail.
4 BIASED REFERENCE COUNTING
                                                                        4.2     Object Header Structure
4.1 Main Idea                                                           To support RC, the compiler reserves one word in each object’s
The goal of this paper is to reduce the overhead of non-deferred        header, called RCWord (for Reference Counting Word). The Swift
RC by minimizing the use of atomic operations. We do this with          runtime uses a 64-bit word. Figure 4 shows the structure of the
a novel algorithm for RC that we call Biased Reference Counting         RCWord. It has a 30-bit counter to keep track of the number of
(BRC). BRC leverages the observation that many objects are only         references to the object. The remaining 34 bits are reserved for
accessed by a single thread. Hence, BRC gives the ownership of, or      weak reference counting and flags to describe the state of the object.
biases, each object to a specific thread. BRC provides two modes of     Weak references are used to prevent cycles, and are outside of the
updating an object’s reference count: the object’s owner thread is      scope of this paper. To prevent race conditions, accesses to RCWord
allowed to update the reference count using non-atomic operations,      always use atomic operations.
while non-owner threads must use atomic operations to update the           BRC modifies RCWord as shown in Figure 5. The new RCWord
reference count.                                                        is now divided into two half-words: Biased and Shared. The biased
Biased Reference Counting                                                                   PACT ’18, November 1–4, 2018, Limassol, Cyprus


                  Counter                          Reserved                    Invariant Description
                                                                               I1: biased + shared = total number of references to object
                     30 bits                        34 bits                         * Must be zero or higher
                                                                                    * If zero, object can be deallocated
                        Figure 4: Original RCWord.                             I2: biased = (references added - references removed) by owner
                                                                                    * Must be zero or higher
                      Biased                        Shared                          * When it reaches 0, owner unbiases object, implicitly merging
                                                                                       counters
            TID                Counter   Counter     Flags    Reserved         I3: shared = (references added - references removed) by non-owners
                                                                                    * Can be negative
           18 bits             14 bits   14 bits     2 bits    16 bits              * If negative, biased must be positive, and object is placed
                                                                                       in owner’s QueuedObjects list so that owner can unbias it
                          Figure 5: BRC’s RCWord.                              I4: Owner only gives up ownership when it merges counters, namely:
                                                                                    * When biased reaches zero (implicit merge)
half-word contains two fields: the owner thread identifier (TID)                    * Or when the owner finds the object in its QueuedObjects
and the biased counter. The TID indicates which thread, if any, the                    list (explicit merge)
                                                                               I5: Object can only be placed into QueuedObjects list once
object is currently biased to. This thread has the exclusive right to               * Placed when shared becomes negative for first time
modify the biased counter.                                                          * Removed when counters are explicitly merged
   The shared half-word contains fields shared by all the threads.                  Table 2: Invariants of the BRC algorithm.
The shared counter field tracks RC activity by non-owner threads.
Then, there are two flags to support the BRC algorithm: Merged
                                                                         global pointer to the object, setting the biased counter to one. Then,
and Queued. The Merged flag is set by the owner thread when it
                                                                         T2 overwrites the global pointer, decrementing the shared counter
has merged the counters. The Queued flag is set by a non-owner
                                                                         of the object. As a result, the shared counter becomes negative.
thread to explicitly request the owner thread to merge counters.
                                                                             When the shared counter for an object becomes negative for
More details about the counter operations are explained later.
                                                                         the first time, the non-owner thread updating the counter also sets
   To prevent race conditions, BRC uses atomic operations to ac-
                                                                         the object’s Queued flag. In addition, it puts the object in a linked
cess the shared half-word. In some situations, the BRC algorithm
                                                                         list belonging to the object’s owner thread called QueuedObjects.
requires multiple fields of the shared half-word to be updated to-
                                                                         Without any special action, this object would leak. This is because,
gether atomically. This is why the flags must be inside of the shared
                                                                         even after all the references to the object are removed, the biased
half-word.
                                                                         counter will not reach zero — since the shared counter is negative.
   BRC reduces the number of bits per counter from 30 bits to 14 bits,
                                                                         As a result, the owner would trigger neither a counter merge nor a
which is more than enough for RC. Many Java programs need only
                                                                         potential subsequent object deallocation.
7 bits [37], and we observe similar behavior in our Swift programs.
                                                                             To handle this case, BRC provides a path for the owner thread to
BRC also reduces the number of the reserved bits used for weak
                                                                         explicitly merge the counters called the ExplicitMerge operation.
reference counting and existing flags to 16 bits. Weak references
                                                                         Specifically, each thread has its own thread-safe QueuedObjects
occur significantly less frequently than regular RC operations, so
                                                                         list. The thread owns the objects in the list. At regular intervals, a
this size is acceptable. Alternatively, we could keep the number of
                                                                         thread examines its list. For each queued object, the thread merges
bits per counter unchanged to 30 by increasing the size of RCWord
                                                                         the object’s counters by accumulating the biased counter into the
at the cost of adding more memory overhead. We evaluate the
                                                                         shared counter. If the sum is zero, the thread deallocates the object.
memory overhead of this alternative design as well in Section 7.4.
                                                                         Otherwise, the thread unbiases the object, and sets the Merged
                                                                         flag. Then, when a thread sets the shared counter to zero, it will
4.3    Algorithm Invariants                                              deallocate the object. Overall, as shown in invariant I4, an owner
To understand the BRC algorithm, we start by describing its main         only gives up ownership when it merges the counters.
invariants. They are described in Table 2. Recall that the value of          Invariant I5 in Table 2 says that an object can be placed into
the counter in the original RCWord (Figure 4) reflects the number        QueuedObjects list only once. It is placed there when its shared
of current references to the object, and must always be zero or          counter becomes negative for the first time. After that, while its
higher. For the same reason, in BRC, invariant I1 in Table 2 says        shared counter may continue to change, since the object is already
that the sum of the biased and shared counters must always be zero       marked as queued, no action is required. It will remain in the
or higher.                                                               owner’s QueuedObjects list until the owner unbiases it.
   Invariant I2 in Table 2 says that the biased counter must always
be zero or higher. This is because, as we will show, as soon as
the biased counter reaches zero, the owner unbiases the object.
                                                                         4.4    Examples of Counter Transitions
This action makes the biased counter inaccessible, and we say it         Figure 6 shows some examples of RCWord transitions in BRC. To
implicitly merges the two counters into the shared counter. The          start with, Figure 6(a) shows the RCWord structure without the Re-
owner thread also sets the Merged flag.                                  served field. Then, in Figure 6(b), we show the RCWord transitions
   On the other hand, I3 says that the shared counter can be negative.   for a private (i.e., thread-local) object. In this example, thread T1
This is because a pair of positive and negative updates may be split     allocates the object and becomes the owner thread. Next, T1 creates
between the biased and shared counters, pushing the shared counter       up to N references to the object, incrementing the biased counter
below zero. As an example, consider two threads T1 and T2. Thread        up to N . Finally, T1 removes these references, decrementing the
T1 creates an object and sets itself as the owner of it. It points a     biased counter to zero, and deallocates the object.
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                                        Jiho Choi, Thomas Shull, and Josep Torrellas

                   Shared        Queued   T1       1      0      0       0
 Thread ID
                   Counter         Flag                                      maximum clarity. BRC’s implementation on the Swift runtime is
                                               T1 allocates an object
                                                                             more efficient than what is shown here.
   TID        BC     SC      M       Q    T1       N      0      0       0      Algorithm 2 shows BRC’s Increment operation. It begins by
                                               T1 creates N references       checking whether the new reference is being created by the object’s
           Biased         Merged
           Counter          Flag                                             owner thread (line 4). If so, the owner thread continues to the
                                          T1       0      0      0       0
                                                                             FastIncrement procedure to increment the biased counter (line 11).
      (a) RCWord Structure
                                            T1 removes all references        Otherwise, a non-owner thread calls SlowIncrement and uses an
                                              T1 deallocates object
      T1       1      0      0        0                                      atomic CAS operation to increment the shared counter (line 19).
                                                (b) Private Object
            T1 allocates an object
                                                                             Algorithm 2 Increment operation
      T1       1      1      0        0   T1       1      0      0       0
                                                                              1: procedure Increment(ob j )             ▷ Increment the reference count of obj
            T2 creates a reference             T1 allocates an object         2:    owner _t id := ob j .r cwor d .biased .t id
                                                                              3:    my _t id := GetT hr ead I D()
               0      1      1        0   T1       1     -1      0       1    4:    if owner _t id == my _t id then
           T1 removes its reference
                                                                              5:        F ast I ncr ement (ob j)                              ▷ Owner access
                                            T2 removes the reference
                                                                              6:    else
            T1 implicitly merges            T2 sets the Queued flag
                                                                              7:        Slow I ncr ement (ob j)                           ▷ Non-owner access
                                                                              8:    end if
               0      0      1        0            0      0      1       1    9: end procedure
           T2 removes its reference              T1 explicitly merges
            T2 deallocates object                T1 deallocates object       10: procedure FastIncrement(ob j )
                                                                             11:    ob j .r cwor d .biased .count er += 1
   (c) Shared Non-Queued Object            (d) Shared Queued Object          12:                                     ▷ Non-atomic increment of biased counter
                                                                             13: end procedure
              Figure 6: Examples of RCWord transitions.
                                                                             14: procedure SlowIncrement(ob j )
   In Figure 6(c), we show the RCWord transitions for a shared               15:    do
                                                                             16:       old := ob j .r cwor d .shar ed                ▷ Read shared half-word
object that is not queued in a QueuedObjects list during its lifetime.       17:       new := old
Thread T1 first allocates the object and sets itself as the owner            18:       new .count er += 1
of it. Next, a second thread T2 creates a reference to the object,           19:    while !CAS (&ob j .r cwor d .shar ed, old, new )
                                                                             20:                                        ▷ Atomic increment of shared counter
incrementing the shared counter. Then, T1 removes its reference to           21: end procedure
the object, decrementing the biased counter. As the biased counter
becomes zero, T1 performs an implicit counter merge: it sets the
Merged flag and unbiases the object. Later, T2 removes its reference             Algorithm 3 shows BRC’s Decrement operation. Similar to Increment,
to the object, decrementing the shared counter. Since the shared             it first checks whether the reference is being removed by the ob-
counter is zero and the Merged flag is set, T2 deallocates the object.       ject’s owner thread (line 4). If so, the owner thread continues to
   In Figure 6(d), we show the RCWord transitions for a shared               the FastDecrement procedure to decrement the biased counter
object that is queued in a QueuedObjects list during its lifetime.           (line 11). If the resulting value of the counter is higher than zero
Thread T1 first allocates the object and sets itself as the owner            (line 13), no further action is required. Otherwise, the biased counter
of it. Then, thread T2 overwrites the reference to the object and            is zero, and the owner thread performs an implicit merge of the
hence decrements the shared counter. Since the shared counter                counters. Specifically, it sets the Merged flag (line 19) by atomically
becomes negative, T2 also sets the Queued flag and places the object         updating the shared half-word (line 20). Next, the shared counter
in T1’s QueuedObjects list. Later, T1 invokes the ExplicitMerge              is read. If its value is zero (line 22), the object is deallocated. Other-
operation and explicitly merges the counters, setting the Merged             wise, BRC unbiases the object by clearing the owner TID (line 25).
flag and unbiasing the object. Since the sum of the counters is zero,        Now, all future RC operations to this object will invoke either the
T1 deallocates the object.                                                   SlowIncrement or the SlowDecrement procedures. In addition, any
                                                                             thread can make the decision to deallocate the object. Note that the
                                                                             Deallocate call in line 23 does not need to lock the object. This
4.5        BRC Algorithm                                                     is because the last reference has been removed so no other thread
                                                                             can access the object.
The BRC algorithm introduces several changes to a conventional
                                                                                 If the Decrement operation is invoked by a non-owner thread,
RC algorithm. First, when an object is allocated, BRC saves the ID of
                                                                             it continues to the SlowDecrement procedure (line 28). BRC decre-
the thread allocating the object in the RCWord, effectively biasing
                                                                             ments the shared counter (line 32) and, if the counter’s new value
the object. Second, BRC modifies the RC operations (i.e., Increment
                                                                             is negative, BRC also sets the Queued flag (line 34). The shared
and Decrement) to update one of the two RCWord counters based
                                                                             half-word is updated atomically (line 36). If the Queued flag has
on which thread an object is biased to. Finally, BRC adds two new
                                                                             been set for the first time by this invocation (line 38), BRC invokes
operations, Queue and ExplicitMerge, to handle a special case
                                                                             function Queue to insert the object in a list to be handled later by
introduced by using two counters. In the following paragraphs, we
                                                                             the owner (line 40) — note that this case implies that the counters
explain these operations in detail. We use a dot notation to access
                                                                             have not been merged yet, as the shared counter’s value is negative.
the biased and shared half-words, and their fields in the algorithms.
                                                                             Otherwise, if the Merged flag is set and the shared counter is zero
Note that the algorithms given below sacrifice performance for
                                                                             (line 41), BRC deallocates the object.
Biased Reference Counting                                                                                   PACT ’18, November 1–4, 2018, Limassol, Cyprus

Algorithm 3 Decrement operation                                                         Algorithm 4 Extra operations
 1: procedure Decrement(ob j )             ▷ Decrement the reference count of obj        1: procedure Queue(ob j )
 2:    owner _t id := ob j .r cwor d .biased .t id                                       2:    owner _t id := ob j .r cwor d .biased .t id
 3:    my _t id := GetT hr ead I D()                                                     3:    QueuedOb ject s[owner _t id ].append (ob j)
 4:    if owner _t id == my _t id then                                                   4:                                    ▷ Adds object to list belonging to owner_tid
 5:        F ast Decr ement (ob j)                               ▷ Owner access          5: end procedure
 6:    else
 7:        Slow Decr ement (ob j)                            ▷ Non-owner access          6: procedure ExplicitMerge
 8:    end if                                                                            7:    my _t id := GetT hr ead I D()
 9: end procedure                                                                        8:    for all ob j ∈ QueuedOb ject s[my _t id] do
                                                                                         9:        do
10: procedure FastDecrement(ob j )                                                      10:            old := ob j .r cwor d .shar ed              ▷ Read shared half-word
11:    ob j .r cwor d .biased .count er −= 1                                            11:            new := old
12:                                      ▷ Non-atomic decrement of biased counter       12:            new .count er += ob j .r cwor d .biased .count er
13:    if ob j .r cwor d .biased .count er > 0 then                                     13:                                                               ▷ Merge counters
14:        return                                                                       14:            new .mer дed :=True
15:    end if                                                                           15:        while !CAS (&ob j .r cwor d .shar ed, old, new )
16:    do                                                  ▷ biased counter is zero     16:                                             ▷ Atomic update of shared half-word
17:        old := ob j .r cwor d .shar ed                  ▷ Read shared half-word      17:        if new .count er == 0 then
18:        new := old                                                                   18:            Deallocat e(ob j)
19:        new .mer дed :=True                                    ▷ Set merged flag     19:        else
20:    while !CAS (&ob j .r cwor d .shar ed, old, new )                                 20:            ob j .r cwor d .biased .t id := 0              ▷ Give up ownership
21:                                            ▷ Atomic update of shared half-word      21:        end if
22:    if new .count er == 0 then                                                       22:       QueuedOb ject s[my _t id ].r emove(ob j)
23:        Deallocat e(ob j)                                                            23:    end for
24:    else                                                                             24: end procedure
25:        ob j .r cwor d .biased .t id := 0                   ▷ Give up ownership
26:    end if                                                                           and, for each object, explicitly merges its two counters. Note that
27: end procedure
                                                                                        this merging can only be done by the owner thread, so the procedure
28: procedure SlowDecrement(ob j )                                                      only accesses the QueuedObjects list owned by the thread invoking
29:    do                                                                               the procedure (line 8). For each object in the list, BRC accumulates
30:        old := ob j .r cwor d .shar ed                  ▷ Read shared half-word
31:        new := old                                                                   the biased counter into the shared counter (line 12) and sets the
32:        new .count er −= 1                                                           Merged flag (line 14). This change is atomic (line 15). If the merged
33:        if new .count er < 0 then                                                    counter becomes zero, the owner deallocates the object (line 18).
34:            new .queued :=True                                   ▷ Set queued flag
35:        end if                                                                       Otherwise, it unbiases the object (line 20) so that all future RC
36:    while !CAS (&ob j .r cwor d .shar ed, old, new )                                 operations are performed on the shared counter. Once this merging
37:                                           ▷ Atomic decrement of shared counter
38:    if old .queued , new .queued then
                                                                                        is completed, it is no longer possible for the object to be leaked,
39:                                    ▷ queued has been first set in this invocation   and thus the owner removes the object from QueuedObjects in a
40:        Queue(ob j)                                                                  thread-safe manner (line 22).
41:    else if new .mer дed ==True and new .count er == 0 then
42:                                ▷ Counters are merged and shared counter is zero        A given object can only be put in the QueuedObjects list once.
43:        Deallocat e(ob j)                                                            This is because, before an object is taken out of the list, its counters
44:    end if                                                                           are merged. Such merging eliminates the possibility that the shared
45: end procedure
                                                                                        counter become negative anymore.
   BRC adds two new operations, Queue and ExplicitMerge (Al-                               Lastly, when a thread terminates, it processes the objects re-
gorithm 4), to support a special case introduced by having two                          maining in its QueuedObjects list, and de-registers itself from
counters. Specifically, the first time that the shared counter attains                  the QueuedObjects structure. Theoretically, an object can out-
a negative value, Queue is invoked. As indicated in Section 4.3, at                     live its owner thread if its biased counter is positive, and has not
this point, the biased counter has a positive value. If BRC did not                     been queued in the QueuedObjects list when the owner thread
take any special action, the biased counter might never be decre-                       terminates. We handle this case as follows. When a non-owner
mented to zero and, thus, the counters might never be merged, and                       thread makes the shared counter of an object negative, it first
the object might never be deallocated. This is a memory leak.                           checks whether the object’s owner thread is alive by looking-up
   To guard against such scenarios, BRC keeps track of objects                          the QueuedObjects structure — which implicitly records the live
that may leak. As shown in the Queue procedure of Algorithm 4,                          threads. If the owner thread is not alive, the non-owner thread
the non-owner thread that first finds that the shared counter be-                       merges the counters instead of queuing the object, and either deal-
comes negative, inserts the object in a thread-safe list belonging                      locates the object or unbiases it.
to the object’s owner thread. The list is part of a structure called
QueuedObjects (line 3), which is organized as per-thread lists of
potentially leaked objects. Potentially leaked objects are added to                     5    PUTTING BRC IN CONTEXT
the QueuedObjects list belonging to the object’s owner thread.                          In this section, we qualitatively compare BRC to other RC algo-
   At regular intervals, a thread checks its QueuedObjects list,                        rithms. Table 4 examines the space-time trade-off of various RC
to explicitly merge counters and enable object deallocation. The                        implementations. Each row corresponds to a different RC implemen-
ExplicitMerge procedure of Algorithm 4 performs this operation.                         tation. The table ranks the RC implementations from 1 (lowest) to 4
The procedure searches through the thread’s QueuedObjects list                          (highest) in terms of performance overhead and memory overhead.
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                                                         Jiho Choi, Thomas Shull, and Josep Torrellas

                 Program           Multi-
                 Name              threaded?       Description
                 Swift Benchmark   No              A set of 212 benchmarks covering a number of important Swift workloads designed to track Swift performance and catch
                                                   performance regressions
                 CryptoSwift       No              Performance tests of a Swift package for cryptography algorithms
                 SwiftyJSON        No              Performance tests of a Swift package for JSON handling

        Client
                 Raytrace          No              Ray tracing application
                 GCBench-Single    No              Single-threaded implementation of an artificial garbage collection benchmark that creates perfect binary trees
                 GCBench-Multi     Yes             Multi-threaded implementation of GCBench
                 Regex-Redux       Yes             Benchmark that uses regular expressions to match and replace DNA 8-mers
                 Perfect-JSON      Yes             JSON generator running on the Perfect framework

        Server
                 Perfect-Blog      Yes             Blog engine running on the Perfect framework
                 Kitura-JSON       Yes             JSON generator running on the Kitura framework
                 Kitura-Blog       Yes             Blog engine running on the Kitura framework
                                                            Table 3: Client and server programs used.


   Algorithm                                   Performance
                                               Overhead
                                                                   Memory Over-
                                                                   head
                                                                                             6     EXPERIMENTAL SETUP
   Basic non-deferred RC                       4                   1 (tie)                   To evaluate BRC, we implement it in the Swift version 3.1.1 run-
   Non-deferred RC w/ optimization             3                   1 (tie)                   time. We evaluate the three configurations shown in Table 5. The
   Deferred RC (DRC)                           1                   3
   BRC                                         2                   2
                                                                                             Original configuration (O) is the unmodified Swift runtime, which
                                                                                             implements RC with lock-free atomic operations. The Ideal con-
Table 4: Ranking performance and memory overheads of RC                                      figuration (I) takes O and eliminates all the atomic operations. In
implementations from 1 (lowest) to 4 (highest).                                              this configuration, due to data races, counters may have incorrect
                                                                                             values. In particular, an object may be accessed after being deal-
   The first row corresponds to the basic non-deferred RC described
                                                                                             located, which may lead to a crash. We collect data from I only
in Section 2.1. It suffers from a high execution time overhead due to
                                                                                             when the program runs to completion, and its output and number
frequent atomic RC operations. However, it has a minimal memory
                                                                                             RC operations are same as in O’s execution. This ensures that I
overhead thanks to immediate reclamation.
                                                                                             did not change semantics. Lastly, the biased configuration (B) is
   The second row corresponds to the non-deferred RC with the
                                                                                             O enhanced with BRC. As a result, all of Swift’s RC optimizations
optimization described in Section 2.2.2. This is Swift’s RC imple-
                                                                                             (which are present in O) are enabled in B by default.
mentation. Compared to basic non-deferred RC, the execution time
overhead is dramatically reduced. This is because many unnec-                                                 Name     Configuration
essary RC operations are removed at compile time. Specifically,                                               O        Original: The unmodified Swift runtime
we found that Swift removes up to 97% of RC operations in our                                                 I        Ideal: O with no atomic operations
programs. This implementation is very effective at removing RC                                                B        Biased: O enhanced with BRC
operations for local variables. At the same time, it maintains im-                                            Table 5: Configurations evaluated.
mediate reclamation, and hence has the same minimal memory
overhead as the basic non-deferred RC.                                                           Table 3 shows the client and server programs that we evaluate.
   The third row corresponds to deferred RC (DRC) implementa-                                The official Swift Benchmark Suite [6] consists of a set of tests
tions, as described in Section 2.2.1. The performance overhead is                            which cover important Swift workloads. The suite is designed to
lower, as deferral and coalescing avoid atomic RC operations during                          track Swift performance and catch performance regressions. Cryp-
the mutation phase. However, since DRC does not perform imme-                                toSwift [2] and SwiftyJSON [10] are popular Swift packages for
diate reclamation for all objects, the memory overhead is higher                             cryptography and JSON handling, respectively. We also use a Swift
than the basic non-deferred RC.                                                              version of ray tracing [9]. GCBench [1] is an artificial garbage col-
   The last row corresponds to BRC. While Swift’s non-deferred                               lection benchmark which creates and discards perfect binary trees
RC with optimization is fast, it is still slower than DRC (about                             to estimate the collector performance. We use single-threaded and
20% [21]). BRC narrows this performance gap by replacing atomic                              multi-threaded implementations of GCBench. Lastly, Regex-Redux
RC operations with non-atomic ones in most cases. It also retains                            is a regular expression benchmark that uses regular expressions to
immediate reclamation for most objects in our programs. Hence, it                            match and replace DNA sequences.
increases the memory overhead very little compared to the basic                                  Our server programs are based on two popular server-side frame-
non-deferred RC. We discuss BRC’s impact on performance and                                  works for Swift, namely Perfect [4] and Kitura [3]. For each frame-
memory in Section 7.3 and 7.4 in detail.                                                     work, we run a blog engine that returns random images and blog
   Overall, we believe that BRC enables a new space-time trade-off                           posts for each request, and a JSON generator that returns a JSON
in the RC design space, different from what has been proposed thus                           dictionary of random numbers for each request [5]. For the server
far. Further, we believe that BRC aligns well with Swift’s philosophy                        programs, we measure throughput instead of execution time.
that emphasizes speed and low memory consumption.                                                We run our experiments on a desktop machine with an Intel
                                                                                             Core i7 processor and 16 GB of memory running Ubuntu 16.04 LTS.
                                                                                             The processor has four cores cycling at 3.50 GHz. Each experiment
                                                                                             is run 10 times and the average is reported.
Biased Reference Counting                                                                                    PACT ’18, November 1–4, 2018, Limassol, Cyprus

                                                        Original                                                Biased
                                     % of     Obj.      RC       RC Ops.    RC        % of          % of RC Ops. % of RC Ops.   % of     % of RC Ops.
                    Program          Shared   Allocs.   Ops.     per        Ops.      RC Ops. to    to Biased       to Shared   Queued   Setting
                    Name             Obj.     per µ s   per µ s Obj.        per µ s   Shared Obj.   Counter         Counter     Obj.     Queued Flag
                    Swift            0.00     1.91      29.18    15.24      33.16     0.00          100.00         0.00         0.00     0.00
                    Benchmark
                    CryptoSwift      0.00     2.39      56.54    23.61      68.16     0.00          100.00         0.00         0.00     0.00

           Client
                    SwiftyJSON       0.00     2.60      68.19    26.24      93.77     0.00          100.00         0.00         0.00     0.00
                    Raytrace         0.00     0.00      101.70   27258.42   173.94    0.00          100.00         0.00         0.00     0.00
                    GCBench-Single   0.00     12.87     64.07    4.98       86.03     0.00          100.00         0.00         0.00     0.00
                    GCBench-Multi    0.16     50.69     150.39   2.97       195.44    0.32          99.97          0.03         0.01     0.00
                    Regex-Redux      0.01     2.58      92.61    35.91      123.99    48.87         88.02          11.98        0.00     0.00
                    Average          0.02     10.44     80.38    39338.19   110.64    7.03          84.00          1.72         0.00     0.00
                    Perfect-JSON     5.26     0.55      4.56     8.25       4.95      16.01         88.64          11.36        1.99     0.24

           Server
                    Perfect-Blog     5.42     0.45      12.57    27.95      12.90     4.67          96.72          3.28         1.95     0.07
                    Kitura-JSON      8.59     0.40      7.27     18.05      7.55      15.71         87.38          12.62        2.76     0.15
                    Kitura-Blog      8.41     0.39      6.12     15.81      6.34      16.68         86.68          13.32        2.70     0.17
                    Average          6.92     0.45      7.63     17.51      7.93      13.27         89.85          10.15        2.35     0.16
                                                          Table 6: Reference counting statistics.


7 EVALUATION                                                                           programs, and 0.16% in server programs. Overall, queuing in the
                                                                                       QueuedObjects list is a negligible overhead.
7.1 Characterization
We start by investigating the overhead of RC in the Original (O)                       7.2     Latency of RC Operations
and Biased (B) configurations. Table 6 shows various metrics of RC
                                                                                      We measure the time it takes to increment a reference counter in the
behavior during execution for both configurations. For reference,
                                                                                      different configurations. For this measurement, we create kernels
Column 3 repeats the data shown in Table 1 about the percentage
                                                                                      that repeatedly increment the counter in a loop. Therefore, the
of shared objects in each program. Recall that we consider an object
                                                                                      operations have a near-perfect cache behavior. In addition, these
as shared if its reference counter updates come from more than
                                                                                      kernels are single-threaded and, therefore, the measured times do
one thread. Next, Columns 4-6 refer to the O configuration, while
                                                                                      not include contention. Overall, our experiments measure best-case
columns 7-12 refer to the B configuration.
                                                                                      timings.
   Columns 4 and 5 show the number of object allocations per
                                                                                         Table 7 shows the time to perform a counter increment in our
µsecond and the number of RC operations per µsecond, respectively.
                                                                                      different configurations: O, I , and B. For the B configuration, we
The latter are counter increments and decrements. Based on the
                                                                                      show the operation time for the owner thread and for non-owner
data in these two columns, Column 6 shows the average number of
                                                                                      threads. As shown in the table, the increment operation takes 13.84
RC operations per object. We can see that, discounting Raytrace,
                                                                                      ns in O and 5.77 ns I . Hence, the use of atomic operations slows
there are 3–36 RC operations per object in client programs, and
                                                                                      down the operation by 2.40x. In B, the owner’s increment takes only
8–28 in server programs.
                                                                                      6.28 ns, while the non-owner increment takes 15.57 ns. Ideally, the
   Column 7 shows the number of RC operations per µsecond in
                                                                                      former should be as fast as I , while the latter should take as long as
the B configuration. Due to the improved performance of B, these
                                                                                      O. In practice, BRC adds some overhead to each of these operations,
numbers are higher than in O for all the programs.
                                                                                      as the TID and various flags are checked before performing the
   Column 8 shows the percentage of RC operations to shared
                                                                                      increment. Consequently, B owner takes 8.8% longer than I , and B
objects, and Columns 9 and 10 the percentage of RC operations
                                                                                      non-owner takes 12.5% longer than O.
to the biased and shared counters, respectively. We see that only
a small percentage of the RC operations are performed on shared
objects (7.03% in client programs and 13.27% in server programs),                                   Configuration                        Time (ns)
and an even smaller percentage are performed on shared counters                                     Original                                    13.84
(1.72% in client programs and 10.15% in server programs). The                                       Ideal                                        5.77
outlier is Regex-Redux, where nearly 50% of the RC operations are                                   Biased (operation by owner)                  6.28
on shared objects, and 12% use the shared counter. Overall, the                                     Biased (operation by non-owner)             15.57
small fraction of the RC operations that use the shared counter is                             Table 7: Time of counter increment operations.
the reason for the speed-ups of B over O; only such operations use
atomic instructions.
   Column 11 shows the percentage of the total objects that are
queued. On average, this number is 0.00% in client programs, and                       7.3     Performance Improvement
2.35% in server programs. This number is very small, in part because                   In this section, we evaluate the performance improvements attained
the percentage of objects that are shared (Column 3) is already small.                 by BRC. Figure 7 shows the execution time of the client programs
Finally, Column 12 shows the percentage of RC operations that set                      for the O, I , and B configurations, normalized to the O configuration.
the Queued flag and add the object to the QueuedObjects list. We                       On average, B reduces the execution time by 22.5% over O. This is
see that this is a rare event, which occurs 0.00% of the time in client                a substantial speed-up, which is attained inexpensively in software
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                                                  Jiho Choi, Thomas Shull, and Josep Torrellas




                                                                                 Normalized
by improving the RC algorithm. Further, this speed-up implies that
a large fraction of the RC overhead in O has been eliminated. Indeed,                            1.1     Original           Biased
as shown in Figure 3, client programs spend on average 42% of their
                                                                                                 1.0

                                                                             Peak Memory Usage
time in RC operations. With B, it can be shown that we eliminate
more than half of such RC time.                                                                  0.9
                 1.00                                                                            0.8

  Normalized
                                                                                                        Swift Bench
                                                                                                        CryptoSwift
                                                                                                         SwiftyJSON
                 0.75                                                                                      Raytrace
                                                                                                          GC-Single

Execution Time
                                                                                                            GC-Multi
                                                                                                       Regex-Redux
                 0.50
                                                                                                       Perfect-JSON
                                                                                                        Perfect-Blog
                                                                                                        Kitura-JSON
                                Original          Ideal             Biased
                                                                                                         Kitura-Blog
                                                                                                            Average
                 0.25
                         Cry nch
                             pto
                          Sw wift
                             iftySe
                                  JSO                                        Figure 9: Peak memory usage under the O and B configura-
                  ift       Ra N
                           GC ceytr a                                        tions.
                      B     GC
                        Re -Mul
                               -Si ng le
                 Sw       ge x-R i
                                 ed    t
                            Av xera  u
                                     ge                                         We observe that, on average, B has only a 1.5% higher mem-
Figure 7: Execution time of client programs under the O, I ,                 ory overhead than O. Single-threaded programs (i.e., the first 5
and B configurations.                                                        programs) have no additional memory overhead in B because the
                                                                             shared counter is not used and, consequently, there are no queued
   We see that, on average, the B configuration is within 3.7% of            objects. While GCBench-single and Regex-Redux are multithreaded,
the I configuration. This difference is smaller than the 8.8% differ-        they have negligible additional memory overhead because they have
ence observed in Table 7 between the B (owner) and I increment               almost no queued objects (Column 11 of Table 6). The server pro-
operations. This is due to Amdahl’s law, as programs only spend a            grams have only a small fraction of queued objects and, therefore,
fraction of their time performing RC operations.                             their additional memory overhead is on average about 4%.
   Figure 8 shows the throughput of the server programs under the               We also measure the memory overhead in the alternative B im-
O and B configurations, normalized to the O configuration. We do             plementation described in Section 4.2, where we add an additional
not show data for the I configuration because running these pro-             64-bit word to the object header to preserve 30-bit counters. In this
grams without atomic operations causes frequent program crashes              case, the peak memory usage in B can be shown to be, on average,
due to premature object deallocations. The figure shows that B               a modest 6% higher than in O.
attains a substantial average throughput increase of 7.3% over O.
This improvement is smaller than the 22.5% average reduction in              7.5                 Sensitivity Study
the execution time of the client programs. This is expected, given           To simulate a worst-case scenario for BRC, we create a synthetic
that the overhead of RC in Figure 3 is higher in the client programs         benchmark where we can control the number of queued objects.
than in the server ones.                                                     In the benchmark, a main thread creates 1,000,000 objects, creat-
                                                                             ing a reference to each object, then performs a fixed amount of
                 1.1                                                         dummy computation, and finally removes any remaining references

Normalized
                                                                             to the objects. In parallel, a second thread removes the references
                 1.0                                                         to 1, 000, 000 × R objects allocated by the main thread. When a
Throughput       0.9                                                         shared counter becomes negative, the second thread adds the cor-
                                      Original             Biased            responding object to the main thread’s QueuedObjects list. In our
                 0.8                                                         experiments, we vary R, which we call Ratio of Queued Objects.
                          N
                         JSO
                                     g
                                    Blo         ON         og         ge     Figure 10 shows the execution time and peak memory usage under
                                ct-         -JS           -Bl       era      the B configuration as we vary R, normalized to the O configuration.
                        ct-    rfe         ura        ura       Av
                   rfe         Pe         Kit        Kit
                  Pe
Figure 8: Throughput of the server programs under the O
and B configurations.                                                                                  Execution Time             Peak Memory Usage
                                                                                 1.2
                                                                                 1.0
7.4              Memory Overhead                                                 0.8
In this section, we evaluate BRC’s memory overhead by comparing                  0.6
the peak memory usage of the O and B configurations. Figure 9                                    0.0      0.2          0.4      0.6      0.8         1.0
shows the peak memory usage of these configurations normalized                                                   Ratio of Queued Objects
to the peak memory usage of O. Recall from Section 4.2 that our
                                                                             Figure 10: Normalized execution time and normalized peak
BRC design does not increase the size of the per-object RCWord.
                                                                             memory usage of the B configuration as we vary the number
Hence, the additional memory overhead of B comes from the use
                                                                             of queued objects.
of the QueuedObjects structure.
Biased Reference Counting                                                                      PACT ’18, November 1–4, 2018, Limassol, Cyprus


   Our results show that, for B to perform worse than the O config-       queued objects. However, their technique uses more atomic oper-
uration, one needs 75% or more queued objects. In reality, as shown       ations than BRC due to its conservative escape detection, and its
in Table 6, the percentage of queued objects in our programs is           lack of the notion of biased threads. In addition, it increases the
much lower than this break-even point.                                    overhead of the store barrier to detect and recursively mark escap-
   We also measure the additional memory overhead of B for this           ing objects. Finally, it does not fully support all of Swift’s function
benchmark. As we see in the figure, the additional memory over-           argument passing semantics.
head is kept low, under 12% over the O configuration. This is be-
cause the counter merging and object dequeuing happen frequently          9    CONCLUSION
enough that reclamation of dead queued objects is not delayed too         This paper proposed Biased Reference Counting (BRC), a novel
much. Note that, for our programs in Table 6, the percentage of           approach to speed-up non-deferred RC for garbage collection. BRC
queued objects is very small and, therefore, the additional memory        is based on the observations that most objects are mostly accessed
overhead of BRC is small.                                                 by a single thread, and that atomic operations have significant
                                                                          overheads. BRC biases each object toward a specific thread. Further,
                                                                          BRC adds a second counter to the object header, enabling the owner
8   RELATED WORK                                                          thread to have its own counter. These changes allow the owner
There have been many works [19, 25, 29, 34–36, 42] which try to           thread of each object to perform RC operations without atomic
limit the amount of overhead to acquire uncontested locks. While          operations, while the other threads atomically update the other
BRC is inspired by biased locking [25], it is not a straightforward       counter. BRC correctly manages the merging of these two counters,
re-application of biased locking. BRC proposes an efficient biasing       handling all corner cases.
technique tailored to RC by exploiting the fact that RC does not             We implemented BRC in the Swift programming language run-
require strong exclusivity like locking. BRC lets multiple threads ac-    time and evaluated it with various client and server programs. We
cess the same object concurrently, by dividing an object’s reference      found that BRC accelerated non-deferred RC. Specifically, it re-
count into two counters. In biased locking, this is not possible. BRC     duced the average execution time of client programs by 22.5%, and
also makes ownership revocation very cheap. This is because own-          improved the average throughput of server programs by 7.3%.
ership is typically voluntarily revoked in BRC and only requires
one CAS. On the other hand, ownership revocation is extremely             ACKNOWLEDGMENTS
expensive in biased locking. It is triggered by a non-owner thread,       This work was supported in part by NSF under grant CCF 15-27223.
and requires inter-thread communication through OS signals or
safepoints. This is the main drawback of biased locking.                  REFERENCES
    Subsequent works on biased locking [19, 29, 34–36, 42] improve         [1] An Artificial Garbage Collection Benchmark. http://www.hboehm.info/gc/gc_
on the original work by making ownership revocation more effi-                 bench.html
cient, enabling ownership transfer, or determining when it is best         [2] CryptoSwift. https://github.com/krzyzanowskim/CryptoSwift
                                                                           [3] Kitura: A Swift Web framework and HTTP Server. http://www.kitura.io/
to bias an object. It is possible to apply such ownership transfer         [4] Perfect: Server-side Swift. http://perfect.org/
techniques to BRC. In future work, we plan to implement similar            [5] Server-side swift benchmarks.                        https://github.com/rymcol/
techniques to better support various program behaviors.                        Server-Side-Swift-Benchmarks-Summer-2017
                                                                           [6] Swift Benchmark Suite. https://github.com/apple/swift/tree/master/benchmark
    Many prior works on RC [12, 14, 15, 18, 21–23, 26, 30, 32, 37–         [7] Swift Has Reached 1.0. https://developer.apple.com/swift/blog/?id=14
40] focus on reducing the number of RC operations. They are are            [8] Swift Programming Language. https://swift.org/.
                                                                           [9] Swift Version of Ray Tracing. https://github.com/rnapier/raytrace
briefly summarized in Section 2.2, and compared to BRC in Sec-            [10] SwiftyJSON. https://github.com/SwiftyJSON/SwiftyJSON
tion 5. Another category of works attempt to efficiently detect and       [11] T. H. Axford. 1990. Reference Counting of Cyclic Graphs for Functional Programs.
remove cyclic references [13, 24, 27, 31, 33]. Swift solves this prob-         Comput. J. 33, 5 (1990), 466–472.
                                                                          [12] David F. Bacon, Clement R. Attanasio, Han B. Lee, V. T. Rajan, and Stephen Smith.
lem through weak references, an approach popular in previous                   2001. Java Without the Coffee Breaks: A Nonintrusive Multiprocessor Garbage
literature [11, 16]. We believe that BRC can also be integrated into           Collector. In Proceedings of the ACM SIGPLAN 2001 Conference on Programming
RC implementations with cyclic reference detection and removal                 Language Design and Implementation (PLDI ’01). 92–103.
                                                                          [13] David F. Bacon and V. T. Rajan. 2001. Concurrent Cycle Collection in Reference
algorithms.                                                                    Counted Systems. In Proceedings of the 15th European Conference on Object-
    Joao et al. [20] propose hardware support for RC. They augment             Oriented Programming (ECOOP ’01). 207–235.
                                                                          [14] Jeffrey M. Barth. 1977. Shifting Garbage Collection Overhead to Compile Time.
the cache hierarchy to gradually merge RC operations. Due to the               Commun. ACM 20, 7 (1977), 513–518.
delay of merging in hardware, their technique does not support            [15] Stephen M. Blackburn and Kathryn S. McKinley. 2003. Ulterior Reference Count-
immediate reclamation. In contrast, BRC supports immediate recla-              ing: Fast Garbage Collection Without a Long Wait. In Proceedings of the 18th
                                                                               Annual ACM SIGPLAN Conference on Object-oriented Programing, Systems, Lan-
mation in most cases.                                                          guages, and Applications (OOPSLA ’03). 344–358.
    Recently, Ungar et al. [41] propose a compiler-assisted dynamic       [16] David R. Brownbridge. 1985. Cyclic reference counting for combinator machines.
optimization technique for RC in Swift. It is similar to BRC in that it        In Conference on Functional Programming and Computer Architecture. 273–288.
                                                                          [17] George E. Collins. 1960. A Method for Overlapping and Erasure of Lists. Commun.
dynamically replaces atomic RC operations with non-atomic ones.                ACM 3, 12 (Dec. 1960), 655–657.
It adds checks before stores to conservatively capture escaping           [18] L. Peter Deutsch and Daniel G. Bobrow. 1976. An Efficient, Incremental, Auto-
                                                                               matic Garbage Collector. Commun. ACM 19, 9 (1976), 522–526.
objects, and uses atomic RC operations for escaped objects only.          [19] David Dice, Mark Moir, and William Scherer III. 2003. Quickly Reacquirable Locks.
Compared to BRC, their technique maintains the immediate recla-                Technical Report. Sun Microsystem Laboratories.
mation property of non-deferred RC, while BRC relaxes this for            [20] José A. Joao, Onur Mutlu, and Yale N. Patt. 2009. Flexible Reference-counting-
                                                                               based Hardware Acceleration for Garbage Collection. In Proceedings of the 36th
PACT ’18, November 1–4, 2018, Limassol, Cyprus                                             Jiho Choi, Thomas Shull, and Josep Torrellas


     Annual International Symposium on Computer Architecture (ISCA ’09). 418–428.
[21] Pramod G. Joisha. 2006. Compiler Optimizations for Nondeferred Reference-
     Counting Garbage Collection. In Proceedings of the 5th International Symposium
     on Memory Management (ISMM ’06).
[22] Pramod G. Joisha. 2007. Overlooking Roots: A Framework for Making Non-
     deferred Reference-counting Garbage Collection Fast. In Proceedings of the 6th
     International Symposium on Memory Management (ISMM ’07). 141–158.
[23] Pramod G. Joisha. 2008. A Principled Approach to Nondeferred Reference-
     counting Garbage Collection. In Proceedings of the 4th ACM SIGPLAN/SIGOPS
     International Conference on Virtual Execution Environments (VEE ’08). 131–140.
[24] Richard E. Jones and Rafael D. Lins. 1993. Cyclic Weighted Reference Counting
     Without Delay. In Proceedings of the 5th International PARLE Conference on Parallel
     Architectures and Languages Europe (PARLE ’93). 712–715.
[25] Kiyokuni Kawachiya, Akira Koseki, and Tamiya Onodera. 2002. Lock Reservation:
     Java Locks Can Mostly Do Without Atomic Operations. In Proc. of the 17th Annual
     ACM SIGPLAN Conference on Object-oriented Programming, Systems, Languages,
     and Applications (OOPSLA ’02).
[26] Yossi Levanoni and Erez Petrank. 2001. An On-the-fly Reference Counting
     Garbage Collector for Java. In Proceedings of the 16th ACM SIGPLAN Conference
     on Object-oriented Programming, Systems, Languages, and Applications (OOPSLA
     ’01). 367–380.
[27] A. D. Martínez, R. Wachenchauzer, and R. D. Lins. 1990. Cyclic Reference Count-
     ing with Local Mark-scan. Inf. Process. Lett. 34, 1 (1990), 31–35.
[28] John McCarthy. 1960. Recursive Functions of Symbolic Expressions and Their
     Computation by Machine, Part I. Commun. ACM 3, 4 (1960), 184–195.
[29] Tamiya Onodera, Kikyokuni Kawachiya, and Akira Koseki. 2004. Lock Reser-
     vation for Java Reconsidered. In Proceedings of the 18th European Conference on
     Object-Oriented Programming (ECOOP ’04).
[30] Young Gil Park and Benjamin Goldberg. 1991. Reference Escape Analysis: Opti-
     mizing Reference Counting Based on the Lifetime of References. In Proceedings
     of the 1991 ACM SIGPLAN Symposium on Partial Evaluation and Semantics-based
     Program Manipulation (PEPM ’91). 178–189.
[31] Harel Paz, David F. Bacon, Elliot K. Kolodner, Erez Petrank, and V. T. Rajan. 2007.
     An Efficient On-the-fly Cycle Collection. ACM Trans. Program. Lang. Syst. 29, 4
     (2007).
[32] Harel Paz and Erez Petrank. 2007. Using Prefetching to Improve Reference-
     counting Garbage Collectors. In Proceedings of the 16th International Conference
     on Compiler Construction (CC’07). 48–63.
[33] Harel Paz, Erez Petrank, David F. Bacon, Elliot K. Kolodner, and V. T. Rajan. 2005.
     An Efficient On-the-fly Cycle Collection. In Proceedings of the 14th International
     Conference on Compiler Construction (CC’05). 156–171.
[34] Filip Pizlo, Daniel Frampton, and Antony L. Hosking. 2011. Fine-grained Adaptive
     Biased Locking. In Proceedings of the 9th International Conference on Principles
     and Practice of Programming in Java (PPPJ ’11). 171–181.
[35] Ian Rogers and Balaji Iyengar. 2011. Reducing Biased Lock Revocation by Learn-
     ing. In Proceedings of the 6th Workshop on Implementation, Compilation, Opti-
     mization of Object-Oriented Languages, Programs and Systems. 65–73.
[36] Kenneth Russell and David Detlefs. 2006. Eliminating Synchronization-related
     Atomic Operations with Biased Locking and Bulk Rebiasing. In Proceedings of the
     21st Annual ACM SIGPLAN Conference on Object-oriented Programming Systems,
     Languages, and Applications (OOPSLA ’06). 263–272.
[37] Rifat Shahriyar, Stephen M. Blackburn, and Daniel Frampton. 2012. Down for
     the Count? Getting Reference Counting Back in the Ring. In Proceedings of the
     2012 International Symposium on Memory Management (ISMM ’12). 73–84.
[38] Rifat Shahriyar, Stephen M. Blackburn, and Kathryn S. McKinley. 2014. Fast
     Conservative Garbage Collection. In Proceedings of the 2014 ACM International
     Conference on Object-oriented Programming Systems Languages, and Applications
     (OOPSLA ’14). 121–139.
[39] Rifat Shahriyar, Stephen Michael Blackburn, Xi Yang, and Kathryn S. McKinley.
     2013. Taking off the Gloves with Reference Counting Immix. In Proceedings of
     the 2013 ACM SIGPLAN International Conference on Object-oriented Programming
     Systems Languages, and Applications (OOPSLA ’13). 93–110.
[40] David Ungar. 1984. Generation Scavenging: A Non-disruptive High Performance
     Storage Reclamation Algorithm. In Proceedings of the First ACM SIGSOFT/SIG-
     PLAN Software Engineering Symposium on Practical Software Development Envi-
     ronments (SDE 1). 157–167.
[41] David Ungar, David Grove, and Hubertus Franke. 2017. Dynamic Atomicity:
     Optimizing Swift Memory Management. In Proceedings of the 13th ACM SIGPLAN
     International Symposium on Dynamic Languages (DLS ’17). 15–26.
[42] Nalini Vasudevan, Kedar S. Namjoshi, and Stephen A. Edwards. 2010. Simple and
     Fast Biased Locks. In Proceedings of the 19th International Conference on Parallel
     Architectures and Compilation Techniques (PACT ’10). 65–74.

