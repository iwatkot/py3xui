#!/bin/bash

# The directory containing the Python files
src_dir="py3xui"

echo "Starting pydoc generation for $src_dir"

# Check if source directory exists
if [ ! -d "$src_dir" ]; then
  echo "Error: Source directory '$src_dir' does not exist"
  exit 1
fi

echo "Finding subdirectories in $src_dir..."

# Find all subdirectories in the source directory
find "$src_dir" -type d | while read -r dir; do
  echo "Processing directory: $dir"
  # Skip the source directory itself
  if [ "$dir" != "$src_dir" ]; then
    echo "  Searching for Python files in: $dir"
    # Find all Python files in the subdirectory, excluding __init__.py
    find "$dir" -name "*.py" ! -name "__init__.py" | while read -r file; do
      echo "    Processing file: $file"
      # Remove the source directory prefix and the .py extension from the file path
      module="${file#"$src_dir/"}"
      module="${module%.py}"

      # Replace / with . to get the Python module name
      module="${module//\//.}"

      echo "      Module name: $module"
      echo "      Running: pydoc-markdown -I $src_dir -m $module"

      # Generate the documentation and save it to a .md file in the same directory
      pydoc-markdown -I "$src_dir" -m "$module" > "${file%.py}.md"
      
      if [ $? -eq 0 ]; then
        echo "      ✓ Successfully generated: ${file%.py}.md"
      else
        echo "      ✗ Failed to generate documentation for: $module"
      fi
    done

    echo "  Merging .md files in: $dir"
    
    # Check if there are any .md files to merge (excluding README.md)
    md_files=$(find "$dir" -maxdepth 1 -name "*.md" ! -name "README.md" 2>/dev/null)
    
    if [ -n "$md_files" ]; then
      echo "    Found .md files to merge:"
      echo "$md_files" | while read -r mdfile; do
        echo "      - $mdfile"
      done
      
      # Merge all .md files in the subdirectory into a README.md file
      find "$dir" -maxdepth 1 -name "*.md" ! -name "README.md" -exec cat {} \; > "$dir/README.md" 2>/dev/null
      
      if [ $? -eq 0 ] && [ -s "$dir/README.md" ]; then
        echo "  ✓ Successfully created: $dir/README.md"
      else
        echo "  ✗ Failed to create README.md in: $dir"
      fi
    else
      echo "  ⚠ No .md files found to merge in: $dir"
      # Create an empty README.md or skip
      touch "$dir/README.md"
    fi
    
    echo "  Cleaning up individual .md files in: $dir"
    # Find and remove all .md files in the directory, excluding README.md
    find "$dir" -type f -name "*.md" ! -name "README.md" -exec rm -f {} +
    echo "  ✓ Cleanup completed for: $dir"
  else
    echo "  Skipping root directory: $dir"
  fi
done

echo "Pydoc generation completed!"