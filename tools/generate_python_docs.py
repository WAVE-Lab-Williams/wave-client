#!/usr/bin/env python3
"""
Generate Python client documentation using introspection and help().

This script inspects the wave_client package and generates markdown documentation
from docstrings, method signatures, and help() output.
"""

import inspect
import sys
import importlib
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re

# Add python directory to path using pathlib
python_dir = Path(__file__).parent.parent / "python"
sys.path.insert(0, str(python_dir))

try:
    import wave_client
    from wave_client import WaveClient
except ImportError as e:
    print(f"Error importing wave_client: {e}")
    print("Make sure you've installed the package in development mode:")
    print("cd python && uv pip install -e .")
    sys.exit(1)


def clean_docstring(docstring: str) -> str:
    """Clean and format a docstring for markdown output."""
    if not docstring:
        return ""

    # Remove common leading whitespace
    lines = docstring.strip().split("\n")
    if len(lines) > 1:
        # Find minimum indentation (ignoring first line and empty lines)
        indents = []
        for line in lines[1:]:
            if line.strip():
                indents.append(len(line) - len(line.lstrip()))
        if indents:
            min_indent = min(indents)
            lines = [lines[0]] + [
                line[min_indent:] if len(line) > min_indent else line for line in lines[1:]
            ]

    return "\n".join(lines)


def format_signature(func: Any, name: str) -> str:
    """Format function signature for markdown."""
    try:
        sig = inspect.signature(func)
        return f"{name}{sig}"
    except (ValueError, TypeError):
        return name


def get_method_info(obj: Any, method_name: str) -> Dict[str, Any]:
    """Get information about a method."""
    method = getattr(obj, method_name, None)
    if not method or method_name.startswith("_"):
        return {}

    info = {
        "name": method_name,
        "signature": format_signature(method, method_name),
        "docstring": clean_docstring(inspect.getdoc(method)),
        "is_async": inspect.iscoroutinefunction(method),
    }

    return info


def generate_quick_reference() -> str:
    """Generate a quick reference section."""
    docs = []
    docs.append("## Quick Reference")
    docs.append("")
    docs.append("```python")
    docs.append("from wave_client import WaveClient")
    docs.append("")
    docs.append("# Initialize client (uses WAVE_API_KEY environment variable)")
    docs.append("async with WaveClient() as client:")
    docs.append("    # Get experiment data as DataFrame")
    docs.append("    df = await client.experiment_data.get_data('experiment-uuid')")
    docs.append("    ")
    docs.append("    # Create new experiment")
    docs.append("    exp = await client.experiments.create(")
    docs.append("        experiment_type_id=1,")
    docs.append("        description='My experiment'")
    docs.append("    )")
    docs.append("    ")
    docs.append("    # Add experiment data")
    docs.append("    await client.experiment_data.create(")
    docs.append("        experiment_id=exp['uuid'],")
    docs.append("        participant_id='P001',")
    docs.append("        data={'reaction_time': 1.234, 'correct': True}")
    docs.append("    )")
    docs.append("```")
    docs.append("")
    return "\n".join(docs)


def generate_class_docs(cls: type, class_name: str, show_methods: bool = True) -> str:
    """Generate documentation for a class."""
    docs = []
    docs.append(f"## {class_name}")
    docs.append("")

    # Class docstring
    class_doc = clean_docstring(inspect.getdoc(cls))
    if class_doc:
        docs.append(class_doc)
        docs.append("")

    if not show_methods:
        return "\n".join(docs)

    # Get all public methods
    methods = []
    for name in dir(cls):
        if not name.startswith("_") and callable(getattr(cls, name, None)):
            method_info = get_method_info(cls, name)
            if method_info:
                methods.append(method_info)

    # Sort methods alphabetically
    methods.sort(key=lambda x: x["name"])

    if methods:
        docs.append("### Methods")
        docs.append("")

        for method in methods:
            # Method signature in code block
            async_prefix = "async" if method["is_async"] else ""
            docs.append("```python")
            docs.append(f"{async_prefix} def {method['signature']}:")
            docs.append('\t"""')

            # Method docstring with tab indentation
            if method["docstring"]:
                # Split docstring into lines and add tab indentation to each
                docstring_lines = method["docstring"].split("\n")
                for line in docstring_lines:
                    docs.append(f"\t{line}")
            else:
                docs.append("\t*No documentation available.*")
            docs.append('\t"""')
            docs.append("```")

    return "\n".join(docs)


