#!/usr/bin/env python3
"""
Script to migrate OpenAI functions API to tools API format.
This converts the deprecated 'functions' format to the new 'tools' format.
"""

def migrate_functions_to_tools(file_path):
    """Convert functions array to tools array format."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    result_lines = []
    in_tools_array = False
    function_depth = 0
    collecting_function = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        # Detect start of tools array
        if 'tools = [' in line:
            in_tools_array = True
            result_lines.append(line)
            continue
        
        # Detect end of tools array
        if in_tools_array and line.strip() == ']' and function_depth == 0:
            in_tools_array = False
            result_lines.append(line)
            continue
        
        # Inside tools array
        if in_tools_array:
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            
            # Start of a function that's not already wrapped
            # (top-level { in array, indented 16 spaces, and not already a "type": "function" wrapper)
            if (stripped.startswith('{') and function_depth == 0 and current_indent == 16 and
                i > 0 and '"type": "function"' not in lines[i-1]):
                collecting_function = True
                function_depth = 1
                indent_level = current_indent
                
                # Add wrapper start
                result_lines.append(' ' * indent_level + '{\n')
                result_lines.append(' ' * (indent_level + 4) + '"type": "function",\n')
                result_lines.append(' ' * (indent_level + 4) + '"function": {\n')
                
                # If line has more than just {, add content
                if stripped not in ['{', '{,', '{\n', '{,\n']:
                    content_part = stripped[1:].lstrip()
                    if content_part:
                        result_lines.append(' ' * (indent_level + 8) + content_part)
                continue
            
            # Inside function - track depth and re-indent
            if collecting_function:
                # Count braces
                open_braces = stripped.count('{')
                close_braces = stripped.count('}')
                
                # Update depth
                function_depth += open_braces - close_braces
                
                if function_depth == 0:
                    # End of function
                    collecting_function = False
                    
                    # Close the wrappers
                    has_comma = ',' in stripped
                    result_lines.append(' ' * (indent_level + 8) + '}\n')  # Close function
                    if has_comma:
                        result_lines.append(' ' * (indent_level + 4) + '},\n')  # Close wrapper with comma
                    else:
                        result_lines.append(' ' * (indent_level + 4) + '}\n')  # Close wrapper
                    continue
                
                # Regular line in function - add 8 spaces for nesting
                result_lines.append(' ' * 8 + line)
                continue
        
        # Not in tools array
        result_lines.append(line)
    
    # Write result
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(result_lines)
    
    print("✅ Tools API migration complete!")
    return True

if __name__ == "__main__":
    file_path = "app/services/openai_service.py"
    migrate_functions_to_tools(file_path)

