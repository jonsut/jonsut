import ast
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ARSENAL_ACCESSIBLE_NAME = (
    "Arsenal's 2025–26 championship season: 14 league titles, "
    "85 points, 7 points clear"
)
sys.path.insert(0, str(ROOT / "tools"))
import build_plates


class ProfileFeatureCoversTest(unittest.TestCase):
    def test_fixed_arsenal_shirts_header_contract(self):
        asset = ROOT / "arsenal-shirts.svg"
        self.assertTrue(
            asset.is_file(), "approved Arsenal shirts asset is missing"
        )

        asset_root = ET.fromstring(asset.read_text())
        self.assertEqual(asset_root.attrib["viewBox"], "0 0 900 360")
        self.assertEqual(asset_root.attrib["width"], "900")
        self.assertEqual(asset_root.attrib["height"], "360")
        self.assertEqual(asset_root.attrib["role"], "img")
        self.assertEqual(
            asset_root.attrib["aria-label"], ARSENAL_ACCESSIBLE_NAME
        )
        self.assertEqual(
            asset_root.findtext("{http://www.w3.org/2000/svg}title"),
            ARSENAL_ACCESSIBLE_NAME,
        )

        readme = (ROOT / "README.md").read_text()
        embed = (
            f'<img src="arsenal-shirts.svg" alt="{ARSENAL_ACCESSIBLE_NAME}" '
            'width="900">'
        )
        self.assertEqual(readme.count(embed), 1)
        football_fragment = (
            f"### Football\n\n{embed}\n\nThe other national obsession."
        )
        self.assertEqual(readme.count(football_fragment), 1)

        football_heading = readme.index("### Football")
        shirts_header = readme.index(embed)
        football_copy = readme.index("The other national obsession.")
        results_asset = readme.index('src="arsenal-results.svg"')
        self.assertTrue(
            football_heading
            < shirts_header
            < football_copy
            < results_asset
        )

        for builder in ("tools/build_plates.py", "tools/build_football.py"):
            self.assertNotIn("arsenal-shirts.svg", (ROOT / builder).read_text())

        football_builder = (ROOT / "tools/build_football.py").read_text()
        specs_dict = next(
            (
                node.value
                for node in ast.walk(ast.parse(football_builder))
                if isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Dict)
                and any(
                    isinstance(target, ast.Name) and target.id == "specs"
                    for target in node.targets
                )
            ),
            None,
        )
        self.assertIsNotNone(
            specs_dict,
            "tools/build_football.py must define specs as a dict literal",
        )
        keys = {
            key.value
            for key in specs_dict.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
        self.assertEqual(keys, {"results", "position", "form"})
        generated_assets = {f"arsenal-{key}.svg" for key in keys}
        self.assertNotIn("arsenal-shirts.svg", generated_assets)

    def test_live_cover_is_the_profile_hook(self):
        readme = (ROOT / "README.md").read_text()
        today_start_marker = "<!-- TODAY:START -->"
        today_end_marker = "<!-- TODAY:END -->"

        self.assertEqual(readme.count(today_start_marker), 1)
        self.assertEqual(readme.count(today_end_marker), 1)
        self.assertEqual(readme.count("cover.svg"), 1)

        links = readme.index("More at [jonsut.co.uk]")
        today_start = readme.index(today_start_marker)
        cover = readme.index("cover.svg")
        today_end = readme.index(today_end_marker)
        breathing_space = readme.index("<br><br><br>")
        section_actions = readme.index("section-actions.svg")
        london_heading = readme.index("### London environment")

        self.assertTrue(
            links
            < today_start
            < cover
            < today_end
            < breathing_space
            < section_actions
            < london_heading
        )
        london_tail = readme[london_heading:]
        self.assertNotIn("<!-- TODAY:", london_tail)

        cover_root = ET.fromstring((ROOT / "cover.svg").read_text())
        self.assertEqual(cover_root.attrib["viewBox"], "0 0 900 400")

    def test_daily_cover_replacement_is_location_independent(self):
        original_root = build_plates.ROOT
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                build_plates.ROOT = temp_dir
                readme = Path(temp_dir) / "README.md"
                readme.write_text(
                    "intro\n"
                    "<!-- TODAY:START -->\n"
                    "old cover\n"
                    "<!-- TODAY:END -->\n"
                    "outro\n"
                )

                build_plates.update_readme(
                    '<img src="cover.svg" alt="new reading" width="900">'
                )

                self.assertEqual(
                    readme.read_text(),
                    "intro\n"
                    "<!-- TODAY:START -->\n"
                    '<img src="cover.svg" alt="new reading" width="900">\n'
                    "<!-- TODAY:END -->\n"
                    "outro\n",
                )
        finally:
            build_plates.ROOT = original_root


if __name__ == "__main__":
    unittest.main()
