#!/usr/bin/env python3
"""Extract approximate layout from a single-slide PPTX poster.

The script intentionally uses only the Python standard library. It reads the
PowerPoint OOXML package, extracts shape coordinates, emits a layout JSON file,
and generates two HTML files: one with placeholders and one preview.
"""

from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

EMU_PER_INCH = 914400
FONT_SIZE_SCALE = 1.0
TITLE_FONT_SIZE_SCALE = 1.25
SECTION_HEADER_FONT_SIZE_SCALE = 1.6
FONT_SIZE_MAX_PX_PER_PT = 2.4
SECTION_HEADER_TEXTS = {
    "対応する課題",
    "提供する価値",
    "概要",
    "適用分野・事業機会",
    "適用分野・事業課題",
    "現況と予定",
    "討論事項",
}


@dataclass
class SlideSize:
    width: int
    height: int


def qn(namespace: str, name: str) -> str:
    return f"{{{NS[namespace]}}}{name}"


def read_xml(package: zipfile.ZipFile, path: str) -> ET.Element:
    return ET.fromstring(package.read(path))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def pct(value: int | None, total: int) -> float:
    if value is None or total == 0:
        return 0.0
    return round((value / total) * 100, 4)


def emu_to_inches(value: int) -> float:
    return round(value / EMU_PER_INCH, 3)


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def get_slide_size(package: zipfile.ZipFile) -> SlideSize:
    presentation = read_xml(package, "ppt/presentation.xml")
    size = presentation.find("p:sldSz", NS)
    if size is None:
        raise ValueError("Could not find ppt/presentation.xml p:sldSz")
    width = parse_int(size.get("cx"))
    height = parse_int(size.get("cy"))
    if not width or not height:
        raise ValueError("Slide size is missing cx/cy")
    return SlideSize(width=width, height=height)


def get_slide_paths(package: zipfile.ZipFile) -> list[str]:
    paths = [
        name
        for name in package.namelist()
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
    ]
    return sorted(paths, key=lambda path: int(re.search(r"slide(\d+)\.xml", path).group(1)))


def get_relationships(package: zipfile.ZipFile, slide_path: str) -> dict[str, str]:
    slide_name = posixpath.basename(slide_path)
    rels_path = f"ppt/slides/_rels/{slide_name}.rels"
    if rels_path not in package.namelist():
        return {}

    root = read_xml(package, rels_path)
    rels: dict[str, str] = {}
    for rel in root.findall("rel:Relationship", NS):
        rel_id = rel.get("Id")
        target = rel.get("Target")
        if not rel_id or not target:
            continue
        rels[rel_id] = posixpath.normpath(posixpath.join("ppt/slides", target))
    return rels


def get_transform(element: ET.Element) -> dict[str, int]:
    xfrm = element.find(".//a:xfrm", NS)
    if xfrm is None:
        return {"left": 0, "top": 0, "width": 0, "height": 0}

    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    return {
        "left": parse_int(off.get("x") if off is not None else None) or 0,
        "top": parse_int(off.get("y") if off is not None else None) or 0,
        "width": parse_int(ext.get("cx") if ext is not None else None) or 0,
        "height": parse_int(ext.get("cy") if ext is not None else None) or 0,
    }


