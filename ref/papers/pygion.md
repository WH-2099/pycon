---
conversion: "PDF converted with pdftotext -layout; page layout, code, and equations may be imperfect."
retrieved: "2026-09-04"
source: "https://legion.stanford.edu/pdfs/pygion2019.pdf"
title: "Pygion: Flexible, Scalable Task-Based Parallelism with Python"
---

<!-- rumdl-disable-file -->

   Pygion: Flexible, Scalable Task-Based Parallelism
                      with Python
                                  Elliott Slaughter                                      Alex Aiken
                      SLAC National Accelerator Laboratory                            Stanford University
                           eslaught@slac.stanford.edu                               aiken@cs.stanford.edu



   Abstract—Dynamic languages provide the flexibility needed to  (data races, deadlocks, etc.) that can occur in programs written
implement expressive support for task-based parallel program-    in traditional programming models.
ming constructs. We present Pygion, a Python interface for          Task-based programs are conceptually simpler than ones
the Legion task-based programming system, and show that it
can provide features comparable to Regent, a statically typed    written in traditional programming models, but for two reasons
programming language with dedicated support for the Legion       they can sometimes be longer than one might expect, especially
programming model. Furthermore, we show that the dynamic         when written in C++. First, task-based programs reify the data
nature of Python permits the implementation of several key       flows in a program, as any data to be used by a task must
optimizations (index launches, futures, mapping) currently imple-be explicitly identified in the task’s arguments, along with a
mented in the Regent compiler. Together these features enable
Pygion code that is comparable in expressiveness but more        corresponding privilege. This reification is an essential feature
flexible than Regent, and substantially more concise, less error that drives the other advantages of task-based systems. Second,
prone, and easier to use than C++ Legion code. Pygion is designedcertain low-level features of task-based runtime systems, which
to interoperate with Regent and can use Regent to generate high- are necessary for performance, are exposed in the runtime
performance CPU and GPU kernel implementations. We show          APIs for these systems making programming at this level
that, in combination with high-performance kernels written in
                                                                 more complicated than necessary. These issues are challenging
Regent, Pygion is able to achieve efficient, scalable execution on
up to 512 nodes of the heterogeneous supercomputer Piz Daint.    to address in a C or C++ API as these languages lack type
   Index Terms—task-based parallelism, Pygion, Legion, Python    system features necessary to capture the relevant programming
                                                                 system invariants [6], which in turn results in a C/C++ interface
                      I. I NTRODUCTION                           which is verbose, error-prone, and low-level compared to the
   A growing class of users in the physical sciences and conceptual model of task-based systems (see Section III).
data analytics are unfamiliar with traditional high-performance     Programming languages with dedicated support for task-
programming models and languages, yet need access to high- based programming constructs can address this mismatch. For
performance computational resources. This issue is of particular example, Regent [7] is a high-level programming language
relevance to science user facilities such as the Linac Coherent that supports the Legion programming model. The Regent type
Light Source (LCLS) [1], which regularly host users with system enforces many of the low-level invariants required for
no formal training in computer programming and who need writing correct Legion programs, and the compiler provides a
to process and analyze increasingly large volumes of data number of critical optimizations that improve performance and
produced by scientific experiments [2]. In many cases, analyses scalability [8]. However the cost of enforcing these invariants
must be written, debugged and executed on the fly as the exper- in the Regent type system is that the compiler must necessarily
iment is in progress. These users typically program in Python, be conservative, making it difficult or impossible to express
but still need a path to achieve productive, high-performance certain code patterns in an application.
programming on current and future supercomputers.                   In this paper, we explore an alternative approach based on
   Task-based programming models provide a promising path the dynamic programming language Python. A key observation
forward. Such models, which include Legion [3], PaRSEC [4] is that many program analysis problems that are difficult
and StarPU [5], simplify the programming of heterogeneous or intractable to solve at compile time can be solved in a
supercomputers by providing sequential semantics. Tasks (or straightforward manner using dynamic analysis. Type system
functions marked for parallel execution) are enumerated in invariants enforced at compile time by the Regent compiler
program order. The arguments to tasks, and the privileges can be checked at runtime in Python. Many (though not all)
requested on those arguments (read, write, etc.) are passed of the important optimizations provided by Regent can also
through a dynamic analysis to compute a dependence graph be provided in Python via dynamic program analysis. We
between tasks that guides the parallel and distributed execution have implemented five of the seven optimizations in [7], and
of the program. Every execution, even when parallel and/or one has been rendered irrelevant by unrelated improvements
distributed, is guaranteed to be consistent with the original in Legion, leaving only one optimization that could not be
sequential ordering of tasks, ruling out by construction a large implemented (requiring manual user annotation of certain tasks).
class of potential parallel and distributed programming bugs This approach leads to task-based programming constructs that
are more flexible (due to the dynamic nature of the checks),   (launching tasks, moving data, profiling, etc.) of the Legion
while maintaining similar levels of expressiveness and brevity programming model. Regent is a high-level, statically typed
in application codes.                                          language that compiles down to the Legion API. The Regent
   There are tradeoffs involved in this approach, particularly compiler statically checks that programs observe the critical
resulting from the use of dynamic analysis to perform program  invariants of Legion, and also simplifies programming by
optimization. Though certain problems can be addressed         automating and optimizing some aspects of the programming
through careful API design, the abstractions are necessarily   model. Finally as noted above, Pygion, the subject of this
leaky to a certain extent. These leaks are not normally visible in
                                                               paper, is a Python interface to the Legion API that, as we will
idiomatic Python code, but can become visible, for example, if see, provides most of the functionality of Regent running in a
the user explicitly checks the types of certain values generated
                                                               standard Python interpreter.
by the API (see Section IV).                                      Writing a parallel program in Legion consists of two
   Though Python code is certainly slower than that produced   interrelated objectives: the user must divide the program
by Regent’s highly-optimized LLVM [9] backend, this does       execution into tasks (to be executed in parallel) and the program
not necessarily impact overall application performance. In     data into regions (to be distributed across the machine).
particular, the control code in a task-based program (i.e., the   Tasks are simply functions, marked by the user as being
part that launches tasks) can run asynchronously from the rest of
                                                               eligible for parallel execution. The body of a task executes
the code, and thus only needs to achieve an average throughput sequentially, but concurrently with other tasks. Tasks can expose
(in tasks per second) that is higher than the rate at which thenested parallelism to the Legion runtime by invoking subtasks.
system can execute those tasks. If the tasks themselves are    Subtasks run asynchronously, but always in a manner consistent
highly-optimized (perhaps because they are written in another  with a sequential execution of the program.
programming language or call an external library), then the       To identify the parallelism in a Legion program, the runtime
overall application performance can still be high.             performs a dynamic analysis over the sequence of tasks to
   We present Pygion, an implementation of Python support      compute a dependence graph. A dependency exists between
for Legion, and evaluate its performance against three well-   two tasks if they would interfere: i.e., when the two tasks
tuned Regent applications on up to 512 nodes of the Piz Daint  access overlapping data, and at least one task has requested
supercomputer [10]. By reusing the existing, high-performance  write privilege on the data. Note that privileges in Legion are
Regent kernels, these implementations are able to achieve high-strict. A task cannot access data unless it has been passed the
performance execution on Piz Daint’s GPUs. For two out of the  data as an argument with the appropriate privilege.
three applications we consider, we show that Pygion achieves      Application data in Legion is stored in regions. Regions
performance parity (within 2% in absolute performance of       can be thought of as being similar to Pandas dataframes [11],
Regent) at all node counts, while a third achieves within 16%. but natively support multi-dimensional indexing. They contain
   This paper makes the following contributions:               fields, each of which stores a value for each point in an index
   • Section II presents a set of high-level Pygion APIs for   space. In Pygion each field is exposed as a separate NumPy [12]
      Legion and discusses how they compare with Regent and    array.
      C++ Legion.                                                 Listing 1 shows a simple SAXPY example program with two
   • Section III describes a strategy for lowering the high-   tasks. Tasks in Pygion are declared via the @task decorator
      level Pygion APIs to the Legion runtime and the dynamic  (lines 1, 5). Privileges are specified via the privileges
      analysis needed to track the necessary programming model keyword as a list with one entry per argument. In this case, the
      invariants.                                              task reads and writes the field y and reads the field x of the
   • Section IV discusses key optimizations provided by the    first argument s (line 1). The actual computation is performed
      Regent compiler and their corresponding implementations  on line 3 using NumPy array operations.
      in Pygion. This section also discusses an optimization      Execution starts at the task main (lines 5-10). main defines
      that cannot currently be implemented in Pygion due       a region with 10 elements and two fields x and y (line 7),
      to intractability of the necessary dynamic analysis, and partitions it into two pieces (line 8), and the calls the saxpy
      potential strategies for implementing them in the future.task on each piece (lines 9-10).
   • Section V evaluates the performance and scalability of       Data parallelism is achieved in Legion by partitioning regions
      Pygion against reference implementations in Regent on    into subregions. Subregions are views onto the memory of the
      up to 512 nodes of the Piz Daint supercomputer.          original parent regions. Partitions in Legion are very expressive
   Section VI discusses related work, and Section VII con-     and may subdivide regions into arbitrary subsets of elements,
cludes.                                                        including overlapping, or aliased, subsets. Legion provides a
                                                               number of partitioning operators that help users define partitions
           II. P YGION P ROGRAMMING I NTERFACE                 concisely [13]. For example, the equal operator divides a
   In this section we describe the design of Pygion, a high- region into roughly equal subregions (line 8).
level, Python-based interface for Legion. For the purposes        The Legion programming model permits multiple partitions
of this and the following sections, Legion refers to a runtime of the same region (e.g., to express different access patterns)
system implemented as a C++ API that provides all the services as well as replication of data across the memory hierarchy. It
1 @task(privileges=[RW(’y’) + R(’x’)])                                   1 enum FIELD_IDS {
2 def saxpy(S, a):                                                       2   FID_X,
3   S.y += a * S.x                                                       3   FID_Y,
4                                                                        4 };
5  @task                                                                 5
6  def main():                                                           6 enum TASK_IDS {
 7   S = Region([10], {’x’: float32, ’y’: float32})                      7   TID_SAXPY,
 8   P = Partition.equal(S, [2])                                         8   TID_MAIN,
 9   for i in IndexLaunch([2]):                                          9 };
10     saxpy(P[i], 1.23)                                                10
                                                                        11 void saxpy(const Task *task,
                     Listing 1. SAXPY example in Python.                12         const std::vector<PhysicalRegion> &regions,
                                                                        13         Context ctx, Runtime *runtime) {
1 struct fields {                                                       14   FieldAccessor<READ_WRITE,float,1> acc_y(
2   x : float,                                                          15     regions[0], FID_Y);
3   y : float,                                                          16   FieldAccessor<READ_WRITE,float,1> acc_x(
4 }                                                                     17     regions[1], FID_X);
5                                                                       18   float a = *(const float*)(task->args);
6  task saxpy(S : region(fields), a : float)                            19
7  where reads writes(S.y), reads(S.x) do                               20       Rect<1> rect =
 8   for i in S do                                                      21         runtime->get_index_space_domain(
 9     S[i].y += a * S[i].x                                             22           ctx, task->regions[0].region.get_index_space());
10   end                                                                23
11 end                                                                  24       for (PointInRectIterator<1> i(rect); i(); i++) {
12                                                                      25         acc_y[*i] += + a * acc_x[*i];
13 task main()                                                          26       }
14   var S = region(ispace(ptr, 10), fields)                            27   }
15   var P = partition(equal, S, 2)                                     28
16   for i = 0, 2 do                                                    29 void main(const Task *task,
17     saxpy(P[i], 1.23)                                                30        const std::vector<PhysicalRegion> &regions,
18   end                                                                31        Context ctx, Runtime *runtime) {
19 end                                                                  32   IndexSpace I =
                                                                        33     runtime->create_index_space(ctx, Rect<1>(0, 9));
                     Listing 2. SAXPY example in Regent.                34
                                                                        35       FieldSpace F =
                                                                        36         runtime->create_field_space(ctx);
     does so by allowing multiple instances of regions or subregions 37          FieldAllocator allocator =
                                                                         38        runtime->create_field_allocator(ctx, F);
     (physical copies of a region’s data in memory) and manages 39               allocator.allocate_field(sizeof(float), FID_X);
     the coherence of the data in these instances based on which 40              allocator.allocate_field(sizeof(float), FID_Y);
     partition a task uses to access the region. Note that regions are 4142   LogicalRegion S =
     allocated lazily, so that for example the region S at line 7 need 43        runtime->create_logical_region(ctx, I, F);
     not be allocated immediately in any particular node’s memory. 44
                                                                         45   IndexSpace colors =
     (In fact, for S, this means the region need never be allocated at 46        runtime->create_index_space(ctx, Rect<1>(0, 1));
     all in its entirety, since it is only accessed via its subregions.) 47
     These mechanisms are largely invisible to the application, as 4849 IndexPartition             IP =
                                                                                 runtime->create_equal_partition(ctx, I, colors);
     the exact mapping from regions to instances is managed by 50 LogicalPartition P =
     Pygion (see Sections III-B and IV-C).                               51      runtime->get_logical_partition(ctx, S, IP);
                                                                         52
        For comparison with the Pygion code in Listing 1, Listings 2 53 float a = 1.23;
     and 3 show the same example code written in Regent and C++ 54 IndexLauncher launch(
                                                                         55      TID_SAXPY, colors,
     Legion, respectively. The Regent code in Listing 2 is mostly 56             TaskArgument((void *)&a, sizeof(a)),
     comparable to Pygion, and differences in line counts are mostly 57          ArgumentMap());
     due to differences in syntax and formatting. The C++ code in 59     58   launch.add_region_requirement(RegionRequirement(
                                                                                   P, 0, READ_WRITE, EXCLUSIVE, S));
     Listing 3 on the other hand is not only substantially longer, 60 launch.add_region_requirement(RegionRequirement(
     but also exposes more low-level details of the Legion runtime 61              P, 0, READ_ONLY, EXCLUSIVE, S));
                                                                         62   launch.add_field(0, FID_Y);
     system. Users of Legion in C++ must explicitly manage the 63 launch.add_field(1, FID_X);
     IDs associated with fields (lines 1-4) and tasks (lines 6-9), 64 runtime->execute_index_space(ctx, launch);
     must manually manage the creation of index sets (lines 32-33) 65 }
     and fields (lines 35-40) associated with regions, must manually                          Listing 3. SAXPY example in C++.
     set up (and as necessary serialize) the arguments to tasks (lines
     53-64), must manually register tasks (not shown), and so on.
        More fundamentally, the mapping between regions and                   Finally, for efficient execution by the Legion runtime, certain
     instances must be manually managed in C++. Tasks that wish optimizations must be applied to the code. One of these
     to obtain access to the memory associated with an instance optimizations, index launch optimization, is used to improve the
     must manually construct an accessor to do so (lines 14-17). scalability of launching tasks across many nodes by providing
     Accessors are automatically managed by Pygion and Regent a concise representation of a set of tasks to be executed. This
     as described in Section III-B.                                         optimization has been manually applied to the C++ code (lines
53-64), but is automatically (or nearly automatically) applied in      When passing subregions to a subtask, the list of privileges
Pygion and Regent. This and other optimizations are discussed       associated with each region is cleared (inside of the subtask)
in more detail in Section IV.                                       and replaced with the privileges associated with the subtask
   Although for this particular example the Pygion and Regent       itself. The region tree is serialized and passed with the
