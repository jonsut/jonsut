from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "{http://www.w3.org/2000/svg}"
ACCESSIBLE_NAME = "Jon Sutton — Creativity + AI + Engineering"
POSITIONING_COPY = (
    "**A software engineer with roots in research, design and creative "
    "technology.**"
)


class MastheadContractTest(unittest.TestCase):
    def test_generated_masthead_contract(self):
        svg_text = (ROOT / "header.svg").read_text()
        root = ET.fromstring(svg_text)

        self.assertEqual(root.attrib["viewBox"], "0 0 900 190")
        self.assertEqual(root.attrib["width"], "900")
        self.assertEqual(root.attrib["height"], "190")
        self.assertEqual(root.attrib["role"], "img")
        self.assertEqual(root.attrib["aria-label"], ACCESSIBLE_NAME)
        self.assertEqual(root.findtext(f"{SVG_NS}title"), ACCESSIBLE_NAME)

        mark = root.find(f".//{SVG_NS}g[@id='jonmark']")
        self.assertIsNotNone(mark)
        self.assertEqual(
            mark.attrib["transform"], "translate(30 41) scale(0.600000)"
        )

        headlines = [
            node
            for node in root.findall(f".//{SVG_NS}g")
            if node.attrib.get("class") == "ink headline"
        ]
        self.assertEqual(len(headlines), 2)
        self.assertEqual(
            [node.attrib["transform"] for node in headlines],
            [
                "translate(168 84) scale(0.059000 -0.059000)",
                "translate(168 137) scale(0.059000 -0.059000)",
            ],
        )

        self.assertIsNone(root.find(f".//{SVG_NS}line"))
        self.assertNotIn('class="muted"', svg_text)
        self.assertNotIn('class="label"', svg_text)
        self.assertNotIn("<!--DATELINE-->", svg_text)
        self.assertNotIn("<!--/DATELINE-->", svg_text)

    def test_daily_builder_does_not_reintroduce_masthead_date(self):
        source = (ROOT / "tools" / "build_plates.py").read_text()

        self.assertNotIn("import dateline", source)
        self.assertNotIn("dateline.stamp", source)
        self.assertNotIn("dateline:", source)

    def test_readme_intro_contract(self):
        lines = (ROOT / "README.md").read_text().splitlines()

        self.assertEqual(
            lines[0],
            '<img src="header.svg" '
            'alt="Jon Sutton — Creativity + AI + Engineering" width="900">',
        )
        self.assertEqual(lines[2], POSITIONING_COPY)
        self.assertTrue(lines[4].startswith("Most recently at Amazon,"))
        self.assertNotIn("Recent work:", lines)
        self.assertFalse(any("Real-time AI translation" in line for line in lines))
        self.assertFalse(any("Currently exploring" in line for line in lines))
        self.assertEqual(
            lines[6],
            "More at [jonsut.co.uk](https://jonsut.co.uk) · "
            "[LinkedIn](https://www.linkedin.com/in/jon-sutton-b11251147)",
        )
        self.assertEqual(
            lines[14],
            '<img src="section-actions.svg" alt="Data + Actions + SVG" width="900">',
        )


if __name__ == "__main__":
    unittest.main()
