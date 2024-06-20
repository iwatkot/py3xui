#!/bin/bash

# The directory containing the Python files
src_dir="py3xui"

# Find all subdirectories in the source directory
find "$src_dir" -type d | while read -r dir; do
  # Skip the source directory itself
  if [ "$dir" != "$src_dir" ]; then
    # Find all Python files in the subdirectory, excluding __init__.py
    find "$dir" -name "*.py" ! -name "__init__.py" | while read -r file; do
      # Remove the source directory prefix and the .py extension from the file path
      module="${file#"$src_dir/"}"
      module="${module%.py}"

      # Replace / with . to get the Python module name
      module="${module//\//.}"

      # Generate the documentation and save it to a .md file in the same directory
      pydoc-markdown -I "$src_dir" -m "$module" > "${file%.py}.md"
    done

    # Merge all .md files in the subdirectory into a README.md file
    cat "$dir"/*.md > "$dir/README.md"
    # Find and remove all .md files in the directory, excluding README.md
    find "$dir" -type f -name "*.md" ! -name "README.md" -exec rm -f {} +
  fi
done