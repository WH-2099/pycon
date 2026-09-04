# 幻灯片内容与最终资产

资源整理日期：2026-09-05。
讲稿统一维护在项目根目录的 [最终讲稿](../最终讲稿.md)，幻灯片入口是 [slides.py](../slides.py)。
本目录保留正在使用的内容、图片来源与核验说明。
过程截图、历史画廊、未采用的图片与 Mermaid 版本已清理。

## 放映与维护

运行 `just edit` 编辑，或运行 `just present` 放映。
也可直接运行 [`./present.sh`](../present.sh)（或 `sh present.sh`），无需安装 just。
默认端口为 `2718`；需要更换时运行 `./present.sh 3000` 或 `just present 3000`。
首次使用先运行 `uv sync` 准备依赖；脚本会从项目目录启动离线放映服务。
当前共 44 页：35 个正文或时间线配图页、57 个内容分段，以及 9 个开场、章节索引、总结、展望与答谢页。
正文分段按图片 → 代码 → Mermaid 展示，没有的类型自动省略。
空格或右方向键显示下一段，左方向键回看本页前一段；最后一段之后进入下一页。
第 2—4 章的 Index 各保留"三问概览 → 本章聚焦"两步展示。
第五章的总结与展望各自独立成页，随后用手动协调与 bocpy 两页对照同一组 A/B/C 工作。
后者以 Behavior-Oriented Concurrency 为完整标题，将资源声明与必要顺序合为一张图。

- [chapters.toml](chapters.toml)：29 个正文页的标题、说明、代码、保留的 9 份 Mermaid、替代文本及来源。
- [timelines.toml](timelines.toml)：6 个时间线图片页的文案、替代文本及来源。
- [TIMELINES.md](TIMELINES.md)：时间线位置、发布状态与事实边界。
- [prompts.json](prompts.json)：全部 40 张在用配图的最终生成或编辑指令、日期、尺寸、SHA-256 与已记录的生成来源。

使用固定图片版本的页面不保留隐藏的代码或 Mermaid 候选。
`just check` 验证页面覆盖与顺序、分段规则、图片清单及哈希，并运行代码示例。
代码可以直接复制；进程池与解释器池示例应另存为 `.py` 文件运行。
当前未引入 CDN 或外部图标，背景、字体、图片和音频均从本地资源提供。

## 配图清单

以下 40 张 PNG 均由内置 `image_gen.imagegen` 生成或修改，实际使用路径统一为 `public/illustrations/`。
清单只记录当前版本的最终指令，不保留弃选生成结果或多轮中间稿。
历史编辑指令中的参考图不另作演讲资产保留，缺失的早期生成路径不作推定补录。
图内少量标签解释关系，页标题、说明和版本信息放在图外，不叠加长段正文。
图片保持比例完整显示，右侧为会场背景留出安全区，具体尺寸见生成清单。
这些图是说明插图，不是测量结果；背景与音频的来源和使用约定见 [NOTES.md](../NOTES.md)。

