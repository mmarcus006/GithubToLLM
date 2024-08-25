import unittest
import os
import tempfile
from github_repo_analyzer import get_file_content, create_markdown, create_file_tree

class TestGithubRepoAnalyzer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_content = "def test_function():\n    pass\n\nclass TestClass:\n    def method(self):\n        pass"
        self.test_file_path = os.path.join(self.temp_dir, "test_file.py")
        with open(self.test_file_path, "w") as f:
            f.write(self.test_file_content)

    def tearDown(self):
        os.remove(self.test_file_path)
        os.rmdir(self.temp_dir)

    def test_get_file_content(self):
        content = get_file_content(self.test_file_path)
        self.assertEqual(content, self.test_file_content)

    def test_create_markdown(self):
        output_file = os.path.join(self.temp_dir, "output.md")
        create_markdown(self.temp_dir, output_file)
        
        with open(output_file, "r") as f:
            content = f.read()
        
        self.assertIn("# test_file.py", content)
        self.assertIn("```", content)
        self.assertIn("**def** test_function", content)
        self.assertIn("**class** TestClass", content)

    def test_create_file_tree(self):
        output_file = os.path.join(self.temp_dir, "tree.txt")
        create_file_tree(self.temp_dir, output_file)
        
        with open(output_file, "r") as f:
            content = f.read()
        
        self.assertIn(os.path.basename(self.temp_dir), content)
        self.assertIn("test_file.py", content)

if __name__ == "__main__":
    unittest.main()
