#!/usr/bin/env python3
"""
Convert between Obsidian and MkDocs callout syntax
"""
import re
import sys
from pathlib import Path

def obsidian_to_mkdocs(content):
    """Convert Obsidian callouts to MkDocs admonitions"""
    lines = content.split('\n')
    result = []
    in_callout = False
    
    for line in lines:
        # Match callout start: > [!type] Title
        if match := re.match(r'^> \[!(\w+)\]\s*(.*)', line):
            callout_type = match.group(1).lower()
            title = match.group(2)
            if title:
                result.append(f'!!! {callout_type} "{title}"')
            else:
                result.append(f'!!! {callout_type}')
            in_callout = True
        # Match callout continuation: > content
        elif in_callout and line.startswith('> '):
            content = line[2:]  # Remove "> "
            result.append(f'    {content}')
        # Empty line in callout
        elif in_callout and line == '>':
            result.append('    ')
        # End of callout
        elif in_callout and not line.startswith('>'):
            in_callout = False
            result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def mkdocs_to_obsidian(content):
    """Convert MkDocs admonitions to Obsidian callouts"""
    lines = content.split('\n')
    result = []
    in_admonition = False
    
    for line in lines:
        # Match admonition start: !!! type "Title"
        if match := re.match(r'^!!!\s+(\w+)\s*"?([^"]*)"?', line):
            callout_type = match.group(1)
            title = match.group(2)
            if title:
                result.append(f'> [!{callout_type}] {title}')
            else:
                result.append(f'> [!{callout_type}]')
            in_admonition = True
        # Match indented content (4 spaces)
        elif in_admonition and line.startswith('    '):
            content = line[4:]  # Remove 4 spaces
            result.append(f'> {content}')
        # Empty line in admonition
        elif in_admonition and line.strip() == '':
            result.append('>')
        # End of admonition
        elif in_admonition and not line.startswith(' '):
            in_admonition = False
            result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def process_file(filepath, direction='to-mkdocs'):
    """Process a single markdown file"""
    path = Path(filepath)
    content = path.read_text()
    
    if direction == 'to-mkdocs':
        converted = obsidian_to_mkdocs(content)
    else:
        converted = mkdocs_to_obsidian(content)
    
    path.write_text(converted)
    print(f"Converted: {filepath}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert-callouts.py [to-mkdocs|to-obsidian] [file.md or directory]")
        sys.exit(1)
    
    direction = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else 'docs'
    
    target_path = Path(target)
    
    if target_path.is_file():
        process_file(target_path, direction)
    elif target_path.is_dir():
        for md_file in target_path.rglob('*.md'):
            process_file(md_file, direction)
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

if __name__ == '__main__':
    main()
