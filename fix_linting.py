#!/usr/bin/env python3
"""Automated linting fixes for common issues."""
import re
import sys
from pathlib import Path


def fix_file(filepath):
    """Fix common linting issues in a Python file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Remove trailing whitespace
    lines = [line.rstrip() + '\n' if line.strip() else '\n' for line in lines]

    # Ensure file ends with exactly one newline
    while lines and lines[-1] == '\n':
        lines.pop()
    if lines:
        lines.append('\n')

    # Fix too many blank lines (keep max 2)
    fixed_lines = []
    blank_count = 0
    for line in lines:
        if line == '\n':
            blank_count += 1
            if blank_count <= 2:
                fixed_lines.append(line)
        else:
            blank_count = 0
            fixed_lines.append(line)

    with open(filepath, 'w') as f:
        f.writelines(fixed_lines)


if __name__ == '__main__':
    # Fix all Python files
    for pyfile in Path('.').rglob('*.py'):
        if '.venv' not in str(pyfile) and 'venv' not in str(pyfile) and '.git' not in str(pyfile):
            try:
                fix_file(pyfile)
                print(f"Fixed: {pyfile}")
            except Exception as e:
                print(f"Error fixing {pyfile}: {e}", file=sys.stderr)

