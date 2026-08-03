from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_plates


class ProfileFeatureCoversTest(unittest.TestCase):
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
