# 引用资料索引

核验与获取日期：2026-09-04。

## 归档口径

- `peps/` 中的 52 份 PEP 来自 Python 官方 `python/peps` 仓库的 RST 原文。
- 固定快照为 commit `24419b92ae550bf2878716f57c257cba00d3c1a1`。
- 文件使用 Pandoc 3.9 转为 GFM Markdown，便于检索和批注；内容语义保留，但排版不等同于官网 HTML。
- 转换稿带有 `rumdl-disable-file`，避免自动格式化继续改写来源结构；本索引仍接受完整 Markdown 检查。
- 标题、状态和目标版本以获取日的官方 PEP API 为准，草案与预发布版本在演讲前必须再次核验。
- `proposals/` 只放尚未进入正式 PEP 仓库的提案快照，不能把其中内容称为已发布 PEP。
- `python-docs/` 保存 CPython `v3.15.0rc2` 的关键官方文档 Markdown 快照。
- [`papers/`](papers/README.md) 只做一次简单下载与文本转写，未成功项记录在该目录索引中，留待手动补齐。

官方入口：[PEP Index](https://peps.python.org/) · [PEP 源码仓库](https://github.com/python/peps)。

第四章的结构讨论见 [第四章结构备选与资料核读](chapter4-structure-options.md)，包含配套演讲材料的阅读记录、四种结构与现有段落的取舍。

## 当前讲稿的主要资料

以下资料直接支撑当前讲稿主线。

后文继续保留完整归档及状态索引。

### 总体视角

- [PEP 703](peps/pep-0703.md) 说明 GIL 可选化及 CPython 为此补充的内部同步机制。
- [Concurrency is not Parallelism](papers/concurrency-is-not-parallelism.md) 用于区分并发结构与并行执行。

### 任务怎样被组织

- [PEP 255](peps/pep-0255.md)、[PEP 342](peps/pep-0342.md) 和 [PEP 380](peps/pep-0380.md) 构成生成器从暂停到通信、清理与委托的历史线。
- [PEP 3156](peps/pep-3156.md) 和 [PEP 492](peps/pep-0492.md) 记录 `asyncio` 与原生协程进入标准库和语言语法的过程。
- [PEP 654](peps/pep-0654.md) 与 [TaskGroup 官方文档](python-docs/asyncio-task.md) 支撑任务生命周期、取消和异常传播部分。
- [PEP 789](peps/pep-0789.md) 仍为 Draft，用于说明结构化并发边界仍在完善。
- [Notes on Structured Programming](papers/ewd249-notes-on-structured-programming.md) 与 [Notes on structured concurrency](papers/notes-on-structured-concurrency.md) 支撑从结构化编程到任务作用域的思想线。

### 任务怎样真并行

- [PEP 371](peps/pep-0371.md) 记录 Python 通过多进程隔离获得多核并行的标准库路线。
- [PEP 684](peps/pep-0684.md) 和 [PEP 734](peps/pep-0734.md) 分别支撑每解释器 GIL 与标准库多解释器路线。
- [PEP 687](peps/pep-0687.md) 说明标准库扩展如何将进程全局状态移入模块实例，为解释器隔离打好基础。
  [官方原文](https://peps.python.org/pep-0687/) 按上述快照与转换方式于核验日补齐。
- [PEP 703](peps/pep-0703.md) 和 [PEP 779](peps/pep-0779.md) 记录 Free-Threading 从实验构建走向正式但可选支持的过程。
- [多解释器文档](python-docs/concurrent.interpreters.md) 与 [自由线程 HOWTO](python-docs/free-threading-python.md) 用于核对当前用户可见行为和限制。

### 任务怎样共享状态

- [PEP 416](peps/pep-0416.md)、[PEP 603](peps/pep-0603.md) 和 [PEP 814](peps/pep-0814.md) 构成不可变映射从被拒绝、继续探索到进入 Python 3.15 的历史线。
- PEP 814 的浅拷贝示例用于说明浅层不可变的边界：映射中的列表仍然可以修改。
- [Executor 官方文档](python-docs/concurrent.futures.md) 用于核对复制、序列化和执行边界之间的关系。
- [`queue.Queue` 源码](https://github.com/python/cpython/blob/v3.15.0rc2/Lib/queue.py) 用于核对线程间队列传递对象引用，不自动转移访问权。
- [PEP 703](peps/pep-0703.md) 说明自由线程如何在引用计数、内存管理、垃圾回收和容器访问中补回同步。
- [PEP 442](peps/pep-0442.md) 说明循环对象安全终结及终结后的隔离再检查。
  [官方原文](https://peps.python.org/pep-0442/) 按上述快照与转换方式于核验日补齐。
- [线程安全保证](python-docs/threadsafety.md) 与 [共享内存文档](python-docs/multiprocessing.shared_memory.md) 用于区分共享、同步和业务原子性。
- [Data Race Freedom à la Mode](papers/data-race-freedom-a-la-mode.md) 与 [Dynamic Region Ownership](papers/dynamic-region-ownership.md) 提供所有权和安全共享的研究背景。

### 总结与展望

- [PEP 779 Steering Council 接受说明](https://discuss.python.org/t/pep-779-criteria-for-supported-status-for-free-threaded-python/84319/123) 是关于发展更高层并发原语这一要求的直接来源。
- [PEP 805](peps/pep-0805.md) 仍为 Draft，用于展望对象状态与访问关系进入运行时的一种可能方向。
- [When Concurrency Matters](papers/when-concurrency-matters.md) 提出 Behaviour-Oriented Concurrency，并说明 Behavior 与 Cown 的资源关系。
- [When Behaviours Have to Happen](papers/when-behaviours-have-to-happen.md) 进一步讨论 BOC 中哪些先后关系由模型要求。
- [`bocpy` 官方文档](https://microsoft.github.io/bocpy/) 用于核对 BOC 在 CPython 上的实验接口、实现状态与保证边界。
- [bocpy 固定版本 README](bocpy-c8f3cebc.md) 归档 `c8f3cebc` 的官方说明，供新增 BOC 两页与源码交叉核验。
- [Time, Clocks, and the Ordering of Events](papers/time-clocks-ordering-events.md) 提供事件偏序与 happened-before 的理论背景。

## 讲稿准备阶段明确使用过的 PEP

| 本地文件 | 标题 | 状态 |
| --- | --- | --- |
| [PEP 20](peps/pep-0020.md) | The Zen of Python | Active |
| [PEP 255](peps/pep-0255.md) | Simple Generators | Final |
| [PEP 342](peps/pep-0342.md) | Coroutines via Enhanced Generators | Final |
| [PEP 351](peps/pep-0351.md) | The freeze protocol | Rejected |
| [PEP 371](peps/pep-0371.md) | Addition of the multiprocessing package to the standard library | Final |
| [PEP 380](peps/pep-0380.md) | Syntax for Delegating to a Subgenerator | Final |
| [PEP 416](peps/pep-0416.md) | Add a frozendict builtin type | Rejected |
| [PEP 442](peps/pep-0442.md) | Safe object finalization | Final，Python 3.4 |
| [PEP 489](peps/pep-0489.md) | Multi-phase extension module initialization | Final |
| [PEP 492](peps/pep-0492.md) | Coroutines with async and await syntax | Final |
| [PEP 554](peps/pep-0554.md) | Multiple Interpreters in the Stdlib | Superseded by PEP 734 |
| [PEP 567](peps/pep-0567.md) | Context Variables | Final |
| [PEP 573](peps/pep-0573.md) | Module State Access from C Extension Methods | Final |
| [PEP 574](peps/pep-0574.md) | Pickle protocol 5 with out-of-band data | Final |
| [PEP 583](peps/pep-0583.md) | A Concurrency Memory Model for Python | Withdrawn |
| [PEP 603](peps/pep-0603.md) | Adding a frozenmap type to collections | Draft |
| [PEP 630](peps/pep-0630.md) | Isolating Extension Modules | Final |
| [PEP 654](peps/pep-0654.md) | Exception Groups and except* | Final |
| [PEP 683](peps/pep-0683.md) | Immortal Objects, Using a Fixed Refcount | Final |
| [PEP 684](peps/pep-0684.md) | A Per-Interpreter GIL | Final |
| [PEP 687](peps/pep-0687.md) | Isolating modules in the standard library | Final，Python 3.12 |
| [PEP 703](peps/pep-0703.md) | Making the Global Interpreter Lock Optional in CPython | Final |
| [PEP 734](peps/pep-0734.md) | Multiple Interpreters in the Stdlib | Final |
| [PEP 779](peps/pep-0779.md) | Criteria for supported status for free-threaded Python | Final |
| [PEP 788](peps/pep-0788.md) | Protecting the C API from Interpreter Finalization | Final |
| [PEP 789](peps/pep-0789.md) | Preventing task-cancellation bugs by limiting yield in async generators | Draft |
| [PEP 797](peps/pep-0797.md) | Shared Object Proxies | Rejected |
| [PEP 803](peps/pep-0803.md) | "abi3t": Stable ABI for Free-Threaded Builds | Final |
| [PEP 805](peps/pep-0805.md) | Safe Parallel Python | Draft |
| [PEP 814](peps/pep-0814.md) | Add frozendict built-in type | Final |
| [PEP 3121](peps/pep-3121.md) | Extension Module Initialization and Finalization | Final |
| [PEP 3148](peps/pep-3148.md) | futures - execute computations asynchronously | Final |
| [PEP 3156](peps/pep-3156.md) | Asynchronous IO Support Rebooted: the asyncio Module | Final |

PEP 805 的原文使用两个 include 文件，已分别归档为
[示例附录](peps/pep-0805-appendix-examples.md) 和 [实现附录](peps/pep-0805-appendix-implementation.md)。

## 扩展背景 PEP

| 本地文件 | 相关背景 | 状态 |
| --- | --- | --- |
| [PEP 311](peps/pep-0311.md) | 扩展模块获取 GIL 的早期接口 | Final |
| [PEP 384](peps/pep-0384.md) | Stable ABI 起点 | Final |
| [PEP 475](peps/pep-0475.md) | 被信号中断的系统调用重试语义 | Final |
| [PEP 525](peps/pep-0525.md) | 异步生成器 | Final |
| [PEP 530](peps/pep-0530.md) | 异步推导式 | Final |
| [PEP 533](peps/pep-0533.md) | 迭代器确定性清理的历史方案 | Deferred |
| [PEP 550](peps/pep-0550.md) | 执行上下文的历史方案 | Withdrawn |
| [PEP 568](peps/pep-0568.md) | 生成器与 ContextVar 的历史方案 | Deferred |
| [PEP 652](peps/pep-0652.md) | Stable ABI 维护规则 | Final |
| [PEP 688](peps/pep-0688.md) | Python 层 buffer protocol | Final |
| [PEP 689](peps/pep-0689.md) | Unstable C API 层级 | Final |
| [PEP 697](peps/pep-0697.md) | 不透明类型的 Limited C API | Final |
| [PEP 790](peps/pep-0790.md) | Python 3.15 发布计划 | Active |
| [PEP 793](peps/pep-0793.md) | C 扩展新入口 PyModExport | Final |
| [PEP 820](peps/pep-0820.md) | C API 统一 slot 系统 | Final |
| [PEP 828](peps/pep-0828.md) | 异步生成器中的 yield from | Accepted，目标 3.16 |
| [PEP 839](peps/pep-0839.md) | frozen 容器 C API | Draft，目标 3.16 |
| [PEP 841](peps/pep-0841.md) | frozen 语法与优化 | Draft，目标 3.16 |
| [PEP 3118](peps/pep-3118.md) | buffer protocol 基础 | Final |

## 尚未发布的提案

[PEP 795 提案草案固定快照](proposals/pep-0795-afe96b99.md) 来自
[`python/peps` PR #4468](https://github.com/python/peps/pull/4468) 的 commit
`afe96b99ab1ac02f935a407a93d4b81318ec913c`。

截至核验日，`peps.python.org/pep-0795/` 不存在，官方主仓库也没有该编号。
它只能称为"尚未合入的 PEP 795 提案草案"，其 API、范围和目标版本均可能继续变化。

## 时点提醒

- Python 3.15 当前为 3.15.0rc2，PEP 790 计划的最终发布日期是 2026-10-01。
- PEP 805、839、841 仍是 Draft；目标版本不是落地承诺。
- PEP 797 已于 2026-07-08 被拒绝。
- PEP 583 已撤回，不能作为现行 Python 内存模型。
- PEP 603 仍是 Draft，不能讲成已经提供的内置能力。
- Python 3.15 的内建类型线程安全说明比泛化的"线程安全"断言更精确，但仍不是跨实现的完整语言内存模型。

相关官方页面：[Python 3.15 线程安全保证](https://docs.python.org/3.15/library/threadsafety.html)。

章节时间线的逐图一手来源、发布状态和核验说明见 [时间线资料索引](../slide_assets/TIMELINES.md)。
