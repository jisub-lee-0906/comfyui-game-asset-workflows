import csv
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "danbooru_tag_search.py"


class DanbooruTagSearchTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self.csv_path = self.tmp / "danbooru_tag.csv"
        with self.csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["tag", "aliases"])
            writer.writeheader()
            writer.writerow({"tag": "red_border", "aliases": "crimson_border"})
            writer.writerow({"tag": "window_(computing)", "aliases": "computer_window"})
            writer.writerow({"tag": "bus_interior", "aliases": ""})
            writer.writerow({"tag": "train_interior", "aliases": ""})
            writer.writerow({"tag": "very_long_hair", "aliases": ""})
            writer.writerow({"tag": "long_hair", "aliases": "longhair"})

    def tearDown(self):
        self._tmpdir.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--csv", str(self.csv_path), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_csv_search_normalizes_spaces_and_finds_alias_matches(self):
        result = self.run_cli("search", "computer window")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertTrue(lines[0].startswith("tag\tmatch\tscore\taliases"))
        self.assertIn("window_(computing)\talias", lines[1])

    def test_csv_search_ranks_exact_before_substring(self):
        result = self.run_cli("search", "long hair")
        self.assertEqual(result.returncode, 0, result.stderr)
        first_result = result.stdout.strip().splitlines()[1]
        self.assertTrue(first_result.startswith("long_hair\t"), result.stdout)

    def test_check_reports_missing_tokens_with_suggestions(self):
        result = self.run_cli("check", "red border, train station")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("OK\tred_border", result.stdout)
        self.assertIn("MISSING\ttrain_station", result.stdout)
        self.assertIn("SUGGEST\ttrain_interior", result.stdout)

    def test_optional_sqlite_db_enriches_results_with_count_and_category(self):
        db_path = self.tmp / "danbooru-taxonomy.sqlite"
        if db_path.exists():
            db_path.unlink()
        conn = sqlite3.connect(db_path)
        conn.executescript(
            """
            CREATE TABLE tags (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                category_name TEXT NOT NULL,
                post_count INTEGER NOT NULL,
                is_deprecated INTEGER NOT NULL DEFAULT 0
            );
            INSERT INTO tags VALUES
              (1, 'red_border', 'red_border', 'red border', 'general', 250, 0),
              (2, 'red_hair', 'red_hair', 'red hair', 'general', 100000, 0),
              (3, 'old_red_border', 'old_red_border', 'old red border', 'general', 999, 1);
            """
        )
        conn.commit()
        conn.close()

        result = self.run_cli("search", "red border", "--db", str(db_path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("red_border\texact", result.stdout)
        self.assertIn("general", result.stdout)
        self.assertIn("250", result.stdout)
        self.assertNotIn("old_red_border", result.stdout)

    def test_db_check_works_when_csv_file_is_missing(self):
        db_path = self.tmp / "danbooru-taxonomy.sqlite"
        conn = sqlite3.connect(db_path)
        conn.executescript(
            """
            CREATE TABLE tags (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                category_name TEXT NOT NULL,
                post_count INTEGER NOT NULL,
                is_deprecated INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE tag_aliases (
                id INTEGER PRIMARY KEY,
                alias_name TEXT NOT NULL,
                alias_normalized_name TEXT NOT NULL,
                target_tag_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            );
            INSERT INTO tags VALUES
              (1, 'jpeg_artifacts', 'jpeg_artifacts', 'jpeg artifacts', 'meta', 26083, 0),
              (2, 'highres', 'highres', 'highres', 'meta', 500000, 0),
              (3, 'old_tag', 'old_tag', 'old tag', 'general', 10, 1);
            INSERT INTO tag_aliases VALUES
              (1, 'high_res', 'high_res', 2, 'active');
            """
        )
        conn.commit()
        conn.close()
        missing_csv = self.tmp / "missing.csv"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--csv",
                str(missing_csv),
                "check",
                "jpeg artifacts, high res",
                "--db",
                str(db_path),
                "--mode",
                "auto",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK\tjpeg_artifacts", result.stdout)
        self.assertIn("source=db", result.stdout)
        self.assertIn("OK\thighres", result.stdout)


if __name__ == "__main__":
    unittest.main()
