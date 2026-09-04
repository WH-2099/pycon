import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="full",
    css_file="slides.css",
    layout_file="layouts/slides.slides.json",
)


@app.cell
def _():
    from itertools import starmap

    import marimo as mo

    from slide_variants import candidate_slide

    def chapter_transition(current):
        chapters = (
            (
                2,
                "任务怎样被",
                "组织",
                "普通函数通常沿调用栈运行到返回",
                "index-organization",
                "同步调用栈中，调用者调用普通函数，函数完成后返回调用者",
                "#087fbd",
            ),
            (
                3,
                "任务怎样真",
                "并行",
                "GIL 启用时，线程轮流执行 Python",
                "index-parallel",
                "同一解释器内，两个线程受同一把 GIL 约束，轮流执行 Python",
                "#e67700",
            ),
            (
                4,
                "任务怎样共享",
                "状态",
                "跨执行域传值时，需要明确的数据交接",
                "index-state",
                "以传值为例，两个执行域各自持有对象，通过明确的数据交接交换内容",
                "#b7791f",
            ),
        )
        selected = {current: " is-current"}

        def chapter_item(number, prefix, keyword, example, image_id, label, accent):
            picture = mo.image(f"public/illustrations/{image_id}.png", alt=label)
            return f"""
            <article
              class="chapter-transition-item{selected.get(number, "")}"
              style="--chapter-accent: {accent}"
            >
              <h2 class="chapter-transition-title">
                <span>{prefix}</span>
                <strong>{keyword}</strong>
                <span class="chapter-transition-mark">？</span>
              </h2>
              <p class="chapter-transition-example">{example}</p>
              <figure class="chapter-transition-diagram">{picture}</figure>
            </article>
            """

        items = "".join(starmap(chapter_item, chapters))
        return mo.Html(f"""
        <div class="chapter-transition">
          <span
            class="fragment custom chapter-transition-focus"
            data-fragment-index="0"
            aria-hidden="true"
          ></span>
          <div class="chapter-transition-list">{items}</div>
        </div>
        """)

    final_summary_header = """
    <header class="final-summary-header">
      <p class="final-summary-kicker" aria-label="总结与展望">
        <span aria-hidden="true">总</span>
        <span aria-hidden="true">结</span>
        <span aria-hidden="true">与</span>
        <span aria-hidden="true">展</span>
        <span aria-hidden="true">望</span>
      </p>
      <h1 aria-label="自由之后">
        <span aria-hidden="true">自</span>
        <span aria-hidden="true">由</span>
        <span aria-hidden="true">之</span>
        <span aria-hidden="true">后</span>
      </h1>
    </header>
    """

    return candidate_slide, chapter_transition, final_summary_header, mo