code samples look quite similar, Pygion has some advantages         arguments so that the relationships between regions can be
over Regent, particularly in terms of flexibility. Regions and      identified. (The Python pickle module is used for serialization,
partitions are first-class values: both can be stored in data       which preserves object identity within a set of objects if they
structures, passed to and returned from tasks, etc. Privileges      are serialized at the same time.) For efficiency and to avoid
are not first-class: they follow a strict stack discipline where    passing unneeded context, the region tree is truncated at the
a task can access only regions it has created itself, or ones       least common ancestor among all the subregions of a given
passed as arguments (and where privileges have been declared        region for which the subtask has requested privileges.
on those arguments). To make sure that region accesses are             Regions can be passed to subtasks inside of data structures
safe (i.e., consistent with the declared privileges) and that all   as long as any that require privileges are also named explicitly
calls to the Legion API are well-formed, Pygion and Regent          as separate arguments. For efficiency, Pygion does not attempt
must track the subregion relationships between regions and          to recursively scan data structures for regions, but relies on
the privileges that apply to them. In Regent, these checks          pickle to preserve object identity among a set of serialized
must necessarily be performed statically (and must therefore        objects to ensure that the regions match up correctly. This is
be conservative). When the Regent type system cannot verify         a capability for which limited support is available in Regent,
that an access is safe it must reject it at compile time, which     due to the need to track regions at the type system level.
makes it challenging or impossible to construct certain forms          If a subtask creates a new region, it can return that region to
of data structures. By using a dynamic analysis Pygion is           the caller, and the caller will inherit the privileges along with
able to provide more flexibility while preserving the same          the region. Pygion correctly tracks the ownership of created
degree of safety; the tradeoff, of course, is that errors are       regions, including when returned out of a subtask. Pygion
reported at runtime instead of at compile time. The tracking        also correctly tracks the region tree if a subregion is returned
of relationships between regions and privileges is discussed in     (or a data structure that contains a region and zero or more
Section III.                                                        subregions of that region).
            III. L OWERING P YGION TO L EGION                       B. Accessors
   Pygion, like Regent, provides a higher-level interface than       Region instances can be organized according to any of a
what is supported by the Legion runtime itself. This interface wide variety of data layouts: C or Fortran array order, struct-
must be lowered to the Legion runtime to execute the program. of-arrays or array-of-structs, or complex hybrid layouts (e.g.,
This section describes the steps taken to lower Pygion APIs to optimized for vectorization or tiling). To ensure that access to
Legion and the salient details of the implementation.             instances is efficient, Legion exposes instances as a separate
                                                                  type from regions (PhysicalRegion in C++, see line 12
A. Tracking Regions and Privileges                                of Listing 3) and requires the user to use a templated class
   As described in Section II, the subregion relationships FieldAccessor to access them (lines 14-17).
between regions, and privileges that apply to those regions,         Pygion manages this transparently on behalf of the user.
must be tracked to ensure that region accesses are safe and Fields of a region are exposed as NumPy arrays (via asarray
that Legion API calls are well-formed.                            to avoid copying), and the mapping of regions to instances is
   This tracking is relatively straightforward within the body managed automatically. NumPy natively provides support for a
of a task: Pygion maintains a list of privileges for each region variety of data layouts, avoiding the need for specialized code
as well as a region tree (i.e., a tree formed by the parent-child that is visible to the user.
relationships between regions and subregions). On an attempt
to access the contents of a subregion, it is necessary to check C. Calling Convention
that a superset of the required privileges are available, either     Legion provides the building blocks for users to construct
for the subregion itself or for some ancestor in the region tree. calls to subtasks however they choose, but the exact details of
Similarly, for a call to a subtask to be well-formed, it must the calling convention are left up to the user. For example, in
identify from which ancestor region it derives privileges, which Listing 3 line 56, the pass-by-value argument a is serialized
can also be determined from the region tree and privileges simply by packing it into a buffer. Objects with special
for each region. (An example can be seen in Listing 3 on significance to the runtime are passed separately: regions (lines
lines 59 and 61 where S is provided as the 5th argument to 58-63), futures (described in Section IV-B), etc. are passed to
signify that it is the ancestor which holds privileges.) These subtasks by different sets of runtime calls.
dynamic checks are simple but sufficient to capture the precise      Pygion supports two calling conventions: the Regent calling
relationships between regions. In contrast, Regent must perform convention [14], and one native to Pygion. In the Regent
a type-based alias analysis which can lose precision, leading calling convention, arguments are packed into a struct along
to reduced flexibility.                                           with a bitmask which specifies which of the arguments (if
any) are being passed via futures. Additional arrays are            this would impose too high a performance penalty. Thanks to
passed containing the field IDs of any regions contained in         Python’s reference counting implementation, only cycles of
the arguments. Legion runtime objects such as regions are           garbage are at risk of escaping this way; otherwise collection is
represented by handles that are safe to pass between nodes,         entirely deterministic. In our experience, referring to a Legion
but otherwise only plain-old-data types are supported.              object from a reference cycle is not common as Legion objects
   The Pygion native calling convention is substantially more       do not have any user-controlled outgoing references.
flexible. Arguments are serialized via pickle. In practice,            Values that escape have the ownership bit set on serialization,
pickle is a universal standard in Python, so nearly any kind        so that the caller task takes ownership of the value (once it is
of data structure can be encoded. pickle maintains object           deserialized). In contrast, values serialized in all other cases
identity within a set of serialized objects so that large data      (such as in the arguments to a subtask call) do not have the
structures are passed correctly. Certain runtime objects (such      ownership bit set (so that for example subtasks do not attempt to
as regions) are preprocessed prior to serialization (e.g., to       deallocate values owned by a parent task). Legion automatically
clear the list of existing privileges and to minimize the extent    considers any non-deallocated value to have escaped at the end
of the region tree which must be serialized). For large data        of a task, so this is a good match for Legion’s semantics, and
structures passed repeatedly, serialization time can be amortized   it is substantially more flexible than Regent, which must do
by storing the data structure in a future and passing this future   any escape analysis statically at compile time.
to each task.                                                          Note that Legion tracks objects such as regions and futures
   As noted in [14], the grouping of fields into region re-         passed to subtasks, so it is not necessary to track these
quirements impacts the performance of the dynamic analysis          references in Pygion. If the parent task completes without
employed by the Legion runtime. For this purpose Pygion             allowing these values to escape, Pygion will instruct Legion to
uses the same grouping algorithm as Regent to ensure optimal        deallocate them, but the deallocation will be deferred by the
packing of fields into region requirements.                         runtime until the corresponding subtasks have completed.
D. Automatic Memory Management                                                           IV. O PTIMIZATIONS
   Python provides automatic memory management via refer-              One potential concern in developing a Python interface for
ence counting, combined with a garbage collector designed task-based programming is that a naive lowering of high-level
to detect and break cycles of garbage values. This memory constructs to the lower-level runtime interface is known to
management strategy becomes somewhat more complicated be far from optimal [7]. We show that most of Regent’s
in the presence of tasks and distributed execution: a value optimizations for task-based programs can be provided in
passed in as an argument to a subtask cannot be freed inside Python using dynamic analysis, in combination with careful
of the subtask even if the subtask no longer has need of it, API design. Out of seven optimizations presented in [7], five can
because the parent task might still be using it. Similarly a be performed automatically or nearly automatically, one cannot
value returned from a subtask is serialized and then (from be performed, and one has been rendered irrelevant by unrelated
the subtask’s perspective) appears to go out of scope, even improvements in the underlying runtime infrastructure. An
though the value itself is actually returned to caller. In both of additional optimization reported in [8] has been replaced with a
these cases, the reference counting scheme in Python cannot dynamic counterpart described in [15]. In this section we briefly
be solely relied upon, because the parent and child tasks may describe the optimizations, their design and implementation in
execute on different nodes of a distributed-memory cluster, and Pygion, and for the one optimization that cannot be performed,
thus the references will necessarily be broken whenever the suggest a way in which it might potentially be implemented
values are serialized.                                              in the future.
   To mitigate this issue and preserve automatic memory
management (i.e., not require manual deletion of Legion A. Index Launches
runtime objects), Pygion augments Python’s reference counting          Index launches are a construct that enable the runtime
with a notion of ownership, along with an escape analysis analysis for a set of N tasks to be performed in O(1)
which determines when a value escapes a task.                       time instead of O(N ) by leveraging a concise, O(1)-space
   A task that allocates a value is considered to own it, and if description of the tasks to be executed. (Note that O(1)-time
the value does not escape, it is deallocated via Python’s normal execution additionally requires the use of control replication
reference counting scheme. All Legion objects are tracked by (Section IV-D); otherwise launches are executed with an
weak references, and at the end of a task, any weak references O(log N ) broadcast tree.) Therefore this is an optimization
that are still valid are considered to escape. This situation can that is critical to the scalable execution of dynamic task-based
occur in one of two ways: either (a) the object is (possibly code.
transitively) referenced from the task’s return value, or (b)          An index launch as understood by the Legion runtime
the object is in a cycle which has not yet been collected by consists of a launch domain, a task (to be instantiated once
the garbage collector. We consider the object to have escaped for each point in the domain), and arguments (pass-by-value,
in both cases; while it would be possible to run the Python regions, futures, etc.). An example of a C++ index launch
garbage collector to catch all cyclic garbage at the end of a task, can be seen in Listing 3 lines 53-64. Region arguments to
1 @task                                                             1 @task
2 def main():                                                       2 def main():
3   S = Region([10], {’x’: float32, ’y’: float32})                  3    S = Region([10], {’x’: float32, ’y’: float32})
4   P = Partition.equal(S, [2])                                     4    T = Region([10], {’x’: float32, ’y’: float32})
5   index_launch([2], saxpy, P[ID], 1.23)                           5    saxpy(S, 1.23)
                                                                    6    saxpy(T, 4.56)
           Listing 4. SAXPY example with constant time launches.    7    print(S.x)
                                                                    8    print(T.x)
                                                                      Listing 5. Example with suboptimal mapping under conservative Legion
    the launch are specified as a projection, or function from a      runtime assumptions which is optimized by Pygion.
    point i in the launch domain to the particular subregion that
    is the argument to the ith task in the launch. In general this
                                                                         Although the differences between futures and concrete values
    can take the form λi.P [f (i)] where f is any function and P
                                                                      can mostly be hidden in idiomatic Pygion code that uses
    is a partition, but by far the most common projection is the
                                                                      duck typing [16], programs that explicitly check the types
    identity λi.P [i]. In lines 59 and 61 the argument 0 specifies
                                                                      of task return values will be able to observe that the values
    the identity projection on the partition argument P.
                                                                      are futures. This is a necessary tradeoff due to the lack of a
       The challenge in developing an index launch optimization for
                                                                      fully static analysis and optimization capability in Pygion. In
    Python is how to capture the projections of region arguments
                                                                      contrast, Regent programs cannot observe whether the future
    for the launch. We achieve this through a combination of careful
                                                                      optimization is enabled or disabled, as the Regent compiler
    API design along with symbolic execution of region expressions.
                                                                      prevents any differences from being visible by the user.
    In Pygion, IndexLaunch is a special iterator which records
    the series of task calls issued while the iterator is active (see C. Mapping
    Listing 1 line 9). The loop variable i is a symbolic value,
                                                                         Region data can be stored in one or more instances as
    which can be coerced to a concrete value, but also can be used
                                                                      described in Section II. Though Legion automatically manages
    with region expressions such as P[i] to generate a projection
                                                                      the coherence of instances, the conservative assumptions made
    expression (line 10). These expressions are understood by
                                                                      by the runtime by default can result in suboptimal performance
    the index launch implementation and generate the appropriate
                                                                      when an application performs a series of repeated task calls.
    Legion calls in the backend.
                                                                         Regions are automatically mapped to instances at the start
       Because Pygion performs this optimization dynamically,
                                                                      of a task, and must be unmapped to avoid data races with
    there are limitations to the impact that it has. In particular,
                                                                      subtasks that have conflicting privileges on the same data. For
    while the optimization successfully reduces runtime analysis
                                                                      example, consider a parent and child task that both have read-
    cost to O(1), the loop must still execute O(N ) times (and
                                                                      write access to a region: sequential semantics requires that
    O(N ) storage is required) because the task arguments are not
                                                                      the parent must unmap the region before the call and then
    generally known to be loop invariant or projections. To reduce
                                                                      subsequently map the region again after the call (blocking
    both the time and space complexity of packing arguments to
                                                                      in the map operation to synchronize on the completion of
    O(1), Pygion provides a second form of index launch, called
                                                                      the subtask), otherwise data races would be possible due to
    constant time launch.
                                                                      concurrent, read-write access to the same data by both the
       This form of index launch can be seen in line 5 of Listing 4. parent and child tasks. By default Legion assumes such races
    In the sample, P[ID] is a symbolic expression representing are possible and automatically inserts the required map and
    the projection λi.P [i] (i.e., ID is the implicit loop variable). unmap calls to force the parent to wait for the completion of
    Arguments are encoded only once, and projections such the child task; but this is suboptimal in the common case where
    as P[ID] are resolved in a post-processing pass over the a task repeatedly launches subtasks without any intervening
    arguments. Because the post-processing pass occurs in parallel accesses to the data.
    (within the spawned tasks themselves), it costs O(N/M ) where        Listing 5 shows an example which is suboptimal under the
    M is the number of processors used to execute the launch, and Legion runtime’s conservative assumptions. By default, Legion
    in practice is effectively constant time.                         inserts map and unmap calls around each task call, causing
                                                                      the main task to block on both lines 5 and 6, even though
    B. Futures
                                                                      these tasks are otherwise non-interfering and the main task
       Subtasks run asynchronously with respect to the caller. does not actually attempt to access the data until lines 7-8.
    To avoid prematurely blocking on the result of a subtask, Thus without further optimization, this program actually does
    which would serialize execution, task calls return futures not achieve parallel execution at all. In C++ the user must
    which represent the yet-to-be-computed results. In Legion C++, manually insert map and unmap calls to avoid this behavior.
    futures are exposed to the user, and must be manually passed For example, if the example in Listing 5 were written in C++,
    through a separate set of runtime APIs to be passed to other the user might choose to unmap both S and T before line 5
    subtasks. In Pygion this is mostly transparent, and futures and map both after line 6. Regent and Pygion automatically
    passed to tasks are automatically added via the appropriate perform this optimization to avoid premature blocking.
    runtime APIs (and deserialized appropriately in argument post-       Pygion automatically optimizes mapping by tracking the
    processing).                                                      liveness of the NumPy arrays that wrap the fields of instances
