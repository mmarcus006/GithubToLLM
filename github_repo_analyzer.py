import argparse
import os
import re
import subprocess
import tempfile
import sys
from pathlib import Path
from urllib.parse import urlparse

def clone_repo(url, temp_dir):
    print(f"Cloning repository from {url}...")
    try:
        subprocess.run(['git', 'clone', url, temp_dir], check=True, capture_output=True, text=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}", file=sys.stderr)
            return f"Unable to read file content: {str(e)}"

def create_markdown(repo_path, output_file):
    print(f"Creating markdown file: {output_file}")
    total_files = sum(len(files) for _, _, files in os.walk(repo_path))
    processed_files = 0

    with open(output_file, 'w', encoding='utf-8') as md_file:
        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                md_file.write(f"# {relative_path}\n\n")
                content = get_file_content(file_path)
                
                # Bold function names (assuming Python-like syntax)
                content = re.sub(r'^(def|class)\s+(\w+)', r'**\1 \2**', content, flags=re.MULTILINE)
                
                md_file.write(f"```\n{content}\n```\n\n")
                md_file.write("---\n\n")

                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f"Progress: {progress:.2f}% ({processed_files}/{total_files} files processed)", end='\r')

    print("\nMarkdown file created successfully.")

def create_file_tree(repo_path, output_file):
    print(f"Creating file tree: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as tree_file:
            for root, dirs, files in os.walk(repo_path):
                level = root.replace(repo_path, '').count(os.sep)
                indent = ' ' * 4 * level
                tree_file.write(f"{indent}{os.path.basename(root)}/\n")
                sub_indent = ' ' * 4 * (level + 1)
                for file in files:
                    tree_file.write(f"{sub_indent}{file}\n")
        print("File tree created successfully.")
    except IOError as e:
        print(f"Error creating file tree: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub repo and generate markdown and file tree.")
    parser.add_argument("input", help="GitHub repo URL or local folder path")
    args = parser.parse_args()

    input_path = args.input

    if urlparse(input_path).scheme:
        # It's a URL, so clone the repo
        with tempfile.TemporaryDirectory() as temp_dir:
            clone_repo(input_path, temp_dir)
            repo_path = temp_dir
            repo_name = os.path.basename(urlparse(input_path).path)
    else:
        # It's a local path
        repo_path = os.path.abspath(input_path)
        if not os.path.exists(repo_path):
            print(f"Error: The specified path does not exist: {repo_path}", file=sys.stderr)
            sys.exit(1)
        repo_name = os.path.basename(repo_path)

    output_dir = os.path.join(os.getcwd(), f"{repo_name}_analysis")
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating output directory: {str(e)}", file=sys.stderr)
        sys.exit(1)

    markdown_file = os.path.join(output_dir, f"{repo_name}_contents.md")
    tree_file = os.path.join(output_dir, f"{repo_name}_file_tree.txt")

    create_markdown(repo_path, markdown_file)
    create_file_tree(repo_path, tree_file)

    print(f"Analysis complete. Output files are in {output_dir}")

if __name__ == "__main__":
    main()
