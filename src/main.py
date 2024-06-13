"""Main entry point to CLI interface"""

import ast
import sys

from dataclasses import dataclass, field

@dataclass
class ExtractedContent:
    filename: str
    content: list[str]      
    dependencies: list[str] = field(default_factory=list)

def read_and_parse_source(source_path: str) -> tuple[ast.Module, str]:
    """Reads and parses the source code from a given Python file."""
    with open(source_path, 'r') as file:
        source_code = file.read()
        node = ast.parse(source_code, filename=source_path)
    return node, source_code

def extract_method_or_cls_content(source_path: str, method_or_cls: str) -> ExtractedContent:
    """Extracts the content of a method or class from a given Python file and
    returns it as an ExtractedContent dataclass."""
    node, source_code = read_and_parse_source(source_path)
       

    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.ClassDef)) and child.name == method_or_cls:
            start_lineno = child.lineno
            end_lineno = child.end_lineno
            target_content_lines = source_code.splitlines()[start_lineno - 1:end_lineno]
            break

    if not target_content_lines:
        raise ValueError(f"No target named '{method_or_cls}' found in {source_path}")

    return ExtractedContent(filename=source_path, content=target_content_lines)

def extract_dependencies(source_path: str, method_or_cls_content: list[str]) -> list:
    """Extracts non-builtin dependencies from the target content, including local definitions."""
    
    node, source_code = read_and_parse_source(source_path)
    
    defined_funcs_and_classes = set()
    for child in ast.walk(node):
        # Get function and class names defined in the source code
        if isinstance(child, (ast.FunctionDef, ast.ClassDef)):
            defined_funcs_and_classes.add(child.name)
        # Get variable names defined in the source code
        if isinstance(child, ast.Name):
            continue
            # defined_names.add(child.id)
    # Convert defined_names to a sorted list for better readability
    in_file_defined_funcs_and_classes = sorted(defined_funcs_and_classes)
    
    # Print the defined names to the terminal
    print("These are all the function and classnames in the Source Code:")
    for name in in_file_defined_funcs_and_classes:
        print(name)

    in_file_imports = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Import):
            for alias in child.names:
                in_file_imports.add(alias.name)
        elif isinstance(child, ast.ImportFrom):
            for alias in child.names:
                in_file_imports.add(alias.name if child.module is None else f"{child.module}.{alias.name}")
    print("These are all the imports in the Source Code:")
    for name in in_file_imports:
        print(name)

    dependencies = []
    for line in method_or_cls_content:
        for defined_name in in_file_defined_funcs_and_classes:
            if defined_name in line:
                dependencies.append(defined_name)
        for import_name in in_file_imports:
            if import_name in line:
                dependencies.append(import_name)
    
    print("These are all the dependencies within the target content:")
    for name in dependencies:
        print(name)

    return dependencies

def add_dependencies_to_extracted_content(extracted_content: ExtractedContent) -> ExtractedContent:
    """Adds a list of non-builtin dependencies to the ExtractedContent dataclass."""
    dependencies = extract_dependencies(extracted_content.filename, extracted_content.content)
    extracted_content_with_deps = ExtractedContent(
        filename=extracted_content.filename,
        content=extracted_content.content,
        dependencies=dependencies
    )
    return extracted_content_with_deps



def main():
    """Main entry point to CLI interface"""
    if len(sys.argv) != 3:
        print("Usage: python main.py <source_path> <method_or_class_name>")
        sys.exit(1)

    source_path = sys.argv[1]
    target = sys.argv[2]
    extracted_content = extract_method_or_cls_content(source_path, target)
    extracted_content_with_deps = add_dependencies_to_extracted_content(extracted_content)

    print(f"Filename: {extracted_content_with_deps.filename}")
    print("Content:")
    print(extracted_content_with_deps.content)



if __name__ == "__main__":
    main()