| 成品 | 当前用途 | 展示顺序 |
| --- | --- | --- |
| [01-timeline](../public/illustrations/01-timeline.png) | 从能够并发，到怎样并发得好 | 图片 |
| [02-01-pause](../public/illustrations/02-01-pause.png) | 暂停，现场留下来 | 图片 → 代码 |
| [02-02-wait](../public/illustrations/02-02-wait.png) | 等结果时，推进别的任务 | 图片 → 代码 → Mermaid |
| [02-03-ownership](../public/illustrations/02-03-ownership.png) | 函数返回了，任务归谁？ | 图片 → 代码 |
| [02-04-taskgroup](../public/illustrations/02-04-taskgroup.png) | 失败回到父级，清理留在组内 | 图片 → 代码 → Mermaid |
| [02-05-structure](../public/illustrations/02-05-structure.png) | 调用栈，长成责任树 | 图片 → 代码 |
| [02-timeline](../public/illustrations/02-timeline.png) | 从函数暂停，到任务有归属 | 图片 |
| [03-01-processes](../public/illustrations/03-01-processes.png) | 跨进程，各有一份运行时 | 图片 → 代码 |
| [03-02-interpreters](../public/illustrations/03-02-interpreters.png) | 同一进程，分开解释器状态 | 图片 → 代码 |
| [03-02a-interpreter-state](../public/illustrations/03-02a-interpreter-state.png) | 先把状态分开，GIL 才能分开 | 图片 |
| [03-02b-interpreter-transfer](../public/illustrations/03-02b-interpreter-transfer.png) | 对象跨界，先说清复制还是共享 | 图片 |
| [03-03-threads](../public/illustrations/03-03-threads.png) | 同一解释器，也能多核执行 | 图片 → 代码 |
| [03-04-parallel](../public/illustrations/03-04-parallel.png) | 三条路线，三种边界 | 图片 → 代码 |
| [03-timeline](../public/illustrations/03-timeline.png) | 三条并行路线，一直并存 | 图片 |
| [04-01-boundaries](../public/illustrations/04-01-boundaries.png) | 先减少共同写入 | 图片 → 代码 → Mermaid |
| [04-01a-local](../public/illustrations/04-01a-local.png) | 请求切换，状态跟着任务走 | 图片 |
| [04-01b-transfer](../public/illustrations/04-01b-transfer.png) | 消息照样传，大块数据少搬运 | 图片 |
| [04-01c-immutable](../public/illustrations/04-01c-immutable.png) | 冻结键值关系，还要看值会不会变 | 图片 |
| [04-02-race](../public/illustrations/04-02-race.png) | 各步安全，整段仍会竞态 | 图片 → 代码 → Mermaid |
| [04-03-protection](../public/illustrations/04-03-protection.png) | 全局锁拆开，保护分头接手 | 图片 → Mermaid |
| [04-04-refcounts](../public/illustrations/04-04-refcounts.png) | 少争同一个计数器 | 图片 → Mermaid |
| [04-04a-biased-counting](../public/illustrations/04-04a-biased-counting.png) | 常走本地路径，必要时协调合并 | 图片 |
| [04-04b-deferred-counting](../public/illustrations/04-04b-deferred-counting.png) | 少争计数器，也要补齐存活信息 | 图片 |
| [04-05-memory-gc](../public/illustrations/04-05-memory-gc.png) | 先得到稳定的堆视图 | 图片 → Mermaid |
| [04-05a-gc-heap](../public/illustrations/04-05a-gc-heap.png) | 分配器找到对象，类型说明引用 | 图片 |
| [04-05b-gc-cycle](../public/illustrations/04-05b-gc-cycle.png) | 先找不可达，再确认没有复活 | 图片 |
| [04-06-containers](../public/illustrations/04-06-containers.png) | 对象锁保护容器内部 | 图片 → Mermaid |
| [04-07-extensions](../public/illustrations/04-07-extensions.png) | 并发约定，扩展也要重签 | 图片 → 代码 |
| [04-08-lock](../public/illustrations/04-08-lock.png) | 完整状态变化，放进锁里 | 图片 → 代码 → Mermaid |
| [04-09-state](../public/illustrations/04-09-state.png) | 谁看，谁改，谁保护 | 图片 |
| [04-timeline](../public/illustrations/04-timeline.png) | 共享越自由，保护越具体 | 图片 |
| [05-01-manual-state](../public/illustrations/05-01-manual-state.png) | 锁与等待，仍要自己接起来 | 图片 |
| [05-02-bocpy](../public/illustrations/05-02-bocpy.png) | 声明资源，运行时安排必要顺序 | 图片 |
| [05-timeline-outlook](../public/illustrations/05-timeline-outlook.png) | 下一步：让关系进入运行时？ | 图片 |
| [05-timeline-summary](../public/illustrations/05-timeline-summary.png) | 三条演进线，汇成三个责任 | 图片 |
| [index-organization](../public/illustrations/index-organization.png) | 第二章 Index：同步调用与返回 | 图片 |
| [index-parallel](../public/illustrations/index-parallel.png) | 第三章 Index：同一解释器内的 GIL 与等待 | 图片 |
| [index-state](../public/illustrations/index-state.png) | 第四章 Index：跨执行域传值 | 图片 |
| [05-summary](../public/illustrations/05-summary.png) | 自由之后：局部结构接手保护责任 | 图片 |
| [05-outlook](../public/illustrations/05-outlook.png) | 自由之后：让关系进入运行时？ | 图片 |

## 核验记录

