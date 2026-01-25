#!/usr/bin/env python3
"""
Automatic Documentation Generator for MedBillDozer

This script generates comprehensive documentation by extracting facts directly from the codebase:
- Module structure and dependencies
- Function signatures and docstrings
- Class definitions and their methods
- Provider capabilities and configurations
- API surface and usage patterns

All documentation is derived from code-owned facts, not written by hand.
"""

import ast
import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from collections import defaultdict
import inspect
import importlib.util
import json


@dataclass


class FunctionInfo:
    """Metadata about a function extracted from AST"""
    name: str
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    lineno: int
    is_async: bool = False


@dataclass


class ClassInfo:
    """Metadata about a class extracted from AST"""
    name: str
    bases: List[str]
    docstring: Optional[str]
    methods: List[FunctionInfo]
    attributes: List[str]
    lineno: int


@dataclass


class ModuleInfo:
    """Metadata about a module extracted from AST"""
    filepath: str
    module_name: str
    docstring: Optional[str]
    imports: List[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    constants: Dict[str, Any]
    dependencies: Set[str] = field(default_factory=set)


class CodeAnalyzer(ast.NodeVisitor):
    """Extract facts from Python source code via AST traversal"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.module_name = self._get_module_name(filepath)
        self.imports = []
        self.functions = []
        self.classes = []
        self.constants = {}
        self.dependencies = set()
        self.docstring = None

    def _get_module_name(self, filepath: str) -> str:
        """Convert file path to module name"""
        path = Path(filepath)
        parts = list(path.parts)

        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]

        # Find the starting point (_modules or root)
        try:
            if '_modules' in parts:
                idx = parts.index('_modules')
                return '.'.join(parts[idx:])
        except ValueError:
            pass

        return parts[-1] if parts[-1] != '__init__' else '.'.join(parts[-2:])

    def visit_Module(self, node: ast.Module):
        """Extract module-level docstring"""
        self.docstring = ast.get_docstring(node)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Track import statements"""
        for alias in node.names:
            self.imports.append(alias.name)
            if alias.name.startswith('_modules'):
                self.dependencies.add(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from...import statements"""
        if node.module:
            self.imports.append(node.module)
            if node.module.startswith('_modules'):
                self.dependencies.add(node.module)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Extract function metadata"""
        args = [arg.arg for arg in node.args.args]
        returns = ast.unparse(node.returns) if node.returns else None
        docstring = ast.get_docstring(node)
        decorators = [ast.unparse(d) for d in node.decorator_list]

        func_info = FunctionInfo(
            name=node.name,
            args=args,
            returns=returns,
            docstring=docstring,
            decorators=decorators,
            lineno=node.lineno,
            is_async=False
        )
        self.functions.append(func_info)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Extract async function metadata"""
        args = [arg.arg for arg in node.args.args]
        returns = ast.unparse(node.returns) if node.returns else None
        docstring = ast.get_docstring(node)
        decorators = [ast.unparse(d) for d in node.decorator_list]

        func_info = FunctionInfo(
            name=node.name,
            args=args,
            returns=returns,
            docstring=docstring,
            decorators=decorators,
            lineno=node.lineno,
            is_async=True
        )
        self.functions.append(func_info)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Extract class metadata"""
        bases = [ast.unparse(base) for base in node.bases]
        docstring = ast.get_docstring(node)

        # Extract methods
        methods = []
        attributes = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [arg.arg for arg in item.args.args]
                returns = ast.unparse(item.returns) if item.returns else None
                method_doc = ast.get_docstring(item)
                decorators = [ast.unparse(d) for d in item.decorator_list]

                method_info = FunctionInfo(
                    name=item.name,
                    args=args,
                    returns=returns,
                    docstring=method_doc,
                    decorators=decorators,
                    lineno=item.lineno,
                    is_async=isinstance(item, ast.AsyncFunctionDef)
                )
                methods.append(method_info)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attributes.append(item.target.id)

        class_info = ClassInfo(
            name=node.name,
            bases=bases,
            docstring=docstring,
            methods=methods,
            attributes=attributes,
            lineno=node.lineno
        )
        self.classes.append(class_info)

    def visit_Assign(self, node: ast.Assign):
        """Extract module-level constants"""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                try:
                    # Try to evaluate simple constants
                    value = ast.literal_eval(node.value)
                    self.constants[target.id] = value
                except (ValueError, TypeError):
                    self.constants[target.id] = "<complex value>"

    def analyze(self, source: str) -> ModuleInfo:
        """Parse source code and extract metadata"""
        tree = ast.parse(source)
        self.visit(tree)

        return ModuleInfo(
            filepath=self.filepath,
            module_name=self.module_name,
            docstring=self.docstring,
            imports=self.imports,
            functions=self.functions,
            classes=self.classes,
            constants=self.constants,
            dependencies=self.dependencies
        )


class DocumentationGenerator:
    """Generate markdown documentation from code metadata"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.modules: List[ModuleInfo] = []
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)

    def scan_codebase(self):
        """Scan all Python files and extract metadata"""
        print("🔍 Scanning codebase...")

        # Scan _modules directory
        modules_dir = self.root_dir / "_modules"
        if modules_dir.exists():
            for py_file in modules_dir.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                self._analyze_file(py_file)

        # Scan app.py
        app_file = self.root_dir / "app.py"
        if app_file.exists():
            self._analyze_file(app_file)

        print(f"✓ Analyzed {len(self.modules)} modules")

    def _analyze_file(self, filepath: Path):
        """Analyze a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            analyzer = CodeAnalyzer(str(filepath.relative_to(self.root_dir)))
            module_info = analyzer.analyze(source)
            self.modules.append(module_info)

            # Build dependency graph
            for dep in module_info.dependencies:
                self.dependency_graph[module_info.module_name].add(dep)

        except Exception as e:
            print(f"⚠️  Warning: Could not analyze {filepath}: {e}")

    def generate_overview(self) -> str:
        """Generate project overview documentation"""
        lines = ["# MedBillDozer Documentation", ""]
        lines.append("*Auto-generated from codebase analysis*")
        lines.append("")
        lines.append("## Project Overview")
        lines.append("")

        # Group modules by category
        categories = defaultdict(list)
        for module in self.modules:
            if 'providers' in module.module_name:
                categories['LLM Providers'].append(module)
            elif 'extractors' in module.module_name:
                categories['Fact Extractors'].append(module)
            elif 'prompts' in module.module_name:
                categories['Prompt Builders'].append(module)
            elif 'core' in module.module_name:
                categories['Core Business Logic'].append(module)
            elif 'ui' in module.module_name:
                categories['UI Components'].append(module)
            elif 'utils' in module.module_name:
                categories['Utilities'].append(module)
            else:
                categories['Application'].append(module)

        lines.append(f"**Total Modules:** {len(self.modules)}")
        lines.append("")

        for category, modules in sorted(categories.items()):
            lines.append(f"### {category} ({len(modules)} modules)")
            lines.append("")
            for module in sorted(modules, key=lambda m: m.module_name):
                doc_snippet = module.docstring.split('\n')[0] if module.docstring else "No description"
                lines.append(f"- **{module.module_name}**: {doc_snippet}")
            lines.append("")

        return "\n".join(lines)

    def generate_module_docs(self, module: ModuleInfo) -> str:
        """Generate detailed documentation for a single module"""
        lines = [f"## Module: `{module.module_name}`", ""]

        # File path
        lines.append(f"**Source:** `{module.filepath}`")
        lines.append("")

        # Docstring
        if module.docstring:
            lines.append("### Description")
            lines.append("")
            lines.append(module.docstring)
            lines.append("")

        # Constants
        if module.constants:
            lines.append("### Constants")
            lines.append("")
            for name, value in sorted(module.constants.items()):
                if isinstance(value, str) and len(value) > 50:
                    value = f"{value[:47]}..."
                lines.append(f"- **`{name}`**: `{value}`")
            lines.append("")

        # Classes
        if module.classes:
            lines.append("### Classes")
            lines.append("")
            for cls in module.classes:
                lines.extend(self._format_class(cls))
            lines.append("")

        # Functions
        if module.functions:
            lines.append("### Functions")
            lines.append("")
            for func in module.functions:
                lines.extend(self._format_function(func))
            lines.append("")

        # Dependencies
        if module.dependencies:
            lines.append("### Dependencies")
            lines.append("")
            for dep in sorted(module.dependencies):
                lines.append(f"- `{dep}`")
            lines.append("")

        return "\n".join(lines)

    def _format_class(self, cls: ClassInfo) -> List[str]:
        """Format class documentation"""
        lines = [f"#### `{cls.name}`"]
        lines.append("")

        # Bases
        if cls.bases:
            lines.append(f"**Inherits from:** {', '.join(f'`{b}`' for b in cls.bases)}")
            lines.append("")

        # Docstring
        if cls.docstring:
            lines.append(cls.docstring)
            lines.append("")

        # Attributes
        if cls.attributes:
            lines.append("**Attributes:**")
            for attr in cls.attributes:
                lines.append(f"- `{attr}`")
            lines.append("")

        # Methods
        if cls.methods:
            lines.append("**Methods:**")
            lines.append("")
            for method in cls.methods:
                sig = self._format_signature(method)
                lines.append(f"- **`{sig}`**")
                if method.docstring:
                    # First line of docstring
                    first_line = method.docstring.split('\n')[0].strip()
                    lines.append(f"  - {first_line}")
                lines.append("")

        return lines

    def _format_function(self, func: FunctionInfo) -> List[str]:
        """Format function documentation"""
        lines = []

        sig = self._format_signature(func)
        lines.append(f"#### `{sig}`")
        lines.append("")

        if func.decorators:
            lines.append(f"**Decorators:** {', '.join(f'`@{d}`' for d in func.decorators)}")
            lines.append("")

        if func.docstring:
            lines.append(func.docstring)
            lines.append("")

        return lines

    def _format_signature(self, func: FunctionInfo) -> str:
        """Format function signature"""
        prefix = "async " if func.is_async else ""
        args_str = ", ".join(func.args)
        returns_str = f" -> {func.returns}" if func.returns else ""
        return f"{prefix}{func.name}({args_str}){returns_str}"

    def generate_dependency_graph(self) -> str:
        """Generate dependency graph documentation"""
        lines = ["## Dependency Graph", ""]
        lines.append("Module dependencies within the project:")
        lines.append("")

        for module, deps in sorted(self.dependency_graph.items()):
            if deps:
                lines.append(f"### `{module}`")
                lines.append("")
                lines.append("**Depends on:**")
                for dep in sorted(deps):
                    lines.append(f"- `{dep}`")
                lines.append("")

        return "\n".join(lines)

    def generate_api_reference(self) -> str:
        """Generate API reference for public interfaces"""
        lines = ["## API Reference", ""]
        lines.append("Public interfaces and their usage patterns.")
        lines.append("")

        # Find provider interface
        for module in self.modules:
            if 'llm_interface' in module.module_name:
                lines.append("### Provider Interface")
                lines.append("")
                for cls in module.classes:
                    if 'Provider' in cls.name or 'Registry' in cls.name:
                        lines.extend(self._format_class(cls))

        return "\n".join(lines)

    def generate_all(self, output_dir: Optional[Path] = None):
        """Generate all documentation files"""
        if output_dir is None:
            output_dir = self.root_dir / "docs"

        output_dir.mkdir(exist_ok=True)

        print(f"📝 Generating documentation in {output_dir}...")

        # Generate overview
        overview = self.generate_overview()
        (output_dir / "README.md").write_text(overview, encoding='utf-8')
        print("✓ Generated README.md")

        # Generate module documentation
        modules_doc = [overview, ""]
        for module in sorted(self.modules, key=lambda m: m.module_name):
            modules_doc.append(self.generate_module_docs(module))

        (output_dir / "MODULES.md").write_text("\n".join(modules_doc), encoding='utf-8')
        print("✓ Generated MODULES.md")

        # Generate dependency graph
        dep_graph = self.generate_dependency_graph()
        (output_dir / "DEPENDENCIES.md").write_text(dep_graph, encoding='utf-8')
        print("✓ Generated DEPENDENCIES.md")

        # Generate API reference
        api_ref = self.generate_api_reference()
        (output_dir / "API.md").write_text(api_ref, encoding='utf-8')
        print("✓ Generated API.md")

        # Generate JSON manifest for programmatic access
        manifest = {
            "generated_at": str(Path.cwd()),
            "total_modules": len(self.modules),
            "modules": [
                {
                    "name": m.module_name,
                    "filepath": m.filepath,
                    "has_docstring": m.docstring is not None,
                    "num_classes": len(m.classes),
                    "num_functions": len(m.functions),
                    "num_dependencies": len(m.dependencies),
                    "constants": list(m.constants.keys()),
                }
                for m in self.modules
            ]
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding='utf-8'
        )
        print("✓ Generated manifest.json")

        print(f"\n✅ Documentation generated successfully in {output_dir}/")


def main():
    """Main entry point"""
    root_dir = Path(__file__).parent.parent

    print("=" * 60)
    print("MedBillDozer Automatic Documentation Generator")
    print("=" * 60)
    print()

    generator = DocumentationGenerator(str(root_dir))
    generator.scan_codebase()
    generator.generate_all()

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

