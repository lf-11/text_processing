import os

def count_lines(file_path):
    """Counts the number of lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    except Exception:
        return 0

def generate_structure_and_count(dir_path, indent="", base_path=None):
    """Recursively generates the structure and collects line count information."""
    structure = []
    large_files = []
    
    # Set base_path on first call
    if base_path is None:
        base_path = dir_path

    # Define allowed extensions and ignored patterns
    allowed_extensions = ('.py', '.html', '.css', '.txt', '.js')
    ignored_patterns = (
        '__pycache__',
        '.pyc',
        'alembic',
        '.pdf'
    )

    for entry in sorted(os.listdir(dir_path)):
        full_path = os.path.join(dir_path, entry)
        
        # Skip ignored patterns
        if any(pattern in entry for pattern in ignored_patterns):
            continue

        if os.path.isdir(full_path):
            structure.append(f"{indent}├── {entry}")
            sub_structure, sub_large_files = generate_structure_and_count(full_path, indent + "│   ", base_path)
            structure.extend(sub_structure)
            large_files.extend(sub_large_files)
        else:
            if entry.endswith(allowed_extensions):
                line_count = count_lines(full_path)
                if line_count > 100:
                    # Get relative path from base directory
                    rel_path = os.path.relpath(full_path, base_path)
                    large_files.append((entry, rel_path, line_count))
            structure.append(f"{indent}├── {entry}")

    return structure, large_files

def write_to_markdown(output_file, large_files, structure):
    """Writes the large file list and structure to a markdown file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        # Write large files section
        file.write("# Files with more than 100 lines\n\n")
        if large_files:
            for filename, path, line_count in large_files:
                file.write(f"- **{filename}** ({path}): {line_count} lines\n")
        else:
            file.write("No files with more than 100 lines.\n")

        # Write structure section - now without extra newlines
        file.write("\n# Project Structure\n")  # Removed extra newline before structure
        for line in structure:
            file.write(line)  # Removed \n
            if line != structure[-1]:  # Add newline for all but last line
                file.write('\n')

def main():
    project_root = os.getcwd()  # Current directory
    output_file = "project_structure.md"

    structure, large_files = generate_structure_and_count(project_root)
    write_to_markdown(output_file, large_files, structure)

    print(f"Project structure and file analysis saved to {output_file}")

if __name__ == "__main__":
    main()
