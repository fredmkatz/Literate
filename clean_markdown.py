import re
import textwrap

def clean_markdown(md0, width=80):
    """
    Clean markdown text by properly wrapping lines while respecting markdown elements.
    
    Args:
        md0 (str): The input markdown text
        width (int): Maximum line width for wrapped text (default: 80)
        
    Returns:
        str: Cleaned markdown with properly wrapped text
    """
    # Split the markdown into lines
    lines = md0.split('\n')
    
    # Initialize variables
    result = []
    in_code_block = False
    in_list = False
    buffer = []
    list_indent = 0
    
    for line in lines:
        # Check for code block delimiters
        if line.strip().startswith('```'):
            # Flush the buffer before starting/ending a code block
            if buffer:
                if not in_code_block:
                    wrapped = textwrap.fill('\n'.join(buffer), width=width)
                    result.append(wrapped)
                else:
                    result.extend(buffer)
                buffer = []
            
            # Toggle code block state and add the line
            in_code_block = not in_code_block
            result.append(line)
            continue
        
        # If we're in a code block, preserve the line as is
        if in_code_block:
            result.append(line)
            continue
        
        # Check for headings (# to ######)
        if re.match(r'^#{1,6}\s', line.strip()):
            # Flush the buffer before adding a heading
            if buffer:
                wrapped = textwrap.fill('\n'.join(buffer), width=width)
                result.append(wrapped)
                buffer = []
            
            result.append(line)
            continue
        
        # Check for horizontal rules
        if re.match(r'^([-*_]\s*){3,}$', line.strip()):
            if buffer:
                wrapped = textwrap.fill('\n'.join(buffer), width=width)
                result.append(wrapped)
                buffer = []
            
            result.append(line)
            continue
        
        # Check for list items
        list_match = re.match(r'^(\s*)([*+-]|\d+\.)\s', line)
        if list_match:
            # Flush the buffer if we're transitioning to a list
            if buffer and not in_list:
                wrapped = textwrap.fill('\n'.join(buffer), width=width)
                result.append(wrapped)
                buffer = []
            
            in_list = True
            list_indent = len(list_match.group(1)) + len(list_match.group(2)) + 1
            
            # Check if this is a continuation of the previous list item
            if buffer:
                wrapped = textwrap.fill('\n'.join(buffer), width=width, 
                                        initial_indent=' ' * list_indent,
                                        subsequent_indent=' ' * list_indent)
                result.append(wrapped)
                buffer = []
            
            # Add the list item marker
            result.append(line)
            continue
        
        # If we're in a list and this is a continuation (indented line)
        if in_list and line.startswith(' ' * list_indent):
            buffer.append(line.strip())
            continue
        
        # If we were in a list but now we're not
        if in_list and (not line.startswith(' ' * list_indent) or not line.strip()):
            if buffer:
                wrapped = textwrap.fill('\n'.join(buffer), width=width,
                                       initial_indent=' ' * list_indent,
                                       subsequent_indent=' ' * list_indent)
                result.append(wrapped)
                buffer = []
            
            in_list = False
            list_indent = 0
        
        # Check for blank lines - they separate paragraphs
        if not line.strip():
            if buffer:
                wrapped = textwrap.fill('\n'.join(buffer), width=width)
                result.append(wrapped)
                buffer = []
            
            result.append('')
            continue
        
        # Check for indented text (blockquotes or indented paragraphs)
        indent_match = re.match(r'^(\s+)(.+)$', line)
        if indent_match:
            indent = len(indent_match.group(1))
            if buffer:
                wrapped = textwrap.fill('\n'.join(buffer), width=width)
                result.append(wrapped)
                buffer = []
            
            # Preserve the indentation
            wrapped = textwrap.fill(line.strip(), width=width-indent,
                                   initial_indent=' ' * indent,
                                   subsequent_indent=' ' * indent)
            result.append(wrapped)
            continue
        
        # Check for blockquotes
        if line.strip().startswith('>'):
            quote_match = re.match(r'^(\s*>+\s*)(.+)$', line)
            if quote_match:
                prefix = quote_match.group(1)
                content = quote_match.group(2)
                
                if buffer:
                    wrapped = textwrap.fill('\n'.join(buffer), width=width)
                    result.append(wrapped)
                    buffer = []
                
                # Preserve the blockquote marker
                wrapped = textwrap.fill(content, width=width-len(prefix),
                                      initial_indent=prefix,
                                      subsequent_indent=prefix)
                result.append(wrapped)
                continue
        
        # For regular text, add to buffer for paragraph wrapping
        buffer.append(line.strip())
    
    # Flush any remaining content in the buffer
    if buffer:
        if not in_code_block:
            wrapped = textwrap.fill('\n'.join(buffer), width=width)
            result.append(wrapped)
        else:
            result.extend(buffer)
    
    return '\n'.join(result)

if __name__ == "__main__":
    model_name = "Literate"
    model_name = "LiterateTester"
    input_path = f"ldm/ldm_models/{model_name}.md"
    output_path = f"ldm/ldm_models/{model_name}_results/{model_name}.clean.md"
    from utils_pom.util_fmk_pom import read_text, write_text
    
    input_str = read_text(input_path)
    output_str = clean_markdown(input_str)
    write_text(output_path, output_str)