(again, thanks to Python’s deterministic reference counting          now provides support for co-location constraints on tasks which
implementation and with the same caveats regarding cyclic            require Legion to place the constrained regions into a single
garbage). Mapping and unmapping is performed lazily, at the          instance together, eliminating the need for any dynamic checks.
point where a subtask is launched (if the last data access was
local) or where a local data access is made (if the last operation   F. Optimizations Not Performed
was a subtask). This strategy provides improved precision in            An important optimization in the Legion runtime is the
the case of conditionals, compared to Regent’s flow-sensitive        ability to designate tasks as leaf or inner. Leaf tasks access
analysis which must consider all possible execution paths.           data locally but do not launch subtasks. Inner tasks launch
                                                                     subtasks but do not directly access data. Knowing that a task
D. Optimizations Performed Externally                                is inner means no instances need to be mapped for a task (and
   The following optimizations provided by Regent are also           therefore the task can begin to execute even before the data is
available in Pygion, but are provided directly by the Legion         ready); knowing that a task is leaf means that several important
runtime or another dependency.                                       runtime tests become cheaper because the task cannot launch
   Because the fields of regions in Pygion are exposed as            subtasks.
NumPy arrays, pointer check elision and vectorization are               Regent analyzes the body of each task to automatically
performed by NumPy. In most cases, users who write idiomatic         determine these designations, but Pygion’s use of interpreted
Legion code use bulk NumPy operations, which are generally           Python makes it challenging to apply static analysis to the
amenable to amortizing any necessary checks such as pointer          bodies of tasks (and dynamic analysis is insufficient to
checks. (Pointers are really offsets into arrays in Legion, so       determine these designations, as the best one could do would
pointer checks are subsumed into NumPy’s existing bounds             be to abort the program if the designation were violated).
checks.) Similarly, NumPy provides vectorized implementations           As a workaround, users can manually annotate tasks in
of these bulk operations, making a separate vectorization            Pygion as leaf and/or inner by way of optional keyword
pass unnecessary. For cases where NumPy implementations              arguments to the @task decorator (not shown in the code
might benefit from other optimizations such as loop fusion           samples). The cost of adding this annotation to tasks is low,
and/or tiling, Numba [17] can be used to generate these high-        but it does require users to be familiar with the definitions of
performance implementations. Or Regent itself can be called          leaf and inner to make the correct annotations. (Though note
from Pygion, enabling automatic generation of efficient CPU          that if the user makes a mistake, an error will be reported at
and GPU implementations.                                             runtime and will not be permitted to corrupt the runtime state
   Control replication [8] is an optimization that substantially     of the program.)
improves the scalability of a Legion program by converting              A potential future approach to implementing this optimiza-
the repeated fork-join style parallelism of index launches into      tion could rely on speculation support in the Legion runtime.
efficient, SPMD-style code.                                          Similar to optimistic concurrency schemes, Legion provides
   In normal execution, the main task is executed on one node.       the ability to speculate on what properties a task might have (in
This node can become a scalability bottleneck as the subtasks        this case leaf and/or inner), and to roll back the execution in the
of the main task must be launched from the same node the main        case that the speculated property does not hold. This capability
task is running on (though they may execute on other nodes).         comes at a cost (in particular, additional copies of data must be
Under control replicated execution, the main task is instead         made in memory or on disk to ensure rollback is possible in the
executed on all nodes simultaneously in SPMD fashion. The            event of a missed speculation), but it seems likely that in long-
Legion runtime filters the set of tasks executed by each node        running iterative applications, the speculation would be likely
so that each task is only executed once. The Legion runtime          to converge quickly, reducing the cost of these mechanisms.
also automatically inserts data movement and synchronization         Our experience indicates that tasks do not dynamically switch
to preserve the original sequential semantics of the program. In     between leaf and inner, so this approach is likely to work well.
this way the SPMD nature of the execution is not visible to the
user as long as the main task is deterministic. Therefore control                            V. E VALUATION
replication avoids a sequential bottleneck because the analysis        We present an evaluation of Pygion on up to 512 nodes of
and execution of tasks is distributed across the machine.            the Piz Daint supercomputer [10]. Piz Daint is a Cray XC50
   Control replication was first implemented in the Regent           machine with one Intel Xeon E5-2690 v3 (12 physical cores)
compiler but is now directly implemented in the Legion               and one NVIDIA Tesla P100 per node. We use the system
runtime [15]. In the following experiments we use exclusively        default installations of GCC 6.2.0 and CUDA 9.1.85. Legion
the Legion implementation of this optimization.                      uses GASNet-EX 2019.3.0 as its communication layer [18].
                                                                     Regent uses LLVM 3.8.1 for code generation [9]. Pygion uses
E. Optimizations No Longer Necessary                                 Python 3.7.3, NumPy 1.16.4, and CFFI 1.12.3.
  The dynamic branch elision optimization in Regent, which             We consider three already-optimized Regent applications,