@app.cell(hide_code=True)
def cover_warmup(mo):
    backgrounds = {
        name: mo.image(f"public/bg-{name}.png")
        for name in ("cover", "content", "collaboration")
    }
    background_urls = {
        name: image.text.split("src='", maxsplit=1)[1].split("'", maxsplit=1)[0]
        for name, image in backgrounds.items()
    }
    fonts = {
        "sans": mo.image("public/fonts/noto-sans-sc-variable.otf"),
        "serif": mo.image("public/fonts/lora-variable.ttf"),
    }
    font_urls = {
        name: font.text.split("src='", maxsplit=1)[1].split("'", maxsplit=1)[0]
        for name, font in fonts.items()
    }
    player = mo.audio("public/ai.flac")
    player = mo.Html(
        player.text.replace(
            "<audio ",
            '<audio class="warmup-player" loop preload="metadata" '
            'aria-label="暖场音乐：小虎队《爱》" ',
            1,
        )
    )
    clock = mo.iframe(
        """
        <script>
        const diagramSheet = new parent.CSSStyleSheet();
        diagramSheet.replaceSync(`
          .marimo > .contents > div {
            display: grid;
            grid-template: minmax(0, 1fr) / minmax(0, 1fr);
            width: 100%; height: 100%; min-width: 0; min-height: 0;
          }
          svg { width: 100%; height: 100%; max-width: none !important; }
        `);
        const fitDiagrams = () => {
          parent.document.querySelectorAll("marimo-mermaid").forEach((host) => {
            const root = host.shadowRoot;
            if (root && !root.adoptedStyleSheets.includes(diagramSheet)) {
              root.adoptedStyleSheets.push(diagramSheet);
            }
          });
        };
        const diagramObserver = new parent.MutationObserver(fitDiagrams);
        diagramObserver.observe(parent.document.getElementById("App"), {
          childList: true, subtree: true,
        });
        parent.customElements.whenDefined("marimo-mermaid").then(fitDiagrams);
        addEventListener("unload", () => diagramObserver.disconnect(), { once: true });

        let cleanup = () => {};
        const initFrame = parent.requestAnimationFrame(() => {
          const root = frameElement?.closest(".warmup");
          const slide = root?.closest("section");
          const audio = root?.querySelector(".warmup-player");
          const animations = [...(root?.querySelectorAll(".warmup-word") ?? [])]
            .flatMap((word) => word.getAnimations());
          if (!slide || !audio || !animations.length) return;

          let frame = 0;
          let spaceStarted = !audio.paused;
          const sync = () => {
            const time = audio.currentTime * 1000;
            animations.forEach((animation) => { animation.currentTime = time; });
          };
          const tick = () => {
            frame = 0;
            sync();
            if (!audio.paused && audio.isConnected) {
              frame = parent.requestAnimationFrame(tick);
            }
          };
          const start = () => {
            spaceStarted = true;
            if (!frame) tick();
          };
          const stop = () => {
            if (frame) parent.cancelAnimationFrame(frame);
            frame = 0;
            sync();
          };
          const handleSpace = (event) => {
            if (
              event.code !== "Space"
              || event.altKey
              || event.ctrlKey
              || event.metaKey
              || event.shiftKey
              || !slide.classList.contains("present")
            ) return;

            event.preventDefault();
            event.stopImmediatePropagation();
            if (event.repeat) return;

            if (!spaceStarted) {
              spaceStarted = true;
              void audio.play().catch(() => { spaceStarted = false; });
              return;
            }
            parent.document.querySelector(".navigate-right")?.click();
          };

          audio.addEventListener("playing", start);
          audio.addEventListener("pause", stop);
          audio.addEventListener("seeked", sync);
          parent.document.addEventListener("keydown", handleSpace, true);
          cleanup = () => {
            stop();
            audio.removeEventListener("playing", start);
            audio.removeEventListener("pause", stop);
            audio.removeEventListener("seeked", sync);
            parent.document.removeEventListener("keydown", handleSpace, true);
          };
          sync();
          if (!audio.paused) start();
        });
        addEventListener("unload", () => {
          parent.cancelAnimationFrame(initFrame);
          cleanup();
        }, { once: true });
        </script>
        """,
        width="0",
        height="0",
    )
    clock = mo.Html(
        clock.text.replace(
            "<iframe ",
            '<iframe aria-hidden="true" tabindex="-1" ',
            1,
        )
    )
    mo.Html(f"""
    <style>
      @font-face {{
        font-family: "PyCon Sans";
        font-style: normal;
        font-weight: 100 900;
        font-display: block;
        src: url("{font_urls["sans"]}") format("opentype");
      }}
      @font-face {{
        font-family: "PyCon Serif";
        font-style: normal;
        font-weight: 400 700;
        font-display: block;
        src: url("{font_urls["serif"]}") format("truetype");
      }}
      :root {{
        --slide-background-cover: url("{background_urls["cover"]}");
        --slide-background-content: url("{background_urls["content"]}");
        --slide-background-collaboration: url("{background_urls["collaboration"]}");
      }}
    </style>
    <div class="warmup">
      <div class="warmup-copy">
        <span class="warmup-assistive">AI 与爱</span>
        <div class="warmup-words" aria-hidden="true">
          <span class="warmup-word warmup-ai">AI</span>
          <span class="warmup-word warmup-love">爱</span>
        </div>
      </div>
      <div class="warmup-audio">
        {player}
      </div>
      {clock}
    </div>
    """)
    return


