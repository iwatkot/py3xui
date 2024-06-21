#!/bin/bash

# Check if commit message was supplied
if [ -z "$1" ]
then
  echo "Error: No commit message provided."
  exit 1
fi

# Show the changes
git status

# Add changes to the staging area
git add .

# Commit the changes
git commit -m "$1"

# Push the changes
git push