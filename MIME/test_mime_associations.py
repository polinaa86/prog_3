import tempfile
import unittest
from pathlib import Path
from mime_associations import read_associations, merge_associations, write_associations


class MimeAssociationsTests(unittest.TestCase):
    def test_read_and_write(self):
        associations = {
            "Removed Associations": {"image/png": ["old.desktop"]},
            "Default Applications": {"text/plain": ["editor.desktop", "other.desktop"]},
            "Added Associations": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mimeapps.list"
            write_associations(associations, str(path))
            contents = path.read_text(encoding="utf-8")
            self.assertTrue(contents.startswith("[Default Applications]\n"))
            self.assertNotIn("[Added Associations]", contents)
            self.assertIn("text/plain=editor.desktop;other.desktop\n", contents)
            self.assertEqual(read_associations(str(path)), {
                "Default Applications": associations["Default Applications"],
                "Removed Associations": associations["Removed Associations"],
            })

    def test_merge_does_not_mutate_inputs(self):
        old = {"Default Applications": {"text/plain": ["old.desktop"], "image/png": ["pic.desktop"]}}
        new = {"Default Applications": {"text/plain": ["new.desktop"]}, "Added Associations": {"application/pdf": ["pdf.desktop"]}}
        merged = merge_associations(old, new)
        self.assertEqual(merged["Default Applications"]["text/plain"], ["new.desktop"])
        self.assertEqual(merged["Default Applications"]["image/png"], ["pic.desktop"])
        merged["Default Applications"]["text/plain"].append("extra.desktop")
        self.assertEqual(old["Default Applications"]["text/plain"], ["old.desktop"])
        self.assertEqual(new["Default Applications"]["text/plain"], ["new.desktop"])


if __name__ == "__main__":
    unittest.main()