@app.cell(hide_code=True)
def cover_title(mo):
    mo.Html("""
    <div class="cover-title">
      <span
        class="fragment custom cover-title-step cover-title-step-good"
        data-fragment-index="0"
        aria-hidden="true"
      ></span>
      <span
        class="fragment custom cover-title-step cover-title-step-final"
        data-fragment-index="1"
        aria-hidden="true"
      ></span>
      <p class="cover-title-bridge" aria-hidden="true">
        <span class="cover-title-ai">AI</span>
        <em class="cover-title-good">for Good</em>
      </p>
      <div class="cover-title-final">
        <div class="cover-title-copy">
          <h1 class="cover-title-main">让我们自由自在地并发</h1>
          <p class="cover-title-subtitle">
            对并发运行时、数据共享边界与结构化并发范式演进的系统性探讨
          </p>
        </div>
        <p class="cover-title-byline">
          <span class="cover-title-author">王宏府</span>
          <span class="cover-title-role">语言与文字工作者</span>
        </p>
      </div>
    </div>
    """)
    return


@app.cell(hide_code=True)
def chapter_one_eva(mo):
    eva_not_armor = mo.image(
        "public/eva_not_armor_large.png",
        alt="EVA 原图：没错，那不是装甲",
    )
    eva_restraint = mo.image(
        "public/eva_restraint_large.png",
        alt="EVA 原图：是我们为了压制 EVA 本来力量所安装的拘束器",
    )
    not_restraint = mo.image(
        "public/python_not_restraint.png",
        alt="EVA 梗图：没错，那不是拘束器",
    )
    armor = mo.image(
        "public/python_armor.png",
        alt="EVA 梗图：是我们为了保护 Python 所安装的装甲",
    )
    mo.Html(f"""
    <div class="eva-sequence r-stack">
      <div class="eva-pair fragment fade-out" data-fragment-index="0">
        {eva_not_armor}
        {eva_restraint}
      </div>
      <div class="eva-pair fragment" data-fragment-index="0">
        {not_restraint}
        {armor}
      </div>
    </div>
    """)
    return


