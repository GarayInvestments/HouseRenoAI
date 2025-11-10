#!/usr/bin/env python3
"""
Complete the tools API migration by wrapping remaining functions 5-12.
"""

def wrap_remaining_functions():
    with open('app/services/openai_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find line numbers for the remaining unwrapped functions
    # They start with:                 { (16 spaces)
    # Followed by:                     "name": (20 spaces)
    
    result_lines = []
    i = 0
    functions_wrapped = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is an unwrapped function definition
        if (line == '                {\n' and  # Exactly 16 spaces + {
            i + 1 < len(lines) and
            '"name":' in lines[i + 1] and  # Next line has "name":
            i > 0 and
            '"type": "function"' not in lines[i - 1]):  # Not already wrapped
            
            # Found unwrapped function - wrap it
            functions_wrapped += 1
            result_lines.append('                {\n')  # 16 spaces
            result_lines.append('                    "type": "function",\n')  # 20 spaces
            result_lines.append('                    "function": {\n')  # 20 spaces
            i += 1  # Skip the opening {
            
            # Now copy all lines of the function, adding 8 spaces of indentation
            depth = 1
            while i < len(lines) and depth > 0:
                cur_line = lines[i]
                depth += cur_line.count('{') - cur_line.count('}')
                
                if depth == 0:
                    # This is the closing brace
                    has_comma = ',' in cur_line
                    result_lines.append('                        }\n')  # Close function (24 spaces)
                    if has_comma:
                        result_lines.append('                    },\n')  # Close wrapper with comma (20 spaces)
                    else:
                        result_lines.append('                    }\n')  # Close wrapper without comma (20 spaces)
                else:
                    # Regular line - add 8 spaces
                    result_lines.append('        ' + cur_line)
                
                i += 1
            continue
        
        # Not an unwrapped function, keep as is
        result_lines.append(line)
        i += 1
    
    # Write back
    with open('app/services/openai_service.py', 'w', encoding='utf-8') as f:
        f.writelines(result_lines)
    
    print(f'✅ Wrapped {functions_wrapped} additional functions')
    print(f'✅ Tools API migration complete!')
    return functions_wrapped

if __name__ == '__main__':
    count = wrap_remaining_functions()
    if count != 8:
        print(f'⚠️  Warning: Expected to wrap 8 functions, wrapped {count}')
