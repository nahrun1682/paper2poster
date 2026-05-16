import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".codex/skills/poster-layout-extractor/scripts/extract-layout.py"
SAMPLE_PPTX = ROOT / "templates/powerpoint/research_template.pptx"


class PosterLayoutExtractorTest(unittest.TestCase):
    def test_extracts_layout_json_and_html_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(SAMPLE_PPTX), str(output_dir)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            layout_path = output_dir / "layout.json"
            report_path = output_dir / "extraction-report.json"
            template_path = output_dir / "poster-template.html"
            preview_path = output_dir / "preview.html"

            self.assertTrue(layout_path.exists())
            self.assertTrue(report_path.exists())
            self.assertTrue(template_path.exists())
            self.assertTrue(preview_path.exists())

            layout = json.loads(layout_path.read_text(encoding="utf-8"))
            self.assertEqual(layout["source"], str(SAMPLE_PPTX))
            self.assertEqual(layout["slide_count"], 1)
            self.assertGreater(layout["slide"]["width"], 0)
            self.assertGreater(layout["slide"]["height"], 0)
            self.assertGreater(len(layout["shapes"]), 0)

            first_shape = layout["shapes"][0]
            self.assertIn(first_shape["kind"], {"text", "shape", "image", "table", "unknown"})
            self.assertRegex(first_shape["placeholder"], r"^\{\{shape_\d{2}\}\}$")
            for key in ("left_pct", "top_pct", "width_pct", "height_pct"):
                self.assertGreaterEqual(first_shape[key], 0)
                self.assertLessEqual(first_shape[key], 100)

            text_shape = next(shape for shape in layout["shapes"] if shape["kind"] == "text")
            self.assertGreater(text_shape["font_size_pt"], 0)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["text_integrity"]["missing_in_preview"], [])
            self.assertEqual(report["text_integrity"]["extracted_text_shapes"], 18)
            self.assertIn("研究タイトル（日本語）", report["text_integrity"]["preview_text"])
            self.assertNotIn("functionfitPosterText", report["text_integrity"]["preview_text"])

            html = template_path.read_text(encoding="utf-8")
            preview_html = preview_path.read_text(encoding="utf-8")
            self.assertIn("poster-canvas", html)
            self.assertIn("position: absolute", html)
            self.assertIn(first_shape["placeholder"], html)
            self.assertIn("background:transparent", html)
            self.assertIn("font-size:clamp", html)
            self.assertNotIn(">\n        【概要リード文】", preview_html)
            self.assertNotIn(">\n        課題①", preview_html)
            self.assertIn(">【概要リード文】", preview_html)
            self.assertIn(">課題①", preview_html)
            self.assertIn("font-size:clamp(4px, 1.8519cqw, 24.0px)", preview_html)
            self.assertIn("poster-element text poster-title shape_02", preview_html)
            self.assertIn("font-size:clamp(4px, 4.3981cqw, 57.0px)", preview_html)
            self.assertIn("poster-element text section-heading shape_09", preview_html)
            self.assertIn("font-size:clamp(4px, 2.963cqw, 38.4px)", preview_html)
            self.assertIn("font-weight: 700", preview_html)
            self.assertIn(
                '.poster-element.text:not(.poster-title):not(.section-heading)',
                preview_html,
            )
            self.assertIn("element.scrollHeight > element.clientHeight", preview_html)
            self.assertNotIn("element.scrollWidth > element.clientWidth", preview_html)
            self.assertIn("document.fonts.ready", preview_html)
            self.assertIn("const minSize = 10", preview_html)
            self.assertIn("function fitPosterText", html)
            self.assertIn('<html lang="ja">', preview_html)
            self.assertIn('"IPAPGothic"', preview_html)


if __name__ == "__main__":
    unittest.main()