时间线完成 4 轮页面审查，深化页完成 5 轮，Index 与"自由之后"完成 5 轮生图和 sub-agent 页面审查。
手动协调与 Behavior-Oriented Concurrency 两页完成 4 轮生图及两名 sub-agent 的实际页面审查，1920 × 1080 与 1280 × 720 均通过。
迭代补清了同名锁、用后释放与提交前提，并改善执行条件的字号和窄屏标题换行。
最终两页的美观、讲稿辅助与观众理解评分均至少为 4/5。
最终版本均通过对应的实际渲染复核；本轮仅保留结论，过程截图与逐轮报告按要求移除。
此前的整套 1920 × 1080 放映检查覆盖 35 个配图页、57 个分段、22 次页内回退及其余 9 页。
三个 Index 的概览与聚焦、总结与展望共 8 个状态也逐页复核，未发现裁切、重叠、图片加载失败、浏览器异常或外部请求。
工程验证使用 `just format` → `just check`，覆盖 justfile、uv 锁文件、Ruff、rumdl、ty、marimo 与例程行为。

## 内容边界

1. `await` 是可能暂停的点，不保证每次切换任务；已完成的 awaitable 可以立即返回。
   [Python 3.14 asyncio 文档](https://docs.python.org/3.14/library/asyncio-task.html)。
2. TaskGroup 管理通过该组创建的任务；普通非取消异常才触发相应失败处理，`KeyboardInterrupt` 与 `SystemExit` 有特殊规则。
   [TaskGroup 文档](https://docs.python.org/3.14/library/asyncio-task.html#task-groups)。
3. PEP 789 仍为 Draft，提议约束 `yield` / `yield from`，不能把 `await` 也画成禁用操作。
   [PEP 789](https://peps.python.org/pep-0789/)。
4. 并发可以包含并行，竞态也能由单线程协程交错或有 GIL 的线程产生；不能沿用 2025 实录中"并发绝非同时执行"的绝对化说法。
   [Python 线程安全说明](https://docs.python.org/3.14/howto/free-threading-python.html#thread-safety)。
5. 多解释器隔离 Python 状态，但共享进程级资源，不是安全沙箱；本页特指标准池创建的隔离解释器配置。
   [InterpreterPoolExecutor 文档](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor)。
6. free-threaded 构建不保证运行时 GIL 关闭；迁移时要在导入所需扩展后检测。
   [自由线程运行说明](https://docs.python.org/3.14/howto/free-threading-python.html#the-global-interpreter-lock-in-free-threaded-python)。
7. 线程队列不自动复制对象；传递引用后继续无约束地修改原对象，仍可能共享可变状态。
   [queue 文档](https://docs.python.org/3.14/library/queue.html)。
8. PEP 814 已 Final，目标是尚未正式发布的 3.15；`frozendict` 只有浅层不可变，内部列表仍可变，也不保证任何值组合都可哈希。
   [PEP 814](https://peps.python.org/pep-0814/)。
9. 永生、延迟、偏置与分线程计数不是每个对象必经的四个连续阶段，永生对象不进入通常回收路径。
   [自由线程引用计数说明](https://docs.python.org/3.14/howto/free-threading-python.html)。
10. 3.14 自由线程 GC 的非分代、mimalloc 遍历与两次停止世界暂停都能在对应版本源码文档中核对。
    [CPython v3.14.7 GC 内部文档](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/garbage_collector.md)。
11. 原稿的特化互斥锁与单次特化描述属于 PEP 703 设计脉络，3.14 已有线程本地字节码；关闭 TLBC 也会关闭特化。
    [3.14 命令行中的 `-X tlbc`](https://docs.python.org/3.14/using/cmdline.html#cmdoption-X)。
12. 真实强引用 API 是 `PyList_GetItemRef` / `PyDict_GetItemRef`，扩展声明值是 `Py_MOD_GIL_NOT_USED`，环境变量是 `PYTHON_GIL`。
    [3.14 扩展迁移文档](https://docs.python.org/3.14/howto/free-threading-extensions.html)。
13. 3.14 的自由线程 wheel 与 3.15 的 `abi3t` stable ABI 应分开讲，不能把 PEP 803 的落地时间提前。
    [PEP 803](https://peps.python.org/pep-0803/)。

逐页版本、讲者备注与一手来源保存在内容源中。
文中提到的 PEP 原文均已有 [ref/peps](../ref/peps/) 归档。
