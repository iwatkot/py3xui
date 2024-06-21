#!/bin/sh

# Directories to be removed
dirs=".mypy_cache .pytest_cache htmlcov dist pyx3ui.egg-info"

# Files to be removed
files=".coverage"

# Loop through the directories
for dir in $dirs
do
  echo "Removing directory $dir"
  rm -rf $dir
done

# Loop through the files
for file in $files
do
  echo "Removing file $file"
  rm -f $file
done

echo "Removing __pycache__ directories"
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Cleanup completed."