def generate_resource_overview() -> str:
    """Generate overview of all resource classes."""
    docs = []
    docs.append("## Resource Classes")
    docs.append("")
    docs.append(
        "The Python client is organized into resource classes that handle different aspects of the API:"
    )
    docs.append("")

    resources = [
        ("experiment_data", "ExperimentDataResource", "Access and manage experiment data rows"),
        ("experiments", "ExperimentsResource", "Manage experiment instances"),
        ("experiment_types", "ExperimentTypesResource", "Define experiment schemas and types"),
        ("tags", "TagsResource", "Organize experiments with labels"),
        ("search", "SearchResource", "Advanced search across all resources"),
    ]

    for attr_name, class_name, description in resources:
        docs.append(f"- **`client.{attr_name}`** ({class_name}): {description}")

    docs.append("")
    docs.append("Each resource class provides methods that return pandas DataFrames by default,")
    docs.append("making data analysis straightforward. Raw dictionary data is also available.")
    docs.append("")

    return "\n".join(docs)


def generate_resource_docs() -> str:
    """Generate documentation for all resource classes."""
    docs = []

    # Import all resource modules
    resource_classes = []

    try:
        from wave_client.resources.experiment_data import ExperimentDataResource

        resource_classes.append((ExperimentDataResource, "ExperimentDataResource"))
    except ImportError:
        pass

    try:
        from wave_client.resources.experiments import ExperimentsResource

        resource_classes.append((ExperimentsResource, "ExperimentsResource"))
    except ImportError:
        pass

    try:
        from wave_client.resources.experiment_types import ExperimentTypesResource

        resource_classes.append((ExperimentTypesResource, "ExperimentTypesResource"))
    except ImportError:
        pass

    try:
        from wave_client.resources.tags import TagsResource

        resource_classes.append((TagsResource, "TagsResource"))
    except ImportError:
        pass

    try:
        from wave_client.resources.search import SearchResource

        resource_classes.append((SearchResource, "SearchResource"))
    except ImportError:
        pass

    for cls, name in resource_classes:
        docs.append(generate_class_docs(cls, name))
        docs.append("")

    return "\n".join(docs)


def generate_exceptions_docs() -> str:
    """Generate documentation for exception classes."""
    docs = []
    docs.append("## Exception Classes")
    docs.append("")
    docs.append("The client includes comprehensive error handling with specific exception types:")
    docs.append("")

    try:
        from wave_client import exceptions

        # Get all exception classes
        exception_classes = []
        for name in dir(exceptions):
            obj = getattr(exceptions, name)
            if inspect.isclass(obj) and issubclass(obj, Exception) and not name.startswith("_"):
                exception_classes.append((obj, name))

        exception_classes.sort(key=lambda x: x[1])

        for cls, name in exception_classes:
            docs.append(f"### `{name}`")
            docs.append("")

            class_doc = clean_docstring(inspect.getdoc(cls))
            if class_doc:
                docs.append(class_doc)
            else:
                docs.append("*No documentation available.*")
            docs.append("")

    except ImportError:
        docs.append("*Exception documentation not available*")
        docs.append("")

    # Add usage example
    docs.append("### Usage Example")
    docs.append("")
    docs.append("```python")
    docs.append("from wave_client.exceptions import AuthenticationError, NotFoundError")
    docs.append("")
    docs.append("try:")
    docs.append("    data = await client.experiment_data.get_data('invalid-id')")
    docs.append("except NotFoundError:")
    docs.append("    print('Experiment not found')")
    docs.append("except AuthenticationError:")
    docs.append("    print('Check your API key')")
    docs.append("```")
    docs.append("")

    return "\n".join(docs)


def generate_configuration_docs() -> str:
    """Generate configuration documentation."""
    docs = []
    docs.append("## Configuration")
    docs.append("")
    docs.append("### Environment Variables")
    docs.append("")
    docs.append("```bash")
    docs.append("# Required")
    docs.append("export WAVE_API_KEY='your-api-key-here'")
    docs.append("")
    docs.append("# Optional (defaults to localhost for development)")
    docs.append("export WAVE_API_URL='http://localhost:8000'")
    docs.append("```")
    docs.append("")
    docs.append("### Direct Configuration")
    docs.append("")
    docs.append("```python")
    docs.append("client = WaveClient(")
    docs.append("    api_key='your-api-key',")
    docs.append("    base_url='https://your-wave-backend.com'")
    docs.append(")")
    docs.append("```")
    docs.append("")
    return "\n".join(docs)


def main():
    """Generate complete Python client documentation."""
    print("Generating Python client documentation...")

    docs = []

    # Header
    docs.append("# Python Client API Reference")
    docs.append("")
    docs.append("*Auto-generated from Python docstrings and introspection*")
    docs.append("")

    # Quick reference
    docs.append(generate_quick_reference())

    # Configuration
    docs.append(generate_configuration_docs())

    # Resource overview
    docs.append(generate_resource_overview())

    # Main client class
    docs.append(generate_class_docs(WaveClient, "WaveClient"))
    docs.append("")

    # Resource classes
    docs.append(generate_resource_docs())

    # Exception classes
    docs.append(generate_exceptions_docs())

    # Write output
    output_path = Path(__file__).parent.parent / "docs" / "python-api-reference.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(docs))

    print(f"Documentation generated: {output_path}")
    print(f"Total lines: {len(docs)}")


if __name__ == "__main__":
    main()
