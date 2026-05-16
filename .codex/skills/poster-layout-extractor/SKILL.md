---
name: poster-layout-extractor
description: Use when converting a single-slide PPTX poster, research poster, or layout-heavy PowerPoint template into an HTML template while preserving approximate element placement.
---

# Poster Layout Extractor

## Purpose

Use this skill to turn a one-slide PPTX poster/template into a reusable HTML layout draft. The goal is placement fidelity, not a perfect PowerPoint renderer.

## Scope

Extract:
- slide size and aspect ratio
- text boxes, shapes, tables, and pictures
- left/top/width/height as percentages
- text content and generated placeholders
- best-effort solid fill, line, and text colors

Do not promise exact reproduction of gradients, shadows, theme colors, animations, grouped-shape transforms, or font rendering.

## Workflow

1. Confirm the input is a `.pptx` file and that the expected target is a one-slide poster/template.
2. Choose an output directory. Prefer a throwaway directory first, such as `.codex-output/poster-layout/<name>/`.
3. Run the bundled script from the repository root:

   ```bash
   python .codex/skills/poster-layout-extractor/scripts/extract-layout.py <input.pptx> <output_dir>
   ```

4. Inspect `<output_dir>/layout.json` and `<output_dir>/extraction-report.json`.
5. Summarize for the user:
   - slide dimensions and shape count
   - text/image/table counts
   - whether `text_integrity.missing_in_preview` is empty
   - large regions that likely correspond to poster sections
   - any extraction limitations or unsupported styling
6. Point the user to:
   - `<output_dir>/preview.html` for visual placement review
   - `<output_dir>/poster-template.html` for placeholder-based editing
7. Ask which generated placeholders should be renamed to domain fields such as `title`, `background`, `method`, `findings`, or `diagram`.

## Outputs

The script creates:

- `layout.json`: machine-readable layout data
- `extraction-report.json`: text-integrity and shape-count checks
- `poster-template.html`: HTML template with `{{shape_XX}}` placeholders
- `preview.html`: same layout populated with extracted text and images where available
- `assets/`: copied image assets, if the PPTX contains pictures

## Review Checklist

Before reporting results, verify:

- `layout.json` exists and has exactly one slide
- `extraction-report.json` reports no `missing_in_preview` text
- generated HTML contains `.poster-canvas` and absolutely positioned `.poster-element` blocks
- visible text boxes have corresponding placeholders
- images referenced in `preview.html` exist under `assets/`
- the user understands colors are best-effort only

If the PPTX has multiple slides, stop after extraction and explain that this skill is currently intended for one-slide poster templates.
