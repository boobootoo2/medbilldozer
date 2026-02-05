#!/usr/bin/env python3
"""
Migration Helper Script: _modules/ → src/medbilldozer/

This script helps automate the incremental migration of modules from the old
_modules/ structure to the new src/medbilldozer/ structure.

Usage:
    python3 scripts/migrate_module.py --module utils --dry-run
    python3 scripts/migrate_module.py --module utils --execute

Phase 2: Module-by-Module Migration
"""

import argparse
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in a directory recursively."""
    return list(directory.rglob("*.py"))


def update_imports_in_file(file_path: Path, dry_run: bool = True) -> List[Tuple[str, str]]:
    """
    Update imports from medbilldozer.* to medbilldozer.* in a single file.
    
    Returns list of (old_import, new_import) tuples that were changed.
    """
    changes = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: from medbilldozer.X import Y
    pattern1 = r'from _modules\.(\w+(?:\.\w+)*) import'
    def replace1(match):
        old = f"from medbilldozer.{match.group(1)} import"
        new = f"from medbilldozer.{match.group(1)} import"
        changes.append((old, new))
        return new
    content = re.sub(pattern1, replace1, content)
    
    # Pattern 2: import medbilldozer.X
    pattern2 = r'import _modules\.(\w+(?:\.\w+)*)'
    def replace2(match):
        old = f"import medbilldozer.{match.group(1)}"
        new = f"import medbilldozer.{match.group(1)}"
        changes.append((old, new))
        return new
    content = re.sub(pattern2, replace2, content)
    
    # Only write if content changed and not dry run
    if content != original_content and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return changes


def copy_module(module_name: str, dry_run: bool = True) -> None:
    """
    Copy a module from _modules/ to src/medbilldozer/ and update imports.
    
    Args:
        module_name: Name of the module (e.g., 'utils', 'core', 'providers')
        dry_run: If True, only print what would be done
    """
    repo_root = Path(__file__).parent.parent
    old_path = repo_root / "_modules" / module_name
    new_path = repo_root / "src" / "medbilldozer" / module_name
    
    if not old_path.exists():
        print(f"❌ Error: Module '{module_name}' not found in _modules/")
        return
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Migrating module: {module_name}")
    print(f"  From: {old_path}")
    print(f"  To:   {new_path}")
    print()
    
    # Find all Python files in the old module
    py_files = find_python_files(old_path)
    print(f"Found {len(py_files)} Python files to migrate")
    print()
    
    total_changes = 0
    
    for py_file in py_files:
        relative_path = py_file.relative_to(old_path)
        new_file_path = new_path / relative_path
        
        print(f"{'  [DRY RUN] ' if dry_run else '  '}Processing: {relative_path}")
        
        # Create directory structure in new location
        if not dry_run:
            new_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        if not dry_run:
            shutil.copy2(py_file, new_file_path)
            print(f"    ✅ Copied to {new_file_path.relative_to(repo_root)}")
        else:
            print(f"    Would copy to {new_file_path.relative_to(repo_root)}")
        
        # Update imports in the copied file
        changes = update_imports_in_file(new_file_path if not dry_run else py_file, dry_run=True)
        
        if changes:
            print(f"    📝 Import changes needed: {len(changes)}")
            for old, new in changes[:3]:  # Show first 3
                print(f"       {old} → {new}")
            if len(changes) > 3:
                print(f"       ... and {len(changes) - 3} more")
            
            # Apply changes if not dry run
            if not dry_run:
                actual_changes = update_imports_in_file(new_file_path, dry_run=False)
                print(f"    ✅ Updated {len(actual_changes)} imports")
            
            total_changes += len(changes)
        
        print()
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Migration summary:")
    print(f"  Files processed: {len(py_files)}")
    print(f"  Import changes: {total_changes}")
    
    if dry_run:
        print()
        print("To execute this migration, run:")
        print(f"  python3 scripts/migrate_module.py --module {module_name} --execute")
    else:
        print()
        print("✅ Migration complete!")
        print()
        print("Next steps:")
        print("1. Run tests: pytest tests/")
        print("2. Verify imports work: python3 -c 'from medbilldozer.{} import *'".format(module_name))
        print("3. Add backward compatibility shim to _modules/{}/__init__.py".format(module_name))
        print("4. Update consumers to use new import paths")


def create_backward_compat_shim(module_name: str, dry_run: bool = True) -> None:
    """
    Create a backward compatibility shim in _modules/ that re-exports from src/.
    """
    repo_root = Path(__file__).parent.parent
    shim_file = repo_root / "_modules" / module_name / "__init__.py"
    
    shim_content = f'''"""
Backward compatibility shim for _modules.{module_name}

This module has been migrated to medbilldozer.{module_name}.
Imports from medbilldozer.{module_name} will continue to work but are deprecated.

Prefer: from medbilldozer.{module_name} import ...
Old:    from medbilldozer.{module_name} import ...
"""

# Re-export everything from the new location
from medbilldozer.{module_name} import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.{module_name} is deprecated, use medbilldozer.{module_name}",
#     DeprecationWarning,
#     stacklevel=2
# )
'''
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Creating backward compatibility shim:")
    print(f"  File: {shim_file.relative_to(repo_root)}")
    print()
    
    if dry_run:
        print("Content preview:")
        print("─" * 60)
        print(shim_content)
        print("─" * 60)
    else:
        with open(shim_file, 'w', encoding='utf-8') as f:
            f.write(shim_content)
        print("✅ Shim created successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate a module from _modules/ to src/medbilldozer/"
    )
    parser.add_argument(
        "--module",
        required=True,
        choices=["utils", "data", "prompts", "extractors", "ingest", "core", "providers", "ui"],
        help="Module to migrate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Execute the migration (opposite of --dry-run)"
    )
    parser.add_argument(
        "--create-shim",
        action="store_true",
        default=False,
        help="Create backward compatibility shim in _modules/"
    )
    
    args = parser.parse_args()
    
    # Default to dry run unless --execute is specified
    dry_run = not args.execute
    
    if args.create_shim:
        create_backward_compat_shim(args.module, dry_run=dry_run)
    else:
        copy_module(args.module, dry_run=dry_run)


if __name__ == "__main__":
    main()
