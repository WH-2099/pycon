import json
import tomllib
from html import escape
from pathlib import Path

import marimo as mo

ROOT = Path(__file__).parent
SLIDES = tomllib.loads((ROOT / "slide_assets/chapters.toml").read_text())["slides"]
TIMELINES = tomllib.loads((ROOT / "slide_assets/timelines.toml").read_text())["slides"]
SLIDES.update(TIMELINES)


def slide_diagram(source: str, font_size: int = 32) -> mo.Html:
    theme = json.dumps({
        "fontFamily": "PyCon Sans, sans-serif",
        "fontSize": f"{font_size}px",
        "primaryColor": "#eef8ff",
        "primaryTextColor": "#172033",
        "primaryBorderColor": "#087fbd",
        "lineColor": "#64748b",
        "secondaryColor": "#fff4e6",
        "tertiaryColor": "#f8fafc",
        "edgeLabelBackground": "#ffffff",
        "noteBkgColor": "#edf3f7",
        "noteBorderColor": "#bccdd8",
        "noteTextColor": "#172033",
    })
    return mo.mermaid(
        "---\nconfig:\n  theme: base\n"
        f"  themeVariables: {theme}\n"
        "  flowchart:\n    padding: 18\n    nodeSpacing: 28\n    rankSpacing: 36\n"
        "    wrappingWidth: 320\n    subGraphTitleMargin: {top: 12, bottom: 24}\n"
        "  block:\n    padding: 24\n"
        "  sequence:\n    mirrorActors: false\n    fontSize: 28\n"
        "    messageMargin: 18\n    diagramMarginX: 12\n"
        f"---\n{source}",
        theme="base",
    )


def candidate_slide(slide_id: str, variant: str | None = None) -> mo.Html:  # ruff: ignore[too-many-locals]
    slide = SLIDES[slide_id]
    picture = mo.image(ROOT / f"public/illustrations/{slide_id}.png", alt=slide["alt"])
    variants = {
        "辅助图": mo.Html(f'<figure class="candidate-visual">{picture}</figure>'),
    }
    code_size = 32.0
    if "code" in slide:
        code = mo.md(f"```{slide['language']}\n{slide['code']}\n```")
        variants["代码"] = mo.Html(
            f'<div class="candidate-code">{code.text}</div>'
            f'<p class="candidate-kind">{escape(slide["code_kind"])}</p>'
        )
        lines = slide["code"].splitlines()
        columns = max(sum(1 if c.isascii() else 2 for c in line) for line in lines)
        code_size = min(40, 440 / len(lines), 2200 / columns)
    if "mermaid" in slide:
        diagram = slide_diagram(slide["mermaid"])
        variants["Mermaid"] = mo.Html(
            '<figure class="candidate-visual" role="img" '
            f'aria-label="{escape(slide["diagram_reason"])}">{diagram}</figure>'
        )
    if variant is not None:
        variants = {variant: variants[variant]}
    if len(variants) == 1:
        variant = next(iter(variants))
    panels = []
    for index, (name, body) in enumerate(variants.items()):
        attributes = 'class="candidate-panel"'
        if len(variants) > 1:
            effect = (
                "fade-out"
                if index == 0
                else "current-visible"
                if index < len(variants) - 1
                else ""
            )
            attributes = (
                f'class="candidate-panel fragment {effect}" '
                f'data-fragment-index="{max(0, index - 1)}"'
            )
        panels.append(f'<div {attributes} data-variant="{name}">{body.text}</div>')
    content = f'<div class="candidate-panels">{"".join(panels)}</div>'
    notes = mo.md(
        f"{slide['notes']}\n\n图型选择: {slide['diagram_reason']}\n\n"
        + "\n".join(f"- [来源 {i}]({url})" for i, url in enumerate(slide["sources"], 1))
    )
    portrait = slide.get("mermaid", "").startswith("sequenceDiagram")
    layout = (
        "timeline" if slide_id in TIMELINES else "portrait" if portrait else "landscape"
    )
    section, _, topic = slide["section"].partition(" · ")[2].partition(" · ")
    section = section.partition("、")[2] or section
    if slide_id in TIMELINES:
        section = slide["section"]
    section_label = " / ".join(
        f"<span>{escape(word)}</span>" for word in section.split(" / ")
    )
    topic_label = f"<small>{escape(topic)}</small>" if topic else ""
    title = "，</span><span>".join(escape(slide["title"]).split("，"))
    takeaway = (
        escape(slide["takeaway"])
        .replace("，", "，</span><span>")
        .replace("、", "、</span><span>")
    )
    return mo.Html(f"""
    <article class="candidate-slide" data-candidate-id="{escape(slide_id)}"
      data-diagram-layout="{layout}"
      data-fixed-variant="{escape(variant or "")}"
      style="--candidate-code-size: {code_size:.1f}px">
      <h1 class="candidate-section" aria-label="{escape(slide["section"])}">
        {section_label}{topic_label}
      </h1>
      <header>
        <h2><span>{title}</span></h2>
        <p class="candidate-takeaway"><span>{takeaway}</span></p>
      </header>
      <div class="candidate-stage">{content}</div>
      <footer>{escape(slide["status"])}</footer>
      <aside class="notes">核验日期: 2026-09-04。{notes.text}</aside>
    </article>
    """)