@app.cell(hide_code=True)
def chapter_one_timeline_image(candidate_slide):
    candidate_slide("01-timeline", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_transition_two(chapter_transition):
    chapter_transition(2)
    return


@app.cell(hide_code=True)
def chapter_two_timeline_image(candidate_slide):
    candidate_slide("02-timeline", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_two_pause(candidate_slide):
    candidate_slide("02-01-pause")
    return


@app.cell(hide_code=True)
def chapter_two_wait(candidate_slide):
    candidate_slide("02-02-wait")
    return


@app.cell(hide_code=True)
def chapter_two_ownership(candidate_slide):
    candidate_slide("02-03-ownership")
    return


@app.cell(hide_code=True)
def chapter_two_taskgroup(candidate_slide):
    candidate_slide("02-04-taskgroup")
    return


@app.cell(hide_code=True)
def chapter_two_structure(candidate_slide):
    candidate_slide("02-05-structure")
    return


@app.cell(hide_code=True)
def chapter_transition_three(chapter_transition):
    chapter_transition(3)
    return


@app.cell(hide_code=True)
def chapter_three_timeline_image(candidate_slide):
    candidate_slide("03-timeline", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_three_processes(candidate_slide):
    candidate_slide("03-01-processes")
    return


@app.cell(hide_code=True)
def chapter_three_interpreters(candidate_slide):
    candidate_slide("03-02-interpreters")
    return


@app.cell(hide_code=True)
def chapter_three_interpreter_state(candidate_slide):
    candidate_slide("03-02a-interpreter-state", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_three_interpreter_transfer(candidate_slide):
    candidate_slide("03-02b-interpreter-transfer", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_three_threads(candidate_slide):
    candidate_slide("03-03-threads")
    return


@app.cell(hide_code=True)
def chapter_three_parallel(candidate_slide):
    candidate_slide("03-04-parallel")
    return


@app.cell(hide_code=True)
def chapter_transition_four(chapter_transition):
    chapter_transition(4)
    return


@app.cell(hide_code=True)
def chapter_four_timeline_image(candidate_slide):
    candidate_slide("04-timeline", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_boundaries(candidate_slide):
    candidate_slide("04-01-boundaries")
    return


@app.cell(hide_code=True)
def chapter_four_local(candidate_slide):
    candidate_slide("04-01a-local", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_transfer(candidate_slide):
    candidate_slide("04-01b-transfer", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_immutable(candidate_slide):
    candidate_slide("04-01c-immutable", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_race(candidate_slide):
    candidate_slide("04-02-race")
    return


@app.cell(hide_code=True)
def chapter_four_protection(candidate_slide):
    candidate_slide("04-03-protection")
    return


@app.cell(hide_code=True)
def chapter_four_refcounts(candidate_slide):
    candidate_slide("04-04-refcounts")
    return


@app.cell(hide_code=True)
def chapter_four_biased_counting(candidate_slide):
    candidate_slide("04-04a-biased-counting", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_deferred_counting(candidate_slide):
    candidate_slide("04-04b-deferred-counting", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_memory_gc(candidate_slide):
    candidate_slide("04-05-memory-gc")
    return


@app.cell(hide_code=True)
def chapter_four_gc_heap(candidate_slide):
    candidate_slide("04-05a-gc-heap", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_gc_cycle(candidate_slide):
    candidate_slide("04-05b-gc-cycle", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_four_containers(candidate_slide):
    candidate_slide("04-06-containers")
    return


@app.cell(hide_code=True)
def chapter_four_extensions(candidate_slide):
    candidate_slide("04-07-extensions")
    return


@app.cell(hide_code=True)
def chapter_four_lock(candidate_slide):
    candidate_slide("04-08-lock")
    return


@app.cell(hide_code=True)
def chapter_four_state(candidate_slide):
    candidate_slide("04-09-state")
    return


@app.cell(hide_code=True)
def chapter_five_timeline_summary_image(candidate_slide):
    candidate_slide("05-timeline-summary", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_five_timeline_outlook_image(candidate_slide):
    candidate_slide("05-timeline-outlook", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_five_summary(final_summary_header, mo):
    summary_picture = mo.image(
        "public/illustrations/05-summary.png",
        alt="三项局部责任并列：任务结构负责收尾，执行模型安排执行位置，状态模型明确访问与修改边界。",
    )
    mo.Html(f"""
    <div class="final-summary" role="region" aria-label="总结与展望：自由之后">
      {final_summary_header}
      <div class="final-summary-stage">
        <h2>局部结构，接手保护责任</h2>
        <figure class="final-summary-visual">{summary_picture}</figure>
        <p class="final-summary-caption">任务的生命周期 · 执行位置 · 状态关系</p>
      </div>
    </div>
    """)
    return


@app.cell(hide_code=True)
def chapter_five_outlook(final_summary_header, mo):
    outlook_picture = mo.image(
        "public/illustrations/05-outlook.png",
        alt="开放问题：把任务归属、资源需求和执行位置显式交给运行时，只在相关工作之间保留必要顺序。",
    )
    mo.Html(f"""
    <div class="final-summary" role="region" aria-label="总结与展望：自由之后">
      {final_summary_header}
      <div class="final-summary-stage">
        <h2>让关系进入运行时？</h2>
        <figure class="final-summary-visual">{outlook_picture}</figure>
        <p class="final-summary-caption">开放探索 · 尚非 CPython 已确定的统一路线</p>
      </div>
    </div>
    """)
    return


@app.cell(hide_code=True)
def chapter_five_manual_state(candidate_slide):
    candidate_slide("05-01-manual-state", variant="辅助图")
    return


@app.cell(hide_code=True)
def chapter_five_bocpy(candidate_slide):
    candidate_slide("05-02-bocpy", variant="辅助图")
    return


@app.cell(hide_code=True)
def collaboration_thanks(mo):
    qr_code = mo.image(
        "public/blog-qr.svg",
        alt="博客二维码：https://blog.wh2099.com",
    )
    thanks_player = mo.audio("public/ai.flac")
    thanks_player = mo.Html(
        thanks_player.text.replace(
            "<audio ",
            '<audio class="thanks-player" preload="metadata" '
            'aria-label="答谢页音乐：小虎队《爱》" ',
            1,
        )
    )
    music_clock = mo.iframe(
        """
        <script>
        const initFrame = parent.requestAnimationFrame(() => {
          const root = frameElement?.closest(".thanks");
          const slide = root?.closest("section");
          const audio = root?.querySelector(".thanks-player");
          if (!root || !slide || !audio) return;

          let timer = 0;
          let active = false;
          const reset = () => {
            if (timer) clearTimeout(timer);
            timer = 0;
            audio.pause();
            audio.currentTime = 0;
          };
          const cancelTimer = () => {
            if (timer) clearTimeout(timer);
            timer = 0;
          };
          const handleSpace = (event) => {
            if (
              event.code !== "Space"
              || event.altKey
              || event.ctrlKey
              || event.metaKey
              || event.shiftKey
              || !slide.classList.contains("present")
            ) return;

            event.preventDefault();
            event.stopImmediatePropagation();
            if (event.repeat) return;
            cancelTimer();
            audio.pause();
          };
          const update = () => {
            const present = slide.classList.contains("present");
            if (present === active) return;
            active = present;
            if (!active) {
              reset();
              return;
            }
            reset();
            audio.volume = 0.1;
            timer = setTimeout(() => {
              timer = 0;
              if (!slide.classList.contains("present")) return;
              void audio.play().catch(() => {});
            }, 5000);
          };

          const observer = new MutationObserver(update);
          observer.observe(slide, { attributeFilter: ["class"] });
          audio.addEventListener("play", cancelTimer);
          parent.document.addEventListener("keydown", handleSpace, true);
          update();
          addEventListener("unload", () => {
            observer.disconnect();
            audio.removeEventListener("play", cancelTimer);
            parent.document.removeEventListener("keydown", handleSpace, true);
            reset();
          }, { once: true });
        });
        addEventListener("unload", () => {
          parent.cancelAnimationFrame(initFrame);
        }, { once: true });
        </script>
        """,
        width="0",
        height="0",
    )
    music_clock = mo.Html(
        music_clock.text.replace(
            "<iframe ",
            '<iframe allow="autoplay" aria-hidden="true" tabindex="-1" ',
            1,
        )
    )
    mo.Html(f"""
    <div class="thanks">
      <div class="thanks-copy" role="group" aria-labelledby="thanks-title">
        <p class="thanks-kicker">感谢聆听</p>
        <div class="thanks-conclusion">
          <h1 class="thanks-title" id="thanks-title">
            <span>让我们</span>
            <span>自由自在地并发</span>
          </h1>
        </div>
      </div>
      <a
        class="thanks-qr"
        href="https://blog.wh2099.com"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="访问博客：blog.wh2099.com"
      >
        <span class="thanks-qr-image">{qr_code}</span>
        <span class="thanks-url">blog.wh2099.com</span>
      </a>
      <div class="thanks-audio">{thanks_player}</div>
      {music_clock}
    </div>
    """)
    return


if __name__ == "__main__":
    app.run()
