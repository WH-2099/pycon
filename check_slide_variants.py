import ast
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from tempfile import TemporaryDirectory

from slide_variants import candidate_slide

ROOT = Path(__file__).parent
EXPECTED = {
    "02-01-pause": "READY\nHELLO\nclosed",
    "02-02-wait": "waiting\nother work\nresumed",
    "02-03-ownership": "response\nlog written",
    "02-04-taskgroup": "cleaned\n1",
    "02-05-structure": "('profile', 'body', 'comments')",
    "03-01-processes": "[332833500, 2664667000]",
    "03-02-interpreters": "[332833500, 2664667000]",
    "03-03-threads": "[332833500, 2664667000]",
    "04-01-boundaries": "('count', 1)",
    "04-08-lock": "one cached object",
}


def check_segments(
    slide_id: str, slide: dict[str, object], variant: str | None
) -> None:
    expected = ["辅助图"]
    if "code" in slide:
        expected.append("代码")
    if "mermaid" in slide:
        expected.append("Mermaid")
    if variant is not None:
        expected = [variant]
    rendered = candidate_slide(slide_id, variant=variant).text
    assert re.findall(r'data-variant="([^"]+)"', rendered) == expected, slide_id
    assert ('data-fragment-index="' in rendered) == (len(expected) > 1), slide_id
    assert 'type="radio"' not in rendered, slide_id


def check() -> None:
    slides = tomllib.loads((ROOT / "slide_assets/chapters.toml").read_text())["slides"]
    prompts = json.loads((ROOT / "slide_assets/prompts.json").read_text())
    timelines = tomllib.loads((ROOT / "slide_assets/timelines.toml").read_text())[
        "slides"
    ]
    notebook = ast.parse((ROOT / "slides.py").read_text())
    embedded = [
        node.args[0].value
        for node in ast.walk(notebook)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "candidate_slide"
        and isinstance(node.args[0], ast.Constant)
    ]
    assert [key for key in embedded if key not in timelines] == list(slides), (
        "Missing, duplicated, or reordered content slides"
    )
    fixed_calls = [
        (node.args[0].value, node.keywords[0].value.value)
        for node in ast.walk(notebook)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "candidate_slide"
        and isinstance(node.args[0], ast.Constant)
        and node.keywords
        and isinstance(node.keywords[0].value, ast.Constant)
        and isinstance(node.keywords[0].value.value, str)
    ]
    assert [call for call in fixed_calls if call[0] in timelines] == [
        (key, "辅助图") for key in timelines
    ], "Every timeline must display its illustration once, in order"
    cells = [node.name for node in notebook.body if isinstance(node, ast.FunctionDef)]
    outlook = cells.index("chapter_five_outlook")
    assert cells[outlook : outlook + 4] == [
        "chapter_five_outlook",
        "chapter_five_manual_state",
        "chapter_five_bocpy",
        "collaboration_thanks",
    ], "Show manual coordination before the single combined bocpy page"
    for anchor, prefix, following in (
        ("chapter_one_eva", "chapter_one_timeline", "chapter_transition_two"),
        ("chapter_transition_two", "chapter_two_timeline", "chapter_two_pause"),
        (
            "chapter_transition_three",
            "chapter_three_timeline",
            "chapter_three_processes",
        ),
        ("chapter_transition_four", "chapter_four_timeline", "chapter_four_boundaries"),
        (
            "chapter_four_state",
            "chapter_five_timeline_summary",
            "chapter_five_timeline_outlook_image",
        ),
        (
            "chapter_five_timeline_summary_image",
            "chapter_five_timeline_outlook",
            "chapter_five_summary",
        ),
    ):
        start = cells.index(anchor)
        assert cells[start : start + 3] == [
            anchor,
            f"{prefix}_image",
            following,
        ], prefix
    assert all("mermaid" not in slide for slide in timelines.values()), (
        "Timelines must not retain unused Mermaid variants"
    )
    slides.update(timelines)
    assert all(
        "mermaid" not in slides[key] and "code" not in slides[key]
        for key, variant in fixed_calls
        if variant == "辅助图"
    ), "Fixed illustration pages must not retain unused formats"
    image_ids = set(slides) | {
        "index-organization",
        "index-parallel",
        "index-state",
        "05-summary",
        "05-outlook",
    }
    assert len(prompts) == len(image_ids)
    assert {item["id"] for item in prompts} == image_ids
    assert {
        path.stem for path in (ROOT / "public/illustrations").glob("*.png")
    } == image_ids
    for item in prompts:
        image = ROOT / f"public/illustrations/{item['id']}.png"
        assert item["asset"] == image.relative_to(ROOT).as_posix()
        assert item["prompt"] and item["tool"] and item["generated_on"]
        assert hashlib.sha256(image.read_bytes()).hexdigest() == item["sha256"], item[
            "id"
        ]
    fixed_variants = dict(fixed_calls)
    with TemporaryDirectory(prefix="pycon-slide-examples-") as temporary:
        for slide_id, slide in slides.items():
            image = ROOT / f"public/illustrations/{slide_id}.png"
            assert image.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", slide_id
            assert slide["sources"] and slide["notes"], slide_id
            check_segments(slide_id, slide, fixed_variants.get(slide_id))
            if not slide.get("run"):
                continue
            script = Path(temporary, slide_id.replace("-", "_") + ".py")
            script.write_text(slide["code"], encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script)],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if slide.get("requires") == "free-threaded" and sys._is_gil_enabled():
                assert result.returncode == 1 and "GIL" in result.stderr, slide_id
                continue
            assert result.returncode == 0, (slide_id, result.stderr)
            if slide_id == "04-02-race":
                assert result.stdout.startswith("['built', 'built']"), result.stdout
            else:
                assert result.stdout.strip() == EXPECTED[slide_id], slide_id


if __name__ == "__main__":
    check()