def text_content(element: ET.Element) -> str:
    paragraphs = []
    for paragraph in element.findall(".//a:p", NS):
        parts = [node.text or "" for node in paragraph.findall(".//a:t", NS)]
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)
    text = "\n".join(paragraphs)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def solid_color(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    color = element.find(".//a:srgbClr", NS)
    if color is not None and color.get("val"):
        return f"#{color.get('val')}"
    color = element.find(".//a:schemeClr", NS)
    if color is not None and color.get("val"):
        return f"theme:{color.get('val')}"
    return None


def get_style(element: ET.Element) -> dict[str, str | None]:
    shape_props = element.find("p:spPr", NS) or element.find("p:pic/p:spPr", NS)
    fill = solid_color(shape_props.find("a:solidFill", NS) if shape_props is not None else None)
    line = solid_color(shape_props.find("a:ln/a:solidFill", NS) if shape_props is not None else None)
    text_color = solid_color(element.find(".//a:rPr/a:solidFill", NS))
    return {
        "fill": fill,
        "line": line,
        "text": text_color,
    }


def get_font_size_pt(element: ET.Element) -> float | None:
    sizes = []
    for run_props in element.findall(".//a:rPr", NS):
        size = parse_int(run_props.get("sz"))
        if size:
            sizes.append(size / 100)
    if not sizes:
        return None
    return round(sum(sizes) / len(sizes), 2)


def shape_name(element: ET.Element) -> tuple[str | None, str | None]:
    c_nv_pr = element.find(".//p:cNvPr", NS)
    if c_nv_pr is None:
        return None, None
    return c_nv_pr.get("id"), c_nv_pr.get("name")


def copy_image(
    package: zipfile.ZipFile,
    rels: dict[str, str],
    element: ET.Element,
    assets_dir: Path,
    index: int,
) -> str | None:
    blip = element.find(".//a:blip", NS)
    if blip is None:
        return None
    rel_id = blip.get(qn("r", "embed"))
    if not rel_id or rel_id not in rels:
        return None
    source = rels[rel_id]
    if source not in package.namelist():
        return None
    suffix = Path(source).suffix or ".bin"
    output_name = f"image_{index:02d}{suffix}"
    output_path = assets_dir / output_name
    output_path.write_bytes(package.read(source))
    return f"assets/{output_name}"


def iter_layout_elements(root: ET.Element) -> Iterable[ET.Element]:
    sp_tree = root.find(".//p:spTree", NS)
    if sp_tree is None:
        return []
    return [
        child
        for child in list(sp_tree)
        if local_name(child.tag) in {"sp", "pic", "graphicFrame"}
    ]


def classify(element: ET.Element) -> str:
    tag = local_name(element.tag)
    if tag == "pic":
        return "image"
    if tag == "graphicFrame":
        if element.find(".//a:tbl", NS) is not None:
            return "table"
        return "unknown"
    if text_content(element):
        return "text"
    return "shape"


def extract_layout(input_pptx: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets"
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(input_pptx) as package:
        slide_paths = get_slide_paths(package)
        if not slide_paths:
            raise ValueError("No slides found in PPTX")
        slide_size = get_slide_size(package)
        slide_path = slide_paths[0]
        slide_root = read_xml(package, slide_path)
        rels = get_relationships(package, slide_path)

        shapes = []
        image_index = 1
        for index, element in enumerate(iter_layout_elements(slide_root), start=1):
            transform = get_transform(element)
            kind = classify(element)
            source_id, name = shape_name(element)
            placeholder = f"{{{{shape_{index:02d}}}}}"
            image_path = None
            if kind == "image":
                image_path = copy_image(package, rels, element, assets_dir, image_index)
                image_index += 1

            shape = {
                "id": f"shape_{index:02d}",
                "source_id": source_id,
                "name": name,
                "kind": kind,
                "text": text_content(element),
                "placeholder": placeholder,
                "left": transform["left"],
                "top": transform["top"],
                "width": transform["width"],
                "height": transform["height"],
                "left_pct": pct(transform["left"], slide_size.width),
                "top_pct": pct(transform["top"], slide_size.height),
                "width_pct": pct(transform["width"], slide_size.width),
                "height_pct": pct(transform["height"], slide_size.height),
                "image_path": image_path,
                "style": get_style(element),
                "font_size_pt": get_font_size_pt(element),
            }
            shapes.append(shape)

    layout = {
        "source": str(input_pptx),
        "slide_count": len(slide_paths),
        "slide": {
            "width": slide_size.width,
            "height": slide_size.height,
            "width_inches": emu_to_inches(slide_size.width),
            "height_inches": emu_to_inches(slide_size.height),
            "aspect_ratio": round(slide_size.width / slide_size.height, 6),
        },
        "shapes": shapes,
        "limitations": [
            "Only the first slide is converted.",
            "Solid colors are extracted on a best-effort basis.",
            "Gradients, shadows, animations, and exact theme rendering are not reproduced.",
            "Grouped-shape transforms may need manual adjustment.",
        ],
    }
    return layout


def css_color(value: str | None, fallback: str) -> str:
    if not value or value.startswith("theme:"):
        return fallback
    return value


def normalized_heading_text(value: str) -> str:
    return re.sub(r"\s+", "", value)


def is_section_heading(shape: dict) -> bool:
    return (
        shape.get("kind") == "text"
        and normalized_heading_text(shape.get("text") or "") in SECTION_HEADER_TEXTS
    )


def is_poster_title(shape: dict) -> bool:
    return (
        shape.get("kind") == "text"
        and (shape.get("font_size_pt") or 0) >= 16
        and (shape.get("top_pct") or 0) < 10
    )


def font_size_css(shape: dict, slide: dict) -> str:
    size_pt = shape.get("font_size_pt")
    if not size_pt:
        return "clamp(4px, 1.2cqw, 18px)"
    scale = FONT_SIZE_SCALE
    if is_poster_title(shape):
        scale *= TITLE_FONT_SIZE_SCALE
    elif is_section_heading(shape):
        scale *= SECTION_HEADER_FONT_SIZE_SCALE
    # 1pt = 1/72in. cqw is 1% of the rendered poster width.
    preferred = round((size_pt / 72) / slide["width_inches"] * 100 * scale, 4)
    maximum = max(8, round(size_pt * FONT_SIZE_MAX_PX_PER_PT * scale, 2))
    return f"clamp(4px, {preferred}cqw, {maximum}px)"


def element_style(shape: dict, slide: dict) -> str:
    style = shape["style"]
    if shape["kind"] == "text":
        fill = css_color(style.get("fill"), "transparent")
        line = css_color(style.get("line"), "transparent")
    else:
        fill = css_color(style.get("fill"), "transparent")
        line = css_color(style.get("line"), "rgba(17, 24, 39, 0.28)")
    text = css_color(style.get("text"), "#111827")
    style_text = (
        f"left:{shape['left_pct']}%;"
        f"top:{shape['top_pct']}%;"
        f"width:{shape['width_pct']}%;"
        f"height:{shape['height_pct']}%;"
        f"background:{fill};"
        f"border-color:{line};"
        f"color:{text};"
        f"font-size:{font_size_css(shape, slide)};"
    )
    if is_poster_title(shape):
        style_text += "font-weight:700;"
    elif is_section_heading(shape):
        style_text += "font-weight:700;"
    return style_text


def render_shape(shape: dict, slide: dict, preview: bool) -> str:
    content = shape["placeholder"] if shape["kind"] in {"text", "table", "image"} else ""
    classes = f"poster-element {shape['kind']} {shape['id']}"
    if is_poster_title(shape):
        classes = f"poster-element {shape['kind']} poster-title {shape['id']}"
    elif is_section_heading(shape):
        classes = f"poster-element {shape['kind']} section-heading {shape['id']}"
    if preview:
        if shape["kind"] == "image" and shape.get("image_path"):
            content = f'<img src="{html.escape(shape["image_path"])}" alt="{html.escape(shape["name"] or shape["id"])}">'
        elif shape.get("text"):
            content = html.escape(shape["text"]).replace("\n", "<br>")
        else:
            content = ""
    else:
        content = html.escape(content)

    return (
        f'      <section class="{classes}" style="{element_style(shape, slide)}" '
        f'data-placeholder="{html.escape(shape["placeholder"])}">'
        f"{content}"
        "</section>"
    )


def render_html(layout: dict, preview: bool) -> str:
    title = "Poster Layout Preview" if preview else "Poster HTML Template"
    elements = "\n".join(
        render_shape(shape, layout["slide"], preview=preview)
        for shape in layout["shapes"]
    )
    aspect_ratio = layout["slide"]["aspect_ratio"]
    return f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #e5e7eb;
        color: #111827;
        font-family: "IPAPGothic", "IPA Pゴシック", "Noto Sans CJK JP", "Yu Gothic", "Hiragino Kaku Gothic ProN", Meiryo, ui-sans-serif, system-ui, sans-serif;
      }}

      .poster-canvas {{
        position: relative;
        container-type: inline-size;
        width: min(100vw, calc(100vh * {aspect_ratio}));
        aspect-ratio: {layout["slide"]["width"]} / {layout["slide"]["height"]};
        background: #f8fafc;
        box-shadow: 0 24px 80px rgba(15, 23, 42, 0.22);
        overflow: hidden;
      }}

      .poster-element {{
        position: absolute;
        overflow: hidden;
        border: 1px solid rgba(17, 24, 39, 0.28);
        padding: clamp(1px, 0.55cqw, 10px);
        line-height: 1.25;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
      }}

      .poster-element.image {{
        display: grid;
        place-items: center;
        padding: 0;
        background: transparent;
      }}

      .poster-element.section-heading {{
        display: flex;
        align-items: center;
        padding: 0 clamp(2px, 0.8cqw, 12px);
        line-height: 1;
        font-weight: 700;
      }}

      .poster-element.poster-title {{
        display: flex;
        align-items: center;
        padding: 0 clamp(2px, 0.65cqw, 10px);
        line-height: 1.05;
        font-weight: 700;
      }}

      .poster-element img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
      }}
    </style>
  </head>
  <body>
    <main class="poster-canvas" aria-label="{title}">
{elements}
    </main>
    <script>
      function fitPosterText() {{
        const elements = document.querySelectorAll(".poster-element.text:not(.poster-title):not(.section-heading)");
        for (const element of elements) {{
          const style = window.getComputedStyle(element);
          let size = parseFloat(style.fontSize);
          const minSize = 10;
          while (size > minSize && element.scrollHeight > element.clientHeight) {{
            size -= 0.5;
            element.style.fontSize = size + "px";
          }}
        }}
      }}

      window.addEventListener("load", () => {{
        if (document.fonts && document.fonts.ready) {{
          document.fonts.ready.then(fitPosterText);
        }} else {{
          fitPosterText();
        }}
      }});
      window.addEventListener("resize", fitPosterText);
    </script>
  </body>