improves the performance of certain access patterns where            and versions of each application where the main task has
data might be located in any of a set of regions, is no longer       been ported to Pygion. The applications include: Stencil, a
necessary in recent versions of the Legion runtime. The runtime      9-point, star-shaped stencil on a grid [19]; Circuit, an electrical
                          12                                                                                100

  points/s)                                                                         zones/s)
                          10                                                                                 80
                           8
                                                                                                             60




  Throughput per Node (                                                             Throughput per Node (
                           6
                                                                                                             40
                           4
                                     Regent                                                                  20           Regent
                           2         Pygion                                                                               Pygion
                                     Pygion CTL                                                                           Pygion CTL
                           0                                                                                  0
                               1     2      4     8                                                                  1    2     4      8   16 32       64 128 256 512
                                                       16 32       64 128 256 512
                                                        Nodes                                                                               Nodes
                                                                                                                  Fig. 3. Pennant weak scaling, 7.4 × 106 zones/node.
                               Fig. 1. Stencil weak scaling, 9 × 108 points/node.


                          5                                    all codes (within 1% in absolute performance). This is not

  wires/s)
                                                               surprising, as the main task executes asynchronously from
      4                                                        the rest of the application, and therefore does not impact
                                                               performance as long as the average throughput (in tasks per
                                                               second launched by the main task) exceeds the rate at which




  Throughput per Node (
      3                                                        the machine can execute them.
                                                                  Pygion CTL achieves weak scaling parallel efficiency of 96%,
      2                                                        94% and 75% respectively for Stencil, Circuit, and Pennant
                                                               (vs. 98%, 94% and 90% for Regent) at 512 nodes. Without
      1          Regent                                        CTL, the scalability of Pygion is limited, as the O(N ) time
                 Pygion                                        complexity of the packing of index launch arguments grows
                 Pygion CTL                                    to dominate execution time at large node counts. This effect is
      0                                                        most visible in Figure 3, as Pennant has the largest number of
           1 2 4 8 16 32 64 128 256 512                        tasks per iteration of the time-step loop (and those tasks are of
                                    Nodes                      relatively small granularity), as well as a global reduction to
            Fig. 2. Circuit weak scaling, 2 × 105 wires/node.  compute dt for the next time step (which prevents the Legion
                                                               runtime from analyzing tasks more than one iteration ahead of
                                                               the actual execution of the program).
circuit simulation on an unstructured graph [8]; and Pennant,     Although the asymptotic factors are important, constant
a Lagrangian hydrodynamics simulation on a 2D unstructured factors also matter. Notably, Regent does not use constant time
mesh [20]. In order to maintain as much of an apples-to- launches, and so also incurs O(N ) time complexity in the
apples comparison as possible, we reuse the original Regent packing of arguments, but with a constant factor that is so
implementations of the tasks in each application (aside from much smaller that it is not an issue up to 512 nodes. The
the main task); this allows us to make use of Regent’s high- reduction in asymptotic complexity is much more important
performance CUDA code generator to target the GPUs on Piz for Pygion because the constant factors on packing arguments
Daint.                                                         are so much higher.
   To demonstrate the scalability of Pygion, we conduct weak      For two of the three application (Stencil and Circuit), Py-
scaling experiments on Piz Daint up to 512 nodes. The results gion’s scalable execution with CTL ensures that the applications
are presented in Figures 1, 2 and 3. For each application, achieve performance parity across all node counts (within 2%
we consider three versions: Regent (the baseline), Pygion, in absolute performance). Pennant begins to drop at 128 nodes,
and Pygion with constant time launches (CTL). Each data and achieves within 16% of Regent’s performance at 512 nodes.
point in the graphs is the average of 5 runs. We use the At the time of writing, we are currently investigating the cause
following problem sizes: 9×108 points/node for Stencil, 2×105 of the Pennant performance degradation.
wires/node for Circuit, and 7.4 × 106 zones/node for Pennant.
The applications have been configured to run 50, 50, and 30                          VI. R ELATED W ORK
time steps, respectively.                                         Among the existing task-based programming systems for
   Thanks to the use of the existing high-performance kernels, high-performance computing, by far the most common lan-
Pygion achieves performance parity at small node counts for guages used for programming are C and C++. Legion [3],
PaRSEC (with dynamic task discovery) [4], and StarPU [5] domain-specific assumptions, and therefore are not applicable
support distributed-memory, while OpenMP (as of version 4.0) outside of the chosen domain.
[21], OmpSs [22] and Kokkos [23] run on shared-memory                   In contrast to the implicitly parallel systems above, certain
systems. These systems share a number of common features: task-based runtimes provide explicitly parallel program seman-
tasks appear to execute in program order, dependencies between tics. In OCR [30] and Realm [31], the DAG of tasks is explicitly
tasks are determined by the arguments supplied to task calls specified by the user, instead of being inferred via a static or
along with the privileges requested by tasks, and tasks can be dynamic analysis of the arguments to tasks. These systems are
offloaded to available GPUs (with data movement managed typically intended to be used by library and framework authors
by the system). Among these systems, Legion is the only one rather than directly by end-users, as the code to construct DAGs
that provides support for partitioning [13]; the others require of tasks can be verbose and error-prone.
users to explicitly reorganize data in applications that use            Others systems aim to directly improve the usability of
multiple access patterns. However, in general the use of C/C++ explicit parallelism. These include partitioned global address
represents a significant barrier for scientists not already familiar space (PGAS) languages Chapel [32], Fortran coarrays [33],
with traditional HPC programming models and languages.               Titanium [34], UPC [35], and X10 [36]. Although the details
   PyCOMPSs [24] and Dask [25] provide support for task- vary, the common elements include the ability to hold references
based programming in Python. Like Pygion, the use of Python to (and possibly directly access) the contents of memory on
in these systems improves usability for scientists not already remote machines and in many cases the ability to launch tasks
familiar with lower-level programming languages such as to execute locally or remotely. Alternatively, actor models such
C/C++. However, these systems lack features of Legion, such as as Charm++ [37] ensure that no such remote reference are held,
control replication, without which performance and scalability and instead data movement and synchronization occurs via
can be limited [15]. As with most of the systems above, message passing between objects. However, as these systems
PyCOMPSs and Dask also lack support for partitioning.                are explicitly parallel they typically do not prevent all of the
   An alternative approach explored in PaRSEC (with param- possible pitfalls that can occur with parallel programming.
eterized task graphs) [26] is to provide a domain-specific              At the other extreme, Legate [15] and Dask [25] provide sup-
language (DSL) which can generate task graphs automatically. port for running unmodified or minimally-edited NumPy [12]
In this approach a DSL compiler reads a program representation programs on distributed machines. Though NumPy itself
(in the case of PaRSEC, a recursive, algebraic description of a is entirely sequential, these approaches work because most
task graph) and generates code to execute the tasks described NumPy operations work in bulk, over an entire array, and
in the program. These approaches can improve usability within can often be executed lazily (and therefore asynchronously).
a domain, as long as the target programs are well supported Internally, Legate is based on Legion, whereas Dask builds
by the domain-specific semantics.                                    on its own task-based programming model. These approaches
   On the other hand, some languages focus on more general- are appealing because they minimize the amount of work
purpose support for task-based programming. This is the required to understand the programming model, but they rely
case for Regent [7], a language which directly targets the on heuristics that may not provide optimal performance for
Legion programming model. Regent provides a model which any given problem. In cases where the heuristics fail, the user
is higher-level than the Legion C++ interface, and the Regent may be forced to turn to other programming models that more
compiler translates programs into efficient code for the Legion directly support the parallelism required.
runtime. The Regent type system is also richer than C++, and
directly tracks various program properties to ensure correct                                VII. C ONCLUSION
usage of the model [6]. However these type restrictions also
limit the flexibility of the Regent language and make certain           A growing population of users in the physical sciences and
programming patterns difficult.                                      data analysis require supercomputers to process the ever larger
   The Sequoia language [27] for array-based programs offers data sets in these disciplines, but are unfamiliar with traditional
a form of task-based parallelism where tasks are automatically, high-performance programming models and languages. To meet
recursively decomposed for optimized execution on deep the needs of these users, we have presented Pygion, a Python-
memory hierarchies. Various optimizations in the Sequoia based interface for the Legion task-based programming system.
compiler ensure very high performance [28]. However, the By leveraging the flexibility and the dynamic nature of the
compiler requires intimate knowledge of the program, including Python programming language, we have been able to implement
the sizes of all input arrays and the exact configuration of the an interface with expressiveness which is comparable to Regent,
target machine, to be available at compile time in order to a dedicated language for the Legion programming model. For
apply these optimizations. This approach makes it impractical five out of seven optimizations presented in [7], we have
to apply to more dynamic problems.                                   shown that dynamic program analysis in Pygion is sufficient to
   Domain-specific programming frameworks such as Uin- support automatic or nearly automatic optimization in Pygion,
tah [29] provide support for constructing directed acyclic graphs one optimization is no longer necessary, and only one necessary
(DAGs) of tasks that can be executed asynchronously. Such optimization is intractable under this approach and requires
models can provide improved programmability by applying manual user annotation of tasks.
   With constant time launches, Pygion is able to achieve weak                 [13] S. Treichler, M. Bauer, R. Sharma, E. Slaughter, and A. Aiken,
scalability that is comparable to already-optimized Regent                           “Dependent partitioning,” in Object-Oriented Programming, Systems,
                                                                                     Languages, and Applications (OOPSLA). ACM, 2016, pp. 344–358.
GPU implementations on up to 512 nodes of the Piz Daint                        [14] E. Slaughter, “Regent: A high-productivity programming language for
supercomputer. By reusing the original task implementations                          implicit parallelism with logical regions,” Ph.D. dissertation, Stanford
from the Regent code (except for the main task), Pygion is                           University, 2017.
able to target Piz Daint’s GPUs with minimal additional effort                 [15] M. Bauer and M. Garland, “Legate: Accelerated and distributed NumPy,”
                                                                                     in Supercomputing (SC), 2019.
and with high performance.
                                                                               [16] “Duck typing,” https://docs.python.org/3/glossary.html#term-duck-typing.
   Overall, these results point in a promising direction: contrary             [17] “Numba,” https://numba.pydata.org/, 2012.
to what one might expect, Python is fast enough to be useful for               [18] D. Bonachea and P. H. Hargrove, “GASNet-EX: A high-performance,
writing the main tasks in non-trivial mini-apps relevant to high-                    portable communication library for exascale,” Lawrence Berkeley
performance scientific simulation. The additional flexibility                        National Laboratory, Tech. Rep. LBNL-2001174, October 2018,
                                                                                     languages and Compilers for Parallel Computing (LCPC’18). [Online].
afforded by the use of dynamic program analysis, and the                             Available: https://escholarship.org/uc/item/0xg7b704
streamlined interface, have the potential to make this a much                  [19] R. F. Van der Wijngaart and T. G. Mattson, “The Parallel Research
more productive interface for writing task-based programs on                         Kernels,” in HPEC, 2014, pp. 1–6.
modern heterogeneous supercomputers, especially for a large                    [20] C. R. Ferenbaugh, “PENNANT: an unstructured mesh mini-app for
                                                                                     advanced architecture research,” Concurrency and Computation: Practice
class of scientific users who are not familiar with traditional                      and Experience, 2014.
programming models and languages.                                              [21] “OpenMP application program interface,” http://www.openmp.org/
                                                                                     wp-content/uploads/OpenMP4.0.0.pdf, 2013.
                          ACKNOWLEDGMENT                                       [22] A. Duran, E. Ayguadé, R. M. Badia, J. Labarta, L. Martinell, X. Martorell,
                                                                                     and J. Planas, “Ompss: A proposal for programming heterogeneous
   This material is based upon work supported by the Exascale                        multi-core architectures,” Parallel Processing Letters, vol. 21, no. 02, pp.
Computing Project (17-SC-20-SC), a collaborative effort of the                       173–193, 2011.
U.S. Department of Energy Office of Science and the National [23] H. C. Edwards and C. R. Trott, “Kokkos: Enabling performance portability
                                                                                     across manycore architectures,” in Extreme Scaling Workshop (XSW),
Nuclear Security Administration, and by a grant from the                             2013, Aug 2013, pp. 18–24.
Swiss National Supercomputing Centre (CSCS) under project [24] E. Tejedor, Y. Becerra, G. Alomar, A. Queralt, R. M. Badia, J. Torres,
ID d80.                                                                              T. Cortes, and J. Labarta, “PyCOMPSs: Parallel computational workflows
                                                                                     in Python,” The International Journal of High Performance Computing
                                                                                     Applications, vol. 31, no. 1, pp. 66–82, 2017.
                                R EFERENCES
                                                                               [25] M. Rocklin, “Dask: Parallel computation with blocked algorithms and
 [1] “Linac coherent light source,” https://lcls.slac.stanford.edu/, 2009.           task scheduling,” in Python in Science Conference (SciPy), no. 130-136.
 [2] “Slac, berkeley lab researchers prepare for scientific computing                Citeseer, 2015.
     on        the      exascale,”        https://www6.slac.stanford.edu/news/ [26] G. Bosilca, A. Bouteiller, A. Danalis, M. Faverge, T. Hérault, and J. J.
     2016-11-03-slac-berkeley-lab-researchers-prepare-scientific-computing-exascale. Dongarra, “PaRSEC: Exploiting heterogeneity to enhance scalability,”
     aspx, 2016.                                                                     Computing in Science & Engineering, vol. 15, no. 6, pp. 36–45, 2013.
 [3] M. Bauer, S. Treichler, E. Slaughter, and A. Aiken, “Legion: Expressing   [27] K. Fatahalian, D. R. Horn, T. J. Knight, L. Leem, M. Houston, J. Y. Park,
     locality and independence with logical regions,” in Supercomputing (SC),        M. Erez, M. Ren, A. Aiken, W. J. Dally, and P. Hanrahan, “Sequoia:
     2012.                                                                           Programming the memory hierarchy,” in SC, November 2006.
 [4] R. Hoque, T. Herault, G. Bosilca, and J. Dongarra, “Dynamic task [28] T. J. Knight, J. Y. Park, M. Ren, M. Houston, M. Erez, K. Fatahalian,
     discovery in parsec: A data-flow task-based runtime,” in Proceedings of         A. Aiken, W. J. Dally, and P. Hanrahan, “Compilation for explicitly
     the 8th Workshop on Latest Advances in Scalable Algorithms for Large-           managed memory hierarchies,” in Principles and Practice of Parallel
     Scale Systems, ser. ScalA ’17. New York, NY, USA: ACM, 2017, pp. 6:1–           Programming (PPoPP), 2007, pp. 226–236.
     6:8. [Online]. Available: http://doi.acm.org/10.1145/3148226.3148233
                                                                               [29] Q. Meng, A. Humphrey, J. Schmidt, and M. Berzins, “Investigating
 [5] E. Agullo, O. Aumage, M. Faverge, N. Furmento, F. Pruvost, M. Sergent,          applications portability with the Uintah DAG-based runtime system on
     and S. Thibault, “Achieving high performance on supercomputers with a           petascale supercomputers,” in Supercomputing (SC), 2013, pp. 1–12.
     sequential task-based programming model,” Inria, Tech. Rep., 2016.
 [6] S. Treichler, M. Bauer, and A. Aiken, “Language support for dynamic, [30] “The Open Community Runtime interface,” https://xstack.exascale-tech.
     hierarchical data partitioning,” in Object Oriented Programming, Systems,       com/git/public?p=ocr.git;a=blob;f=ocr/spec/ocr-1.1.0.pdf, 2014.
     Languages, and Applications (OOPSLA), 2013.                               [31] S. Treichler, M. Bauer, and A. Aiken, “Realm: An event-based low-level
 [7] E. Slaughter, W. Lee, S. Treichler, M. Bauer, and A. Aiken, “Regent: A          runtime for distributed memory architectures,” in Parallel Architectures
     high-productivity programming language for HPC with logical regions,”           and Compilation Techniques (PACT), 2014.
     in Supercomputing (SC), 2015.                                             [32] B. L. Chamberlain, “Chapel,” in Programming Models for Parallel
 [8] E. Slaughter, W. Lee, S. Treichler, W. Zhang, M. Bauer, G. Shipman,             Computing, P. Balaji, Ed. MIT Press, 2015, pp. 129–159.
     P. McCormick, and A. Aiken, “Control Replication: Compiling implicit      [33] “Fortran 2008,” https://wg5-fortran.org/f2008.html, 2008.
     parallelism to efficient SPMD with logical regions,” in Supercomputing
                                                                               [34] K. Yelick, L. Semenzato, G. Pike, C. Miyamoto, B. Liblit, A. Krishna-
     (SC), 2017.
                                                                                     murthy, P. Hilfinger, S. Graham, D. Gay, and P. Colella, “Titanium: A
 [9] C. Lattner and V. Adve, “LLVM: A compilation framework for lifelong             high-performance Java dialect,” Concurrency Practice and Experience,
     program analysis & transformation,” in Code Generation and Optimiza-            vol. 10, no. 11-13, pp. 825–836, 1998.
     tion (CGO), 2004.
[10] “Piz Daint & Piz Dora - CSCS,” http://www.cscs.ch/computers/piz daint, [35] W. Carlson, J. Draper, D. Culler, K. Yelick, E. Brooks, and K. Warren,
     2016.                                                                           “Introduction to UPC and language specification,” UC Berkeley Technical
[11] W. McKinney, “Data structures for statistical computing in Python,” in          Report: CCS-TR-99-157, 1999.
     Proceedings of the 9th Python in Science Conference, S. van der Walt      [36]  P. Charles, C. Grothoff, V. Saraswat, C. Donawa, A. Kielstra, K. Ebcioglu,
     and J. Millman, Eds., 2010, pp. 51 – 56.                                        C. Von Praun, and V. Sarkar, “X10: An object-oriented approach to non-
[12] S. Van Der Walt, S. C. Colbert, and G. Varoquaux, “The NumPy array:             uniform cluster computing,” in OOPSLA, 2005.
     A structure for efficient numerical computation,” Computing in Science [37] L. V. Kalé and S. Krishnan, “CHARM++: A portable concurrent object
     & Engineering, vol. 13, no. 2, p. 22, 2011.                                     oriented system based on C++,” in OOPSLA, 1993, pp. 91–108.
                          A PPENDIX A                                    SLURM_JOB_NAME=bash
                                                                         PE_HDF5_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH
                    A RTIFACT D ESCRIPTION                               XALT_ETC_DIR=/apps/daint/UES/xalt/0.7.6/etc
                                                                         PE_TRILINOS_DEFAULT_GENCOMPS_CRAY_x86_64=86
Summary of the Experiments Reported                                      PE_TPSL_64_DEFAULT_GENCOMPS_INTEL_interlagos=160
                                                                         PE_PETSC_DEFAULT_GENCOMPILERS_INTEL_mic_knl=16.0
   We perform weak scaling experiments on up to 512 nodes of             PE_LIBSCI_ACC_DEFAULT_PKGCONFIG_VARIABLES=
                                                                               PE_LIBSCI_ACC_DEFAULT_NV_SUFFIX_@accelerator@
the Piz Daint supercomputer [10]. For reproducibility, the exact         PE_FFTW_DEFAULT_TARGET_mic_knl=mic_knl
                                                                         CRAY_UDREG_INCLUDE_OPTS=-I/opt/cray/udreg/2.3.2-6.0.7.1_5.13
version of Legion used in the experiments has been saved in a                  __g5196236.ari/include
                                                                         PE_TRILINOS_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/trilinos
branch, along with all scripts used to build and run. Instructions             /12.12.1.0/@PRGENV@/@PE_TRILINOS_DEFAULT_GENCOMPS@/
                                                                               @PE_TRILINOS_DEFAULT_TARGET@/lib/pkgconfig
for building and running are included in the links below.                PE_SMA_DEFAULT_COMPFLAG_GNU=-fcray-pointer
                                                                         PE_PARALLEL_NETCDF_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/
Artifact Availability                                                          parallel-netcdf/1.8.1.3/@PRGENV@/
                                                                               @PE_PARALLEL_NETCDF_DEFAULT_GENCOMPS@/lib/pkgconfig
                                                                         PE_NETCDF_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/netcdf
      Software Artifact Availability: All author-created software              /4.6.1.2/@PRGENV@/@PE_NETCDF_DEFAULT_GENCOMPS@/lib/pkgconfig
artifacts are maintained in a public repository under an OSI-            LIBRARYMODULES=acml:alps:cray-dwarf:cray-fftw:cray-ga:cray-hdf5:cray-
                                                                               hdf5-parallel:cray-libsci:cray-libsci_acc:cray-mpich:cray-mpich2
approved license.                                                              :cray-mpich-abi:cray-netcdf:cray-netcdf-hdf5parallel:cray-
                                                                               parallel-netcdf:cray-petsc:cray-petsc-complex:cray-shmem:cray-
      Hardware Artifact Availability: There are no author-                     tpsl:cray-trilinos:cudatoolkit:fftw:ga:hdf5:hdf5-parallel:iobuf:
                                                                               libfast:netcdf:netcdf-hdf5parallel:ntk:onesided:papi:petsc:petsc
created hardware artifacts.                                                    -complex:pmi:tpsl:trilinos:xt-libsci:xt-mpich2:xt-mpt:xt-papi
                                                                         CRAY_SITE_LIST_DIR=/etc/opt/cray/pe/modules
      Data Artifact Availability: There are no author-created            XKEYSYMDB=/usr/X11R6/lib/X11/XKeysymDB
                                                                         PE_TPSL_64_DEFAULT_GENCOMPILERS_CRAY_x86_64=8.6
data artifacts.                                                          PE_SMA_DEFAULT_COMPFLAG=
      Proprietary Artifacts: None of the associated artifacts,           PE_MPICH_ALTERNATE_LIBS_dpm=_dpm
                                                                         PE_HDF5_DEFAULT_GENCOMPILERS_GNU=7.1 6.1 5.3 4.9
author-created or otherwise, are proprietary.                            PE_ENV=GNU
                                                                         SLURM_NODE_ALIASES=(null)
      List of URLs and/or DOIs where artifacts are available:            PKGCONFIG_ENABLED=1
                                                                         PE_TPSL_DEFAULT_GENCOMPS_CRAY_x86_skylake=86
Project repository: https://github.com/StanfordLegion/legion/            HOST=daint105
                                                                         TERM=xterm-256color
tree/papers/pygion-paw19                                                 SHELL=/usr/local/bin/bash
   Instructions: https://github.com/StanfordLegion/legion/blob/          PE_TPSL_DEFAULT_GENCOMPILERS_GNU_x86_skylake=7.1 6.1
                                                                         PE_PETSC_DEFAULT_GENCOMPS_CRAY_sandybridge=86
papers/pygion-paw19/language/paw19 scripts/README.md                     PROFILEREAD=true
                                                                         HISTSIZE=
                                                                         SLURM_JOB_QOS=normal
Baseline Experimental Setup, and Modifications Made for the              PE_TRILINOS_DEFAULT_VOLATILE_PRGENV=CRAY GNU INTEL
                                                                         PE_TPSL_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH:PE_LIBSCI
Paper                                                                    PE_TPSL_DEFAULT_GENCOMPS_GNU_sandybridge=71 53 49
                                                                         PE_TPSL_64_DEFAULT_GENCOMPS_INTEL_x86_skylake=160
     Relevant Hardware Details: Piz Daint (Cray XC50, Intel              PE_PETSC_DEFAULT_GENCOMPS_INTEL_haswell=160
                                                                         PE_PETSC_DEFAULT_GENCOMPS_GNU_haswell=71 53 49
Xeon E5-2690 v3, NVIDIA Tesla P100, Aries interconnect)                  PE_PARALLEL_NETCDF_DEFAULT_VOLATILE_PRGENV=GNU
                                                                         PE_NETCDF_DEFAULT_VOLATILE_PRGENV=GNU
     Operating Systems and Versions: CNL based on SLES                   CRAY_XPMEM_POST_LINK_OPTS=-L/opt/cray/xpmem/2.2.15-6.0.7.1_5.11
12 SP3 running Linux kernel 4.4.162                                            __g7549d06.ari/lib64
                                                                         CRAY_UGNI_POST_LINK_OPTS=-L/opt/cray/ugni/6.0.14.0-6.0.7.1_3.13
     Compilers and Versions: GCC 6.2.0, CUDA 9.1.85,                           __gea11d3d.ari/lib64
                                                                         CRAYPE_DIR=/opt/cray/pe/craype/2.5.15
LLVM 3.8.1 (Regent only), Python 3.7.3 (Legion Python only)              SLURM_CSCS=yes
                                                                         PE_MPICH_DIR_PGI_DEFAULT64=64
     Applications and Versions: All benchmarks are included              PE_PETSC_DEFAULT_GENCOMPS_CRAY_interlagos=86
                                                                         PE_NETCDF_HDF5PARALLEL_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/
in the Legion repository                                                       netcdf-hdf5parallel/4.6.1.2/@PRGENV@/
     Libraries and Versions: NumPy 1.16.4, CFFI 1.12.3                         @PE_NETCDF_HDF5PARALLEL_DEFAULT_GENCOMPS@/lib/pkgconfig
                                                                         PE_HDF5_PARALLEL_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/hdf5-
     Key Algorithms: N/A                                                       parallel/1.10.2.0/@PRGENV@/@PE_HDF5_PARALLEL_DEFAULT_GENCOMPS@/
                                                                               lib/pkgconfig
     Input Datasets and Versions: N/A                                    PE_HDF5_DEFAULT_VOLATILE_PRGENV=GNU
                                                                         PE_FFTW_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/fftw/3.3.6.5/
     Paper Modifications: N/A                                                  @PE_FFTW_DEFAULT_TARGET@/lib/pkgconfig
                                                                         ALT_LINKER=/apps/daint/UES/xalt/0.7.6/bin/ld
     Output from scripts that gathers execution environment              CRAY_MPICH2_DIR=/opt/cray/pe/mpt/7.7.2/gni/mpich-gnu/7.1
information:                                                             PERL5LIB=/opt/slurm/17.11.12.cscs//lib/perl5/site_perl/5.18.2/x86_64-
                                                                               linux-thread-multi:/opt/slurm/default/lib/perl5/site_perl
CRAY_CUDATOOLKIT_VERSION=9.1.85_3.18-6.0.7.0_5.1__g2eb7c52                     /5.18.2/x86_64-linux-thread-multi:
PE_TPSL_64_DEFAULT_GENCOMPS_INTEL_mic_knl=160                            CRAY_CUDATOOLKIT_POST_LINK_OPTS=-L/opt/nvidia/cudatoolkit9.1/9.1.85_3
PE_SMA_DEFAULT_PKGCONFIG_VARIABLES=PE_SMA_COMPFLAG_@prgenv@                    .18-6.0.7.0_5.1__g2eb7c52/lib64 -L/opt/nvidia/cudatoolkit9
PE_LIBSCI_VOLATILE_PRGENV=CRAY GNU INTEL                                       .1/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52/extras/CUPTI/lib64 -Wl,--as
KSH_AUTOLOAD=1                                                                 -needed -Wl,-lcupti -Wl,-lcudart -Wl,--no-as-needed -L/opt/cray/
MODULE_VERSION_STACK=3.2.10.6                                                  nvidia/default/lib64 -lcuda
LESSKEY=/etc/lesskey.bin                                                 PE_TPSL_DEFAULT_GENCOMPS_CRAY_mic_knl=86
PE_TPSL_DEFAULT_GENCOMPS_INTEL_x86_skylake=160                           PE_TPSL_64_DEFAULT_GENCOMPILERS_CRAY_interlagos=8.6
PE_PETSC_DEFAULT_GENCOMPS_CRAY_skylake=86                                PE_LIBSCI_DEFAULT_GENCOMPS_GNU_x86_64=71 61 51 49
PE_PETSC_DEFAULT_GENCOMPILERS_CRAY_sandybridge=8.6                       PE_GA_DEFAULT_VOLATILE_PRGENV=GNU
PE_PAPI_DEFAULT_ACCEL_FAMILY_LIBS_nvidia=,-lcupti,-lcudart,-lcuda        PE_TPSL_DEFAULT_GENCOMPS_INTEL_x86_64=160
GNU_VERSION=6.2.0                                                        PE_MPICH_DEFAULT_GENCOMPILERS_GNU=7.1 5.1 4.9
PE_MPICH_GENCOMPILERS_PGI=15.3                                           PE_LIBSCI_ACC_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH:PE_LIBSCI
PE_CXX_PKGCONFIG_LIBS=mpichcxx                                           PE_LIBSCI_ACC_DEFAULT_GENCOMPS_CRAY_x86_64=85
NNTPSERVER=news                                                          PERFTOOLS_VERSION=7.0.3
MANPATH=/opt/nvidia/cudatoolkit9.1/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52/    PE_MPICH_GENCOMPS_GNU=71 51 49
      doc/man:/opt/cray/pe/perftools/7.0.3/man:/opt/cray/pe/papi         PE_PKGCONFIG_PRODUCTS=PE_LIBSCI:PE_MPICH
      /5.6.0.3/share/pdoc/man:/opt/cray/pe/atp/2.1.2/man:/opt/cray/      FPATH=:/opt/cray/pe/modules/3.2.10.6/init/sh_funcs/no_redirect:/opt/
      alps/6.6.43-6.0.7.1_5.45__ga796da32.ari/man:/opt/cray/job                cray/pe/modules/3.2.10.6/init/sh_funcs/no_redirect
      /2.2.3-6.0.7.1_5.43__g6c4e934.ari/man:/opt/cray/pe/pmi/5.0.14/     MORE=-sl
      man:/opt/cray/pe/libsci/18.07.1/man:/opt/cray/pe/man/csmlversion   PE_TPSL_64_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/tpsl/18.06.1/
      :/opt/cray/pe/craype/2.5.15/man:/opt/gcc/6.2.0/snos/share/man:/          @PRGENV@64/@PE_TPSL_64_DEFAULT_GENCOMPS@/
      opt/slurm/17.11.12.cscs/share/man:/opt/cray/pe/mpt/7.7.2/gni/man         @PE_TPSL_64_DEFAULT_TARGET@/lib/pkgconfig
      /mpich:/opt/cray/pe/modules/3.2.10.6/share/man:/opt/slurm/         PE_TPSL_64_DEFAULT_GENCOMPS_CRAY_haswell=86
      default/share/man:/usr/local/man:/usr/share/man:/opt/cray/share/   PE_PETSC_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH:PE_LIBSCI:
      man:/opt/cray/pe/man                                                     PE_HDF5_PARALLEL:PE_TPSL
PE_PAPI_DEFAULT_ACCEL_LIBS_nvidia35=,-lcupti,-lcudart,-lcuda             PE_LIBSCI_GENCOMPS_INTEL_x86_64=160
PE_TRILINOS_DEFAULT_GENCOMPILERS_CRAY_x86_64=8.6                         PE_LIBSCI_DEFAULT_GENCOMPILERS_INTEL_x86_64=16.0
PE_CRAY_DEFAULT_FIXED_PKGCONFIG_PATH=/opt/cray/pe/parallel-netcdf        OFFLOAD_INIT=on_start
      /1.8.1.3/CRAY/8.6/lib/pkgconfig:/opt/cray/pe/netcdf-hdf5parallel   GCC_VERSION=6.2.0
      /4.6.1.2/CRAY/8.6/lib/pkgconfig:/opt/cray/pe/netcdf/4.6.1.2/CRAY   CHPL_CG_CPP_LINES=1
      /8.6/lib/pkgconfig:/opt/cray/pe/hdf5-parallel/1.10.2.0/CRAY/8.6/   PE_PRODUCT_LIST=CRAY_RCA:CRAY_ALPS:DVS:CRAY_XPMEM:CRAY_DMAPP:CRAY_PMI
      lib/pkgconfig:/opt/cray/pe/hdf5/1.10.2.0/CRAY/8.6/lib/pkgconfig          :CRAY_UGNI:CRAY_UDREG:CRAY_LIBSCI:CRAYPE:CRAYPE_HASWELL:GNU:GCC:
      :/opt/cray/pe/ga/5.3.0.8/CRAY/8.6/lib/pkgconfig                          PERFTOOLS:CRAYPAT
PE_TPSL_64_DEFAULT_GENCOMPILERS_CRAY_sandybridge=8.6                     FROM_HEADER=
PE_PETSC_DEFAULT_GENCOMPS_CRAY_x86_64=86                                 APPS=/apps/daint
PE_LIBSCI_DEFAULT_OMP_REQUIRES_openmp=_mp                                PE_TPSL_DEFAULT_GENCOMPS_GNU_x86_skylake=71 61
PE_FORTRAN_PKGCONFIG_LIBS=mpichf90                                       PE_PETSC_DEFAULT_GENCOMPILERS_GNU_x86_64=7.1 5.3 4.9
SLURM_SPANK_SHIFTER_GID=31707                                            PE_MPICH_DEFAULT_GENCOMPS_PGI=153
PE_SMA_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/mpt/7.7.2/gni/       CRAY_MPICH_ROOTDIR=/opt/cray/pe/mpt/7.7.2
      sma@PE_SMA_DEFAULT_DIR_DEFAULT64@/lib64/pkgconfig                  PAGER=less
CRAYPAT_LD_LIBRARY_PATH=/opt/cray/pe/gcc-libs:/opt/cray/gcc-libs:/opt    PE_TPSL_64_DEFAULT_GENCOMPILERS_INTEL_x86_64=16.0
      /cray/pe/perftools/7.0.3/lib64                                     PE_PETSC_DEFAULT_GENCOMPS_INTEL_skylake=160
CRAYPAT_ALPS_COMPONENT=/opt/cray/pe/perftools/7.0.3/sbin/pat_alps        PE_PETSC_DEFAULT_GENCOMPS_GNU_skylake=61
ALLINEA_QUEUE_DLL=/opt/cray/pe/mpt/7.7.2/gni/mpich-gnu/7.1/lib/          PE_LIBSCI_GENCOMPILERS_GNU_x86_64=7.1 6.1 5.1 4.9
      libtvmpich.so.3.0.1                                                PE_MPICH_MODULE_NAME=cray-mpich
PE_TRILINOS_DEFAULT_GENCOMPS_INTEL_x86_64=160                            PE_MPICH_GENCOMPILERS_CRAY=8.6
PE_LIBSCI_ACC_DEFAULT_VOLATILE_PRGENV=CRAY GNU                           CSHEDIT=emacs
CRAY_MPICH_BASEDIR=/opt/cray/pe/mpt/7.7.2/gni                            PE_TPSL_DEFAULT_GENCOMPS_CRAY_sandybridge=86
PE_TPSL_64_DEFAULT_GENCOMPS_INTEL_haswell=160                            PE_TPSL_DEFAULT_GENCOMPS_CRAY_haswell=86
PE_TPSL_64_DEFAULT_GENCOMPS_CRAY_x86_skylake=86                          PE_TPSL_64_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH:PE_LIBSCI
PE_NETCDF_HDF5PARALLEL_DEFAULT_GENCOMPILERS_GNU=7.1 6.1 5.3 4.9          PE_MPICH_TARGET_VAR_nvidia20=-lcudart
PE_HDF5_PARALLEL_DEFAULT_GENCOMPILERS_GNU=7.1 6.1 5.3 4.9                PE_MPICH_DEFAULT_VOLATILE_PRGENV=CRAY GNU PGI
HISTFILESIZE=                                                            PE_LIBSCI_GENCOMPS_CRAY_x86_64=86
JRE_HOME=/usr/lib64/jvm/java/jre                                         PE_LIBSCI_DEFAULT_GENCOMPILERS_CRAY_x86_64=8.6
SLURM_NNODES=1                                                           CRAYPAT_ROOT=/opt/cray/pe/perftools/7.0.3
CRAYPE_LINK_TYPE=dynamic                                                 XDG_CONFIG_DIRS=/etc/xdg
PE_TRILINOS_DEFAULT_GENCOMPILERS_INTEL_x86_64=160                        PE_TPSL_64_DEFAULT_GENCOMPS_GNU_x86_64=71 53 49
PE_TRILINOS_DEFAULT_GENCOMPILERS_GNU_x86_64=71 53 49                     PE_TPSL_64_DEFAULT_GENCOMPS_GNU_mic_knl=71 53
PE_TPSL_DEFAULT_GENCOMPS_CRAY_x86_64=86                                  PE_PARALLEL_NETCDF_DEFAULT_GENCOMPS_GNU=51 49
PE_TPSL_64_DEFAULT_GENCOMPILERS_INTEL_mic_knl=16.0                       PE_NETCDF_DEFAULT_GENCOMPS_GNU=
PE_PETSC_DEFAULT_GENCOMPILERS_INTEL_interlagos=16.0                      PE_LIBSCI_PKGCONFIG_LIBS=libsci_mpi:libsci
PE_LIBSCI_DEFAULT_VOLATILE_PRGENV=CRAY GNU INTEL                         PE_LIBSCI_ACC_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/libsci_acc
PE_FFTW_DEFAULT_TARGET_interlagos=interlagos                                   /18.07.1/@PRGENV@/@PE_LIBSCI_ACC_DEFAULT_GENCOMPS@/
LD_LIBRARY_PATH=/opt/cray/pe/papi/5.6.0.3/lib64:/opt/cray/job                  @PE_LIBSCI_ACC_DEFAULT_TARGET@/lib/pkgconfig
      /2.2.3-6.0.7.1_5.43__g6c4e934.ari/lib64:/opt/gcc/6.2.0/snos/       DVS_VERSION=0.9.0
      lib64                                                              CRAY_LIBSCI_DIR=/opt/cray/pe/libsci/18.07.1
LS_COLORS=no=00:fi=00:di=01;34:ln=00;36:pi=40;33:so=01;35:do=01;35:bd    CRAY_LIBSCI_BASE_DIR=/opt/cray/pe/libsci/18.07.1
      =40;33;01:cd=40;33;01:or=41;33;01:ex=00;32:*.cmd=00;32:*.exe       CRAY_DMAPP_INCLUDE_OPTS=-I/opt/cray/dmapp/7.1.1-6.0.7.1_5.45
      =01;32:*.com=01;32:*.bat=01;32:*.btm=01;32:*.dll=01;32:*.tar             __g5a674e0.ari/include -I/opt/cray/gni-headers/5.0.12.0-6.0.7.1
      =00;31:*.tbz=00;31:*.tgz=00;31:*.rpm=00;31:*.deb=00;31:*.arj             _3.11__g3b1768f.ari/include
      =00;31:*.taz=00;31:*.lzh=00;31:*.lzma=00;31:*.zip=00;31:*.zoo      USERMODULES=acml:alps:apprentice:apprentice2:atp:blcr:cce:chapel:cray
      =00;31:*.z=00;31:*.Z=00;31:*.gz=00;31:*.bz2=00;31:*.tb2=00;31:*.         -ccdb:cray-fftw:cray-ga:cray-hdf5:cray-hdf5-parallel:cray-lgdb:
      tz2=00;31:*.tbz2=00;31:*.xz=00;31:*.avi=01;35:*.bmp=01;35:*.fli          cray-libsci:cray-libsci_acc:cray-mpich:cray-mpich2:cray-mpich-
      =01;35:*.gif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mng=01;35:*.mov            compat:cray-netcdf:cray-netcdf-hdf5parallel:cray-parallel-netcdf
      =01;35:*.mpg=01;35:*.pcx=01;35:*.pbm=01;35:*.pgm=01;35:*.png             :craypat:craype:cray-petsc:cray-petsc-complex:craypkg-gen:cray-
      =01;35:*.ppm=01;35:*.tga=01;35:*.tif=01;35:*.xbm=01;35:*.xpm             shmem:cray-snplauncher:cray-tpsl:cray-trilinos:cudatoolkit:ddt:
      =01;35:*.dl=01;35:*.gl=01;35:*.wmv=01;35:*.aiff=00;32:*.au               fftw:ga:gcc:hdf5:hdf5-parallel:intel:iobuf:java:lgdb:libfast:
      =00;32:*.mid=00;32:*.mp3=00;32:*.ogg=00;32:*.voc=00;32:*.wav             libsci_acc:mpich1:netcdf:netcdf-hdf5parallel:netcdf-nofsync:
      =00;32:                                                                  netcdf-nofsync-hdf5parallel:ntk:onesided:papi:parallel-netcdf:
SLURM_LOG_ACTIONS=yes                                                          pathscale:perftools:perftools-lite:petsc:petsc-complex:pgi:pmi:
PE_TPSL_64_DEFAULT_GENCOMPILERS_INTEL_haswell=16.0                             PrgEnv-cray:PrgEnv-gnu:PrgEnv-intel:PrgEnv-pathscale:PrgEnv-pgi:
PE_TPSL_64_DEFAULT_GENCOMPILERS_GNU_sandybridge=7.1 5.3 4.9                    stat:totalview:tpsl:trilinos:xt-asyncpe:xt-craypat:xt-lgdb:xt-
PE_PETSC_DEFAULT_VOLATILE_PRGENV=CRAY CRAY64 GNU GNU64 INTEL INTEL64           libsci:xt-mpich2:xt-mpt:xt-papi:xt-shmem:xt-totalview
PE_LIBSCI_PKGCONFIG_VARIABLES=PE_LIBSCI_OMP_REQUIRES_@openmp@:           LIBGL_DEBUG=quiet
      PE_SCI_EXT_LIBPATH:PE_SCI_EXT_LIBNAME                              MINICOM=-c on
CRAY_RCA_POST_LINK_OPTS=-L/opt/cray/rca/2.2.18-6.0.7.1_5.47__g2aa4f39    PE_TPSL_DEFAULT_GENCOMPS_CRAY_interlagos=86
      .ari/lib64 -lrca                                                   PE_TPSL_DEFAULT_GENCOMPILERS_GNU_x86_64=7.1 5.3 4.9
PE_MPICH_FIXED_PRGENV=INTEL                                              PE_PKGCONFIG_DEFAULT_PRODUCTS=PE_TRILINOS:PE_TPSL_64:PE_TPSL:PE_PETSC
PE_PKGCONFIG_LIBS=cray-cudatoolkit:AtpSigHandler:cray-rca:libsci_mpi:          :PE_PARALLEL_NETCDF:PE_NETCDF_HDF5PARALLEL:PE_NETCDF:PE_MPICH:
      libsci:mpich                                                             PE_LIBSCI_ACC:PE_LIBSCI:PE_HDF5_PARALLEL:PE_HDF5:PE_GA:PE_FFTW
SINFO_FORMAT=%9P %5a %8s %.10l %.6c %.6z %.7D %10T %N                    PE_HDF5_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/hdf5/1.10.2.0/
PE_TPSL_DEFAULT_GENCOMPS_GNU_haswell=71 53 49                                  @PRGENV@/@PE_HDF5_DEFAULT_GENCOMPS@/lib/pkgconfig
PE_PETSC_DEFAULT_GENCOMPS_INTEL_sandybridge=160                          PAT_REPORT_PRUNE_NAME=_cray$mt_execute_,_cray$mt_start_,__cray_hwpc_,
PE_PETSC_DEFAULT_GENCOMPS_INTEL_interlagos=160                                 f_cray_hwpc_,cstart,__pat_,pat_region_,PAT_,OMP.slave_loop,
PE_PETSC_DEFAULT_GENCOMPS_GNU_sandybridge=71 53 49                             slave_entry,_new_slave_entry,_thread_pool_slave_entry,
PE_PETSC_DEFAULT_GENCOMPS_GNU_interlagos=71 53 49                              THREAD_POOL_join,__libc_start_main,_start,__start,start_thread,
PE_PETSC_DEFAULT_GENCOMPILERS_INTEL_skylake=16.0                               __wrap_,UPC_ADIO_,_upc_,upc_,__caf_,__pgas_,syscall,
PE_PETSC_DEFAULT_GENCOMPILERS_CRAY_x86_64=8.6                                  __device_stub
PE_PETSC_DEFAULT_GENCOMPILERS_CRAY_mic_knl=8.6                           PE_MPICH_GENCOMPILERS_GNU=7.1 5.1 4.9
XNLSPATH=/usr/share/X11/nls                                              MODULE_VERSION=3.2.10.6
PE_TPSL_64_DEFAULT_GENCOMPS_INTEL_sandybridge=160                        SLURM_TASKS_PER_NODE=24
PE_TPSL_64_DEFAULT_GENCOMPILERS_GNU_interlagos=7.1 5.3 4.9               PE_TPSL_DEFAULT_GENCOMPILERS_GNU_haswell=7.1 5.3 4.9
PE_PETSC_DEFAULT_GENCOMPS_INTEL_mic_knl=160                              PE_TPSL_64_DEFAULT_GENCOMPILERS_GNU_x86_skylake=7.1 6.1
PE_PETSC_DEFAULT_GENCOMPS_GNU_mic_knl=53                                 PE_PETSC_DEFAULT_GENCOMPS_CRAY_mic_knl=86
PE_PETSC_DEFAULT_GENCOMPILERS_CRAY_haswell=8.6                           PE_PARALLEL_NETCDF_DEFAULT_GENCOMPILERS_GNU=5.1 4.9
PE_PAPI_DEFAULT_PKGCONFIG_VARIABLES=PE_PAPI_ACCEL_LIBS_@accelerator@     PE_NETCDF_DEFAULT_GENCOMPILERS_GNU=7.1 6.1 5.3 4.9
PE_LIBSCI_DEFAULT_GENCOMPS_CRAY_x86_64=86                                PE_MPICH_DEFAULT_DIR_PGI_DEFAULT64=64
MPICH_ABORT_ON_ERROR=1                                                   PE_FFTW_DEFAULT_TARGET_abudhabi=abudhabi
MPICH_DIR=/opt/cray/pe/mpt/7.7.2/gni/mpich-gnu/7.1                       ATP_IGNORE_SIGTERM=1
PE_TPSL_64_DEFAULT_GENCOMPILERS_CRAY_haswell=8.6                         XTPE_NETWORK_TARGET=aries
PE_PETSC_DEFAULT_GENCOMPILERS_INTEL_sandybridge=16.0                     CSCS_CUSTOM_ENV=true
PE_NETCDF_HDF5PARALLEL_DEFAULT_REQUIRED_PRODUCTS=PE_HDF5_PARALLEL        CPU=x86_64
PE_HDF5_PARALLEL_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH                      _=/usr/bin/env
PE_FFTW_DEFAULT_TARGET_sandybridge=sandybridge                           PE_TPSL_64_DEFAULT_GENCOMPILERS_CRAY_x86_skylake=8.6
PE_FFTW_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH                               PE_SMA_DEFAULT_DIR_CRAY_DEFAULT64=64
CRAY_PRGENVGNU=loaded                                                    PE_NETCDF_HDF5PARALLEL_DEFAULT_GENCOMPS_GNU=
ATP_POST_LINK_OPTS=-Wl,-L/opt/cray/pe/atp/2.1.2/libApp/                  PE_NETCDF_HDF5PARALLEL_DEFAULT_FIXED_PRGENV=CRAY PGI INTEL
PE_MPICH_FORTRAN_PKGCONFIG_LIBS=mpichf90                                 PE_HDF5_PARALLEL_DEFAULT_GENCOMPS_GNU=
HOSTTYPE=x86_64                                                          PE_HDF5_PARALLEL_DEFAULT_FIXED_PRGENV=CRAY PGI INTEL
PE_PETSC_DEFAULT_GENCOMPILERS_GNU_mic_knl=5.3                            SQUEUE_SORT=-t,e,S
RCLOCAL_PRGENV=true                                                      JAVA_BINDIR=/usr/lib64/jvm/java/bin
TMOUT=259200                                                             SLURM_JOB_ID=14250172
gcc_already_loaded=0                                                     PE_TPSL_DEFAULT_GENCOMPS_INTEL_interlagos=160
PE_TPSL_DEFAULT_GENCOMPS_GNU_interlagos=71 53 49                         PE_TPSL_DEFAULT_GENCOMPILERS_CRAY_mic_knl=8.6
PE_TPSL_DEFAULT_GENCOMPILERS_CRAY_x86_64=8.6
PE_TPSL_64_DEFAULT_VOLATILE_PRGENV=CRAY CRAY64 GNU GNU64 INTEL           PE_TPSL_DEFAULT_GENCOMPILERS_CRAY_x86_skylake=8.6
      INTEL64                                                            PE_PETSC_DEFAULT_GENCOMPILERS_GNU_skylake=6.1
PE_TPSL_64_DEFAULT_GENCOMPS_CRAY_sandybridge=86                          PE_LIBSCI_OMP_REQUIRES_openmp=_mp
CRAY_UDREG_POST_LINK_OPTS=-L/opt/cray/udreg/2.3.2-6.0.7.1_5.13           PAT_BUILD_PAPI_BASEDIR=/opt/cray/pe/papi/5.6.0.3
      __g5196236.ari/lib64                                               CRAY_RCA_INCLUDE_OPTS=-I/opt/cray/rca/2.2.18-6.0.7.1_5.47__g2aa4f39.
PE_TPSL_DEFAULT_GENCOMPS_GNU_mic_knl=71 53                                     ari/include -I/opt/cray/krca/2.2.4-6.0.7.1_5.43__g8505b97.ari/
CRAY_ALPS_POST_LINK_OPTS=-L/opt/cray/alps/6.6.43-6.0.7.1_5.45                  include -I/opt/cray-hss-devel/8.0.0/include
      __ga796da32.ari/lib64                                              PE_TPSL_DEFAULT_GENCOMPILERS_INTEL_x86_64=16.0
CRAYPE_VERSION=2.5.15                                                    PE_TPSL_64_DEFAULT_GENCOMPS_CRAY_mic_knl=86
PE_MPICH_VOLATILE_PRGENV=CRAY GNU PGI                                    PE_MPICH_CXX_PKGCONFIG_LIBS=mpichcxx
PE_TPSL_DEFAULT_GENCOMPILERS_INTEL_haswell=16.0                          CRAY_MPICH_DIR=/opt/cray/pe/mpt/7.7.2/gni/mpich-gnu/7.1
PE_PETSC_DEFAULT_GENCOMPILERS_GNU_sandybridge=7.1 5.3 4.9                PE_MPICH_PKGCONFIG_VARIABLES=PE_MPICH_NV_LIBS_@accelerator@:
PE_MPICH_DEFAULT_GENCOMPS_CRAY=86                                              PE_MPICH_ALTERNATE_LIBS_@multithreaded@:
PE_LIBSCI_DEFAULT_OMP_REQUIRES=                                                PE_MPICH_ALTERNATE_LIBS_@dpm@
XALT_TRANSMISSION_STYLE=directdb                                         PE_LIBSCI_DEFAULT_GENCOMPS_INTEL_x86_64=160
_LMFILES_=/opt/cray/pe/modulefiles/modules/3.2.10.6:/opt/cray/pe/        PE_LIBSCI_ACC_DEFAULT_GENCOMPILERS_GNU_x86_64=4.9
      modulefiles/cray-mpich/7.7.2:/opt/modulefiles/slurm/17.11.12.      SQUEUE_FORMAT=%.8i %.8u %.7a %.14j %.3t %9r %19S %.10M %.10L %.5D %.4
      cscs-1:/apps/daint/UES/easybuild/modulefiles/xalt/daint                  C
      -2016.11:/apps/daint/UES/easybuild/modulefiles/daint-gpu:/opt/     CXX=CC
      modulefiles/gcc/6.2.0:/opt/cray/pe/craype/2.5.15/modulefiles/      PE_TPSL_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/tpsl/18.06.1/
      craype-haswell:/opt/cray/pe/craype/2.5.15/modulefiles/craype-            @PRGENV@/@PE_TPSL_DEFAULT_GENCOMPS@/@PE_TPSL_DEFAULT_TARGET@/lib
      network-aries:/opt/cray/pe/modulefiles/craype/2.5.15:/opt/cray/          /pkgconfig
      pe/modulefiles/cray-libsci/18.07.1:/opt/cray/ari/modulefiles/      PE_TPSL_DEFAULT_GENCOMPILERS_INTEL_x86_skylake=16.0
      udreg/2.3.2-6.0.7.1_5.13__g5196236.ari:/opt/cray/ari/modulefiles   PE_TPSL_64_DEFAULT_GENCOMPILERS_CRAY_mic_knl=8.6
      /ugni/6.0.14.0-6.0.7.1_3.13__gea11d3d.ari:/opt/cray/pe/            PE_HDF5_DEFAULT_FIXED_PRGENV=CRAY PGI INTEL
      modulefiles/pmi/5.0.14:/opt/cray/ari/modulefiles/dmapp             CRAY_PMI_POST_LINK_OPTS=-L/opt/cray/pe/pmi/5.0.14/lib64
      /7.1.1-6.0.7.1_5.45__g5a674e0.ari:/opt/cray/ari/modulefiles/gni-   APP2_STATE=7.0.3
      headers/5.0.12.0-6.0.7.1_3.11__g3b1768f.ari:/opt/cray/ari/         PE_MPICH_PKGCONFIG_LIBS=mpich
      modulefiles/xpmem/2.2.15-6.0.7.1_5.11__g7549d06.ari:/opt/cray/     CRAY_MPICH2_VER=7.7.2
      ari/modulefiles/job/2.2.3-6.0.7.1_5.43__g6c4e934.ari:/opt/cray/    HISTCONTROL=erasedups:ignorespace
      ari/modulefiles/dvs/2.7_2.2.118-6.0.7.1_10.2__g58b37a2:/opt/cray   PE_PARALLEL_NETCDF_DEFAULT_FIXED_PRGENV=CRAY PGI INTEL
      /ari/modulefiles/alps/6.6.43-6.0.7.1_5.45__ga796da32.ari:/opt/     PE_NETCDF_DEFAULT_FIXED_PRGENV=CRAY PGI INTEL
      cray/ari/modulefiles/rca/2.2.18-6.0.7.1_5.47__g2aa4f39.ari:/opt/   PE_MPICH_ALTERNATE_LIBS_multithreaded=_mt
      cray/pe/modulefiles/atp/2.1.2:/opt/cray/pe/modulefiles/perftools   PE_LIBSCI_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/libsci/18.07.1/
      -base/7.0.3:/opt/cray/pe/modulefiles/PrgEnv-gnu/6.0.4:/opt/cray/         @PRGENV@/@PE_LIBSCI_GENCOMPS@/@PE_LIBSCI_TARGET@/lib/pkgconfig
      modulefiles/cudatoolkit/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52          PE_LIBSCI_ACC_DEFAULT_GENCOMPS_GNU_x86_64=49
TARGETMODULES=craype-abudhabi:craype-abudhabi-cu:craype-accel-host:      PE_GA_DEFAULT_GENCOMPILERS_GNU=5.3 4.9
      craype-accel-nvidia20:craype-accel-nvidia30:craype-accel-          CUDATOOLKIT_HOME=/opt/nvidia/cudatoolkit9.1/9.1.85_3.18-6.0.7.0_5.1
      nvidia35:craype-barcelona:craype-broadwell:craype-haswell:craype         __g2eb7c52
      -hugepages128K:craype-hugepages128M:craype-hugepages16M:craype-    PE_TPSL_64_DEFAULT_GENCOMPS_GNU_haswell=71 53 49
      hugepages256M:craype-hugepages2M:craype-hugepages32M:craype-       PE_PKGCONFIG_PRODUCTS_DEFAULT=PE_PAPI
      hugepages4M:craype-hugepages512K:craype-hugepages512M:craype-      PE_NETCDF_HDF5PARALLEL_DEFAULT_VOLATILE_PRGENV=GNU
      hugepages64M:craype-hugepages8M:craype-intel-knc:craype-           PE_MPICH_TARGET_VAR_nvidia35=-lcudart
      interlagos:craype-interlagos-cu:craype-istanbul:craype-ivybridge   PE_HDF5_PARALLEL_DEFAULT_VOLATILE_PRGENV=GNU
      :craype-mc12:craype-mc8:craype-mic-knl:craype-network-aries:       CRAY_LIBSCI_VERSION=18.07.1
      craype-network-gemini:craype-network-infiniband:craype-network-    QT_SYSTEM_DIR=/usr/share/desktop-data
      none:craype-network-seastar:craype-sandybridge:craype-shanghai:    JDK_HOME=/usr/lib64/jvm/java
      craype-target-compute_node:craype-target-local_host:craype-        SHLVL=3
      target-native:craype-xeon:xtpe-barcelona:xtpe-interlagos:xtpe-     PE_TPSL_DEFAULT_GENCOMPILERS_INTEL_interlagos=16.0
      interlagos-cu:xtpe-istanbul:xtpe-mc12:xtpe-mc8:xtpe-network-       LESS_ADVANCED_PREPROCESSOR=no
      gemini:xtpe-network-seastar:xtpe-shanghai:xtpe-target-native:      OSTYPE=linux
      xtpe-xeon                                                          PE_TPSL_DEFAULT_VOLATILE_PRGENV=CRAY CRAY64 GNU GNU64 INTEL INTEL64
JAVA_HOME=/usr/lib64/jvm/java                                            PE_PETSC_DEFAULT_GENCOMPILERS_CRAY_interlagos=8.6
PE_TPSL_DEFAULT_GENCOMPILERS_GNU_mic_knl=7.1 5.3                         PE_MPICH_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/mpt/7.7.2/gni/
PE_TPSL_DEFAULT_GENCOMPILERS_CRAY_interlagos=8.6                               mpich-@PRGENV@@PE_MPICH_DEFAULT_DIR_DEFAULT64@/
PE_PETSC_DEFAULT_GENCOMPILERS_CRAY_skylake=8.6                                 @PE_MPICH_DEFAULT_GENCOMPS@/lib/pkgconfig
PE_LIBSCI_MODULE_NAME=cray-libsci/18.07.1                                PE_LIBSCI_ACC_DEFAULT_NV_SUFFIX_nvidia60=nv60
PE_LIBSCI_ACC_DEFAULT_NV_SUFFIX_nvidia20=nv20                            PE_TPSL_DEFAULT_GENCOMPS_INTEL_sandybridge=160
EDITOR=emacs --no-window-system                                          PE_TPSL_64_DEFAULT_GENCOMPS_CRAY_interlagos=86
PE_TPSL_64_DEFAULT_GENCOMPS_GNU_x86_skylake=71 61                        CRAY_PMI_INCLUDE_OPTS=-I/opt/cray/pe/pmi/5.0.14/include
PE_INTEL_FIXED_PKGCONFIG_PATH=/opt/cray/pe/mpt/7.7.2/gni/mpich-intel     LS_OPTIONS=-N --color=none -T 0
      /16.0/lib/pkgconfig                                                XCURSOR_THEME=DMZ
LANG=en_US.UTF-8                                                         SLURM_JOB_CPUS_PER_NODE=24
PE_MPICH_NV_LIBS_nvidia20=-lcudart                                       SLURM_CLUSTER_NAME=daint
PE_LIBSCI_GENCOMPILERS_CRAY_x86_64=8.6                                   CRAY_CUDATOOLKIT_INCLUDE_OPTS=-I/opt/nvidia/cudatoolkit9.1/9.1.85_3
PE_MPICH_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/mpt/7.7.2/gni/mpich-             .18-6.0.7.0_5.1__g2eb7c52/include -I/opt/nvidia/cudatoolkit9
      @PRGENV@@PE_MPICH_DIR_DEFAULT64@/@PE_MPICH_GENCOMPS@/lib/                .1/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52/extras/CUPTI/include -I/opt
      pkgconfig                                                                /nvidia/cudatoolkit9.1/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52/extras/
MODULEPATH=/opt/cray/pe/perftools/7.0.3/modulefiles:/opt/cray/pe/              Debugger/include
      craype/2.5.15/modulefiles:/apps/daint/UES/jenkins/6.0.UP07/gpu/    CRAY_CUDATOOLKIT_DIR=/opt/nvidia/cudatoolkit9.1/9.1.85_3.18-6.0.7.0_5
      easybuild/tools/modules/all:/apps/daint/UES/jenkins/6.0.UP07/gpu         .1__g2eb7c52
      /easybuild/modules/all:/apps/daint/modulefiles:/apps/daint/        PKG_CONFIG_PATH_DEFAULT=/opt/cray/pe/papi/5.6.0.2/lib64/pkgconfig
      system/modulefiles:/apps/daint/UES/easybuild/modulefiles:/apps/    PE_TPSL_DEFAULT_GENCOMPILERS_CRAY_haswell=8.6
      common/UES/modulefiles:/apps/common/system/modulefiles:/opt/cray   GCC_PATH=/opt/gcc/6.2.0
      /pe/modulefiles:/opt/cray/modulefiles:/opt/modulefiles:/opt/cray   ATP_MRNET_COMM_PATH=/opt/cray/pe/atp/2.1.2/libexec/
      /ari/modulefiles:/opt/cray/pe/ari/modulefiles                            atp_mrnet_commnode_wrapper
PYTHONSTARTUP=/etc/pythonstart                                           PE_MPICH_DIR_CRAY_DEFAULT64=64
SHMEM_ABORT_ON_ERROR=1                                                   CRAYPE_NETWORK_TARGET=aries
LOADEDMODULES=modules/3.2.10.6:cray-mpich/7.7.2:slurm/17.11.12.cscs      PRGENVMODULES=PrgEnv-cray:PrgEnv-gnu:PrgEnv-intel:PrgEnv-pathscale:
      -1:xalt/daint-2016.11:daint-gpu:gcc/6.2.0:craype-haswell:craype-         PrgEnv-pgi
      network-aries:craype/2.5.15:cray-libsci/18.07.1:udreg              WINDOWMANAGER=
      /2.3.2-6.0.7.1_5.13__g5196236.ari:ugni/6.0.14.0-6.0.7.1_3.13       PE_TPSL_DEFAULT_GENCOMPILERS_INTEL_sandybridge=16.0
      __gea11d3d.ari:pmi/5.0.14:dmapp/7.1.1-6.0.7.1_5.45__g5a674e0.ari   PE_TPSL_DEFAULT_GENCOMPILERS_GNU_interlagos=7.1 5.3 4.9
      :gni-headers/5.0.12.0-6.0.7.1_3.11__g3b1768f.ari:xpmem             PE_TPSL_64_DEFAULT_GENCOMPILERS_GNU_mic_knl=7.1 5.3
      /2.2.15-6.0.7.1_5.11__g7549d06.ari:job/2.2.3-6.0.7.1_5.43          PE_PETSC_DEFAULT_GENCOMPILERS_GNU_haswell=7.1 5.3 4.9
      __g6c4e934.ari:dvs/2.7_2.2.118-6.0.7.1_10.2__g58b37a2:alps         SLURM_JOB_PARTITION=normal
      /6.6.43-6.0.7.1_5.45__ga796da32.ari:rca/2.2.18-6.0.7.1_5.47        PE_TRILINOS_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH:PE_HDF5_PARALLEL:
      __g2aa4f39.ari:atp/2.1.2:perftools-base/7.0.3:PrgEnv-gnu/6.0.4:          PE_NETCDF_HDF5PARALLEL:PE_LIBSCI:PE_TPSL
      cudatoolkit/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52                      PE_TPSL_DEFAULT_GENCOMPS_GNU_x86_64=71 53 49
TZ=Europe/Zurich                                                         PE_TPSL_64_DEFAULT_GENCOMPILERS_INTEL_sandybridge=16.0
SDK_HOME=/usr/lib64/jvm/java                                             PE_TPSL_64_DEFAULT_GENCOMPILERS_GNU_haswell=7.1 5.3 4.9
PE_TPSL_DEFAULT_GENCOMPILERS_INTEL_mic_knl=16.0                          PE_NETCDF_DEFAULT_REQUIRED_PRODUCTS=PE_HDF5
PE_TPSL_64_DEFAULT_GENCOMPS_GNU_interlagos=71 53 49                      PE_MPICH_NV_LIBS=
PE_PKG_CONFIG_PATH=/opt/cray/pe/cti/1.0.7/lib/pkgconfig:/opt/cray/pe/    PE_HDF5_DEFAULT_GENCOMPS_GNU=
      cti/1.0.6/lib/pkgconfig:/opt/cray/pe/cti/1.0.4/lib/pkgconfig       CRAY_LIBSCI_PREFIX_DIR=/opt/cray/pe/libsci/18.07.1/GNU/6.1/x86_64
PE_FFTW_DEFAULT_TARGET_x86_skylake=x86_skylake                           CRAY_GNI_HEADERS_INCLUDE_OPTS=-I/opt/cray/gni-headers
PE_FFTW_DEFAULT_TARGET_share=share                                             /5.0.12.0-6.0.7.1_3.11__g3b1768f.ari/include
PE_FFTW_DEFAULT_TARGET_ivybridge=ivybridge                               PYTHONPATH=/apps/daint/UES/xalt/0.7.6/site:/apps/daint/UES/xalt
CRAY_DMAPP_POST_LINK_OPTS=-L/opt/cray/dmapp/7.1.1-6.0.7.1_5.45                 /0.7.6/libexec
      __g5a674e0.ari/lib64                                               G_FILENAME_ENCODING=@locale,UTF-8,ISO-8859-15,CP1252
LESS=-M -I -R                                                                  netcdf/4.6.1.2/INTEL/16.0/lib/pkgconfig:/opt/cray/pe/mpt/7.7.2/
MACHTYPE=x86_64-suse-linux                                                     gni/mpich-intel/16.0/lib/pkgconfig:/opt/cray/pe/hdf5-parallel
PE_TRILINOS_DEFAULT_GENCOMPS_GNU_x86_64=71 53 49                               /1.10.2.0/INTEL/16.0/lib/pkgconfig:/opt/cray/pe/hdf5/1.10.2.0/
PE_MPICH_DEFAULT_GENCOMPILERS_CRAY=8.6                                         INTEL/16.0/lib/pkgconfig:/opt/cray/pe/ga/5.3.0.8/INTEL/18.0/lib/
PE_LIBSCI_OMP_REQUIRES=                                                        pkgconfig
DMAPP_ABORT_ON_ERROR=1                                                   PE_GA_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/ga/5.3.0.8/
PE_MPICH_GENCOMPS_CRAY=86                                                      @PRGENV@/@PE_GA_DEFAULT_GENCOMPS@/lib/pkgconfig
PE_TPSL_DEFAULT_GENCOMPILERS_CRAY_sandybridge=8.6                        PE_GA_DEFAULT_GENCOMPS_GNU=53 49
PE_TPSL_64_DEFAULT_GENCOMPILERS_INTEL_interlagos=16.0                    PE_FFTW_DEFAULT_TARGET_haswell=haswell
PE_MPICH_DEFAULT_GENCOMPS_GNU=71 51 49                                   CRAY_LD_LIBRARY_PATH=/opt/nvidia/cudatoolkit9.1/9.1.85_3.18-6.0.7.0_5
PE_MPICH_DEFAULT_FIXED_PRGENV=INTEL                                            .1__g2eb7c52/lib64:/opt/nvidia/cudatoolkit9.1/9.1.85_3
PE_LIBSCI_DEFAULT_REQUIRED_PRODUCTS=PE_MPICH                                   .18-6.0.7.0_5.1__g2eb7c52/extras/CUPTI/lib64:/opt/cray/pe/
PE_LIBSCI_ACC_DEFAULT_NV_SUFFIX_nvidia35=nv35                                  perftools/7.0.3/lib64:/opt/cray/rca/2.2.18-6.0.7.1_5.47
PE_LIBSCI_ACC_DEFAULT_GENCOMPILERS_CRAY_x86_64=8.5                             __g2aa4f39.ari/lib64:/opt/cray/alps/6.6.43-6.0.7.1_5.45
DVS_INCLUDE_OPTS=-I/opt/cray/dvs/2.7_2.2.118-6.0.7.1_10.2__g58b37a2/           __ga796da32.ari/lib64:/opt/cray/xpmem/2.2.15-6.0.7.1_5.11
      include                                                                  __g7549d06.ari/lib64:/opt/cray/dmapp/7.1.1-6.0.7.1_5.45
TOOLMODULES=apprentice:apprentice2:atp:chapel:cray-lgdb:craypat:               __g5a674e0.ari/lib64:/opt/cray/pe/pmi/5.0.14/lib64:/opt/cray/
      craypkg-gen:cray-snplauncher:ddt:gdb:iobuf:papi:perftools:               ugni/6.0.14.0-6.0.7.1_3.13__gea11d3d.ari/lib64:/opt/cray/udreg
      perftools-lite:stat:totalview:xt-craypat:xt-lgdb:xt-papi:xt-             /2.3.2-6.0.7.1_5.13__g5196236.ari/lib64:/opt/cray/pe/libsci
      totalview                                                                /18.07.1/GNU/6.1/x86_64/lib:/opt/cray/pe/mpt/7.7.2/gni/mpich-gnu
XDG_DATA_DIRS=/usr/share                                                       /7.1/lib
PE_TPSL_DEFAULT_GENCOMPILERS_GNU_sandybridge=7.1 5.3 4.9                 G_BROKEN_FILENAMES=1
PE_LIBSCI_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/libsci            SLURM_MEM_PER_NODE=61000
      /18.07.1/@PRGENV@/@PE_LIBSCI_DEFAULT_GENCOMPS@/                    PE_PETSC_DEFAULT_GENCOMPS_INTEL_x86_64=160
      @PE_LIBSCI_DEFAULT_TARGET@/lib/pkgconfig                           PE_PETSC_DEFAULT_GENCOMPS_GNU_x86_64=71 53 49
PE_GA_DEFAULT_FIXED_PRGENV=CRAY PGI INTEL                                PE_PETSC_DEFAULT_GENCOMPS_CRAY_haswell=86
MODULESHOME=/opt/cray/pe/modules/3.2.10.6                                PE_MPICH_DEFAULT_DIR_CRAY_DEFAULT64=64
SLURM_JOB_NUM_NODES=1                                                    JAVA_ROOT=/usr/lib64/jvm/java
PE_PETSC_DEFAULT_VOLATILE_PKGCONFIG_PATH=/opt/cray/pe/petsc/3.8.4.0/     COLORTERM=1
      complex/@PRGENV@/@PE_PETSC_DEFAULT_GENCOMPS@/                      BASH_FUNC_module%%=() { eval ‘/opt/cray/pe/modules/3.2.10.6/bin/
      @PE_PETSC_DEFAULT_TARGET@/lib/pkgconfig                                  modulecmd bash $*‘
PE_MPICH_NV_LIBS_nvidia35=-lcudart                                       }
PELOCAL_PRGENV=true                                                      + lsb_release -a
SLURM_TIME_FORMAT=relative                                               LSB Version:    n/a
PKG_CONFIG_PATH=/opt/nvidia/cudatoolkit9.1/9.1.85_3.18-6.0.7.0_5.1       Distributor ID: SUSE
      __g2eb7c52/lib64/pkgconfig:/opt/cray/rca/2.2.18-6.0.7.1_5.47       Description:    SUSE Linux Enterprise Server 12 SP3
      __g2aa4f39.ari/lib64/pkgconfig:/opt/cray/alps/6.6.43-6.0.7.1_5     Release:        12.3
      .45__ga796da32.ari/lib64/pkgconfig:/opt/cray/xpmem                 Codename:       n/a
      /2.2.15-6.0.7.1_5.11__g7549d06.ari/lib64/pkgconfig:/opt/cray/gni   + uname -a
      -headers/5.0.12.0-6.0.7.1_3.11__g3b1768f.ari/lib64/pkgconfig:/     Linux daint105 4.4.162-94.72-default #1 SMP Mon Nov 12 18:57:45 UTC
      opt/cray/dmapp/7.1.1-6.0.7.1_5.45__g5a674e0.ari/lib64/pkgconfig          2018 (9de753f) x86_64 x86_64 x86_64 GNU/Linux
      :/opt/cray/pe/pmi/5.0.14/lib64/pkgconfig:/opt/cray/ugni            + lscpu
      /6.0.14.0-6.0.7.1_3.13__gea11d3d.ari/lib64/pkgconfig:/opt/cray/    Architecture:           x86_64
      udreg/2.3.2-6.0.7.1_5.13__g5196236.ari/lib64/pkgconfig:/opt/cray   CPU op-mode(s):         32-bit, 64-bit
      /pe/craype/2.5.15/pkg-config:/opt/cray/pe/iobuf/2.0.8/lib/         Byte Order:             Little Endian
      pkgconfig:/opt/slurm/17.11.12.cscs/lib64/pkgconfig:/opt/slurm/     CPU(s):                 20
      default/lib64/pkgconfig:/opt/cray/pe/atp/2.1.2/lib/pkgconfig       On-line CPU(s) list:    0-19
LESSOPEN=lessopen.sh %s                                                  Thread(s) per core:     1
PE_TPSL_64_DEFAULT_GENCOMPS_INTEL_x86_64=160                             Core(s) per socket:     10
LIBSCI_BASE_DIR=/opt/cray/pe/libsci/18.07.1                              Socket(s):              2
CRAYPAT_OPTS_EXECUTABLE=sbin/pat-opts                                    NUMA node(s):           2
PE_TPSL_DEFAULT_GENCOMPS_INTEL_mic_knl=160                               Vendor ID:              GenuineIntel
PE_TPSL_64_DEFAULT_GENCOMPS_GNU_sandybridge=71 53 49                     CPU family:             6
PE_MPICH_NV_LIBS_nvidia60=-lcudart                                       Model:                  63
PE_LIBSCI_DEFAULT_PKGCONFIG_VARIABLES=                                   Model name:             Intel(R) Xeon(R) CPU E5-2650 v3 @ 2.30GHz
      PE_LIBSCI_DEFAULT_OMP_REQUIRES_@openmp@:PE_SCI_EXT_LIBPATH:        Stepping:               2
      PE_SCI_EXT_LIBNAME                                                 CPU MHz:                1200.025
LIBSCI_VERSION=18.07.1                                                   CPU max MHz:            3000.0000
INFOPATH=/opt/gcc/6.2.0/snos/share/info                                  CPU min MHz:            1200.0000
CC=cc                                                                    BogoMIPS:               4600.15
PE_TPSL_64_DEFAULT_GENCOMPILERS_GNU_x86_64=7.1 5.3 4.9                   Virtualization:         VT-x
PE_PGI_DEFAULT_FIXED_PKGCONFIG_PATH=/opt/cray/pe/parallel-netcdf         L1d cache:              32K
      /1.8.1.3/PGI/15.3/lib/pkgconfig:/opt/cray/pe/netcdf-hdf5parallel   L1i cache:              32K
      /4.6.1.2/PGI/17.10/lib/pkgconfig:/opt/cray/pe/netcdf/4.6.1.2/PGI   L2 cache:               256K
      /17.10/lib/pkgconfig:/opt/cray/pe/hdf5-parallel/1.10.2.0/PGI       L3 cache:               25600K
      /17.10/lib/pkgconfig:/opt/cray/pe/hdf5/1.10.2.0/PGI/17.10/lib/     NUMA node0 CPU(s):      0,2,4,6,8,10,12,14,16,18
      pkgconfig:/opt/cray/pe/ga/5.3.0.8/PGI/17.10/lib/pkgconfig          NUMA node1 CPU(s):      1,3,5,7,9,11,13,15,17,19
PE_LIBSCI_GENCOMPILERS_INTEL_x86_64=16.0                                 Flags:                  fpu vme de pse tsc msr pae mce cx8 apic sep
PE_FFTW_DEFAULT_TARGET_broadwell=broadwell                                     mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2
CRAY_ALPS_INCLUDE_OPTS=-I/opt/cray/alps/6.6.43-6.0.7.1_5.45                    ss ht tm pbe syscall nx pdpe1gb rdtscp lm ibrs flush_l1d
      __ga796da32.ari/include                                                  constant_tsc arch_perfmon pebs bts rep_good nopl xtopology
CRAY_CPU_TARGET=haswell                                                        nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor
CRAY_PRE_COMPILE_OPTS=-hnetwork=aries                                          ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca
XDG_RUNTIME_DIR=/run/user/23600                                                sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave
XTPE_LINK_TYPE=dynamic                                                         avx f16c rdrand lahf_lm abm ida arat epb invpcid_single pln pts
craype_already_loaded=0                                                        dtherm ssbd ibpb stibp kaiser tpr_shadow vnmi flexpriority ept
PE_TPSL_64_DEFAULT_GENCOMPS_CRAY_x86_64=86                                     vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm
PE_PAPI_DEFAULT_ACCELL_FAMILY_LIBS=                                            xsaveopt cqm_llc cqm_occup_llc
PE_MPICH_DEFAULT_GENCOMPILERS_PGI=15.3                                   + cat /proc/meminfo
PE_LIBSCI_REQUIRED_PRODUCTS=PE_MPICH                                     MemTotal:       263274152 kB
CRAY_XPMEM_INCLUDE_OPTS=-I/opt/cray/xpmem/2.2.15-6.0.7.1_5.11            MemFree:        86758608 kB
      __g7549d06.ari/include                                             MemAvailable:   187873960 kB
CRAY_UGNI_INCLUDE_OPTS=-I/opt/cray/ugni/6.0.14.0-6.0.7.1_3.13            Buffers:         2570964 kB
      __gea11d3d.ari/include                                             Cached:         134770224 kB
PE_MPICH_GENCOMPS_PGI=153                                                SwapCached:             0 kB
PE_TPSL_DEFAULT_GENCOMPS_INTEL_haswell=160                               Active:          9569164 kB
PE_LIBSCI_GENCOMPS_GNU_x86_64=71 61 51 49                                Inactive:       128684260 kB
PE_LIBSCI_DEFAULT_GENCOMPILERS_GNU_x86_64=7.1 6.1 5.1 4.9                Active(anon):     935828 kB
PE_PETSC_DEFAULT_GENCOMPILERS_INTEL_x86_64=16.0                          Inactive(anon):      7048 kB
PE_FFTW_DEFAULT_TARGET_x86_64=x86_64                                     Active(file):    8633336 kB
ATP_HOME=/opt/cray/pe/atp/2.1.2                                          Inactive(file): 128677212 kB
LESSCLOSE=lessclose.sh %s %s                                             Unevictable:    15728720 kB
PE_TPSL_64_DEFAULT_GENCOMPILERS_INTEL_x86_skylake=16.0                   Mlocked:        15728720 kB
PE_SMA_DEFAULT_DIR_PGI_DEFAULT64=64                                      SwapTotal:      134217724 kB
PE_PETSC_DEFAULT_GENCOMPILERS_INTEL_haswell=16.0                         SwapFree:       134217724 kB
PE_PETSC_DEFAULT_GENCOMPILERS_GNU_interlagos=7.1 5.3 4.9                 Dirty:                980 kB
PE_PAPI_DEFAULT_ACCEL_LIBS=                                              Writeback:            112 kB
PE_INTEL_DEFAULT_FIXED_PKGCONFIG_PATH=/opt/cray/pe/parallel-netcdf       AnonPages:      16641048 kB
      /1.8.1.3/INTEL/16.0/lib/pkgconfig:/opt/cray/pe/netcdf-             Mapped:          1161008 kB
      hdf5parallel/4.6.1.2/INTEL/16.0/lib/pkgconfig:/opt/cray/pe/        Shmem:             30600 kB
Slab:             19340680 kB
SReclaimable:       1339944 kB
SUnreclaim:       18000736 kB
KernelStack:          23648 kB
PageTables:           83928 kB
NFS_Unstable:              0 kB
Bounce:                    0 kB
WritebackTmp:              0 kB
CommitLimit:      265854800 kB
Committed_AS:     18191864 kB
VmallocTotal:     34359738367 kB
VmallocUsed:               0 kB
VmallocChunk:              0 kB
HardwareCorrupted:         0 kB
AnonHugePages: 15501312 kB
HugePages_Total:           0
HugePages_Free:            0
HugePages_Rsvd:            0
HugePages_Surp:            0
Hugepagesize:          2048 kB
DirectMap4k:      11571956 kB
DirectMap2M:      234747904 kB
DirectMap1G:      24117248 kB
+ inxi -F -c0
./collect_environment.sh: line 14: inxi: command not found
+ lsblk -a
NAME    MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
loop0     7:0     0 2.6G 0 loop
loop1     7:1     0 34.7G 0 loop /var/opt/cray/imps-image-binding/PE/
      squash_mounts/squashfs_vSpo3d_mount_point
loop2     7:2     0           1 loop
loop3     7:3     0           0 loop
loop4     7:4     0           0 loop
loop5     7:5     0           0 loop
loop6     7:6     0           0 loop
loop7     7:7     0           0 loop
sda       8:0     0 700G 0 disk
    sda1      8:1      0 1007K 0 part
    sda2      8:2      0     2G 0 part /boot
    sda3      8:3      0    20G 0 part
    sda4      8:4      0 256G 0 part /tmp
    sda5      8:5      0 128G 0 part [SWAP]
sdb       8:16    0 1.5T 0 disk
    sdb1      8:17     0    10G 0 part /var/crash
    sdb2      8:18     0     2G 0 part /var/mmfs
    sdb3      8:19     0 1.5T 0 part /var/opt/cray/persistent
sr0      11:0     1 1024M 0 rom
+ lsscsi -s
[0:2:0:0]      disk      DELL      PERC H730 Mini 4.29 /dev/sda   751
      GB
[0:2:1:0]      disk      DELL      PERC H730 Mini 4.29 /dev/sdb  1.64
      TB
[10:0:0:0]     cd/dvd HL-DT-ST DVD+-RW GTA0N      A3B0 /dev/sr0
      -
+ module list
++ /opt/cray/pe/modules/3.2.10.6/bin/modulecmd bash list
Currently Loaded Modulefiles:
  1) modules/3.2.10.6
  2) cray-mpich/7.7.2
  3) slurm/17.11.12.cscs-1
  4) xalt/daint-2016.11
  5) daint-gpu
  6) gcc/6.2.0
  7) craype-haswell
  8) craype-network-aries
  9) craype/2.5.15
 10) cray-libsci/18.07.1
 11) udreg/2.3.2-6.0.7.1_5.13__g5196236.ari
 12) ugni/6.0.14.0-6.0.7.1_3.13__gea11d3d.ari
 13) pmi/5.0.14
 14) dmapp/7.1.1-6.0.7.1_5.45__g5a674e0.ari
 15) gni-headers/5.0.12.0-6.0.7.1_3.11__g3b1768f.ari
 16) xpmem/2.2.15-6.0.7.1_5.11__g7549d06.ari
 17) job/2.2.3-6.0.7.1_5.43__g6c4e934.ari
 18) dvs/2.7_2.2.118-6.0.7.1_10.2__g58b37a2
 19) alps/6.6.43-6.0.7.1_5.45__ga796da32.ari
 20) rca/2.2.18-6.0.7.1_5.47__g2aa4f39.ari
 21) atp/2.1.2
 22) perftools-base/7.0.3
 23) PrgEnv-gnu/6.0.4
 24) cudatoolkit/9.1.85_3.18-6.0.7.0_5.1__g2eb7c52