</html>
"""


def normalize_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<script\b[^>]*>.*?</script>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<style\b[^>]*>.*?</style>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<br\\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", "", value)
    return value


def build_report(layout: dict, preview_html: str) -> dict:
    preview_text = normalize_text(preview_html)
    text_shapes = [shape for shape in layout["shapes"] if shape.get("text")]
    missing = []
    for shape in text_shapes:
        text = normalize_text(shape["text"])
        if text and text not in preview_text:
            missing.append(
                {
                    "id": shape["id"],
                    "name": shape["name"],
                    "text": shape["text"],
                }
            )

    return {
        "source": layout["source"],
        "slide_count": layout["slide_count"],
        "shape_count": len(layout["shapes"]),
        "kind_counts": {
            kind: sum(1 for shape in layout["shapes"] if shape["kind"] == kind)
            for kind in sorted({shape["kind"] for shape in layout["shapes"]})
        },
        "text_integrity": {
            "extracted_text_shapes": len(text_shapes),
            "missing_in_preview": missing,
            "preview_text": preview_text,
        },
        "warnings": layout["limitations"],
    }


def write_outputs(layout: dict, output_dir: Path) -> None:
    template_html = render_html(layout, preview=False)
    preview_html = render_html(layout, preview=True)
    report = build_report(layout, preview_html)

    (output_dir / "layout.json").write_text(
        json.dumps(layout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "poster-template.html").write_text(
        template_html,
        encoding="utf-8",
    )
    (output_dir / "preview.html").write_text(
        preview_html,
        encoding="utf-8",
    )
    (output_dir / "extraction-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pptx", type=Path)
    parser.add_argument("output_dir", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.input_pptx.exists():
        print(f"Input PPTX not found: {args.input_pptx}", file=sys.stderr)
        return 2
    if args.input_pptx.suffix.lower() != ".pptx":
        print(f"Input must be a .pptx file: {args.input_pptx}", file=sys.stderr)
        return 2

    try:
        layout = extract_layout(args.input_pptx, args.output_dir)
        write_outputs(layout, args.output_dir)
    except Exception as exc:
        print(f"Failed to extract layout: {exc}", file=sys.stderr)
        return 1

    counts = {}
    for shape in layout["shapes"]:
        counts[shape["kind"]] = counts.get(shape["kind"], 0) + 1
    print(f"Extracted {len(layout['shapes'])} shape(s) from {args.input_pptx}")
    print(f"Slide count: {layout['slide_count']} / converted first slide only")
    print("Kinds: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print(f"Wrote {args.output_dir / 'layout.json'}")
    print(f"Wrote {args.output_dir / 'extraction-report.json'}")
    print(f"Wrote {args.output_dir / 'poster-template.html'}")
    print(f"Wrote {args.output_dir / 'preview.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
