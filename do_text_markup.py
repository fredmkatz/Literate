#!/usr/bin/env python3
"""
Text Markup Preprocessor for ANTLR

This program adds start and end markers to sections of text that should be treated as
"straight text" rather than formal language elements in an ANTLR parser.

The program uses a state machine approach with simplified pattern matching to process
the input file line by line, identifying special lines and marking up text sections.
"""

"""ToDo
- fix data types
- count line types
"""

import re
import sys
from pathlib import Path
from typing import List

START_TEXT = "<<<"
END_TEXT = ">>>"
all_marked_lines = []
all_headers = []
all_annotations = [ ]   

import re
from util_antlr import path_for, input_doc_path

def do_markup(ppass:str, grammar: str, document: str) -> None:
    """
    Process a renamed markdown file and output marked version.
    """
    print(f"ppass is {ppass}, grammar is {grammar}, doc is {document}")
    input_path = path_for(ppass, grammar, "outputs", document, "_01.renamed.md")
    print(f"Input path for marked is -  {input_path}")


    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found for {grammar} - {document}: {input_path}")
    
    output_path = path_for(ppass, grammar, "outputs", document, "_01a.marked.md")
    print(f"New output path for marked is -  {output_path}")

    do_text_markup(str(input_path), str(output_path), debug=False)
    
    return Path(output_path)


def do_text_markup(input_path, output_path, debug=False):
    """
    Process a file and add text markup markers to indicate sections that should be treated
    as straight text rather than formal language elements.
    
    Args:
        input_path (str): Path to the input file
        output_path (str): Path where the marked-up output should be written
        debug (bool): Whether to enable debug logging
    """
    
    global all_headers
    global all_annotations
    
    print(f"input path is: {input_path}")
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Process the lines
    marked_lines = markup_text_lines(lines, debug)
    
    # Write the processed content to the output file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(marked_lines)

    output_path2 = output_path.replace("marked.md", "marked_heads.md")
    with open(output_path2, 'w', encoding='utf-8') as file:
        file.writelines(all_headers)

    output_path3 = output_path.replace("marked.md", "marked_notes.md")
    with open(output_path3, 'w', encoding='utf-8') as file:
       file.writelines(all_annotations)


def debug_print(message, enabled=False):
    """
    Print a debug message if debugging is enabled.
    
    Args:
        message (str): The message to print
        enabled (bool): Whether debugging is enabled
    """
    if enabled:
        print(f"DEBUG: {message}")



def new_identify_line_type(line, debug=False):
    """
    Simplified line type identification based on starting characters.
    
    Args:
        line (str): The line to check
        debug (bool): Whether to enable debug logging
        
    Returns:
        tuple: (line_type, parts) where parts is a dictionary containing relevant line parts
    """
    line = line.strip()
    
    # Skip empty lines
    if not line:
        return 'blank', {}
    
    # Initialize parts dictionary
    parts = {}
    
    # Check for section header (starting with #)
    header_chars = ["#", "_", "__", "-"]
    is_header = False
    for char in header_chars:
        if line.startswith(char):
            is_header = True
    
    if is_header:
        header = None
        oneliner = None
        parenthetical = None
        
        # Find the dash that separates the header from oneliner (if any)
        dash_pos = line.find(' - ')
        if dash_pos > 0:
            # Header with oneliner
            header = line[:dash_pos].strip()
            oneliner = line[dash_pos + 3:].strip()
        else:
            # Header without oneliner
            header = line
            
        # Check for parenthetical at the end
        parenthetical = None
        if oneliner and '(' in oneliner and oneliner.endswith(')'):
            parenthetical_start = oneliner.rfind('(')
            parenthetical = oneliner[parenthetical_start + 1:-1]
            oneliner = oneliner[:parenthetical_start].strip()
            
        parts = {'header': header, 'oneliner': oneliner, 'parenthetical': parenthetical}

        # print("NILT returning: header + ", parts)
        # print("\tfor: ", line)
        return 'header', parts
    
    
    # Check for annotation (containing :)
    elif ':' in line:
        colon_pos = line.find(':')
        if colon_pos > 0:
            label = line[:colon_pos].strip()
            value = line[colon_pos + 1:].strip()
            parts = {'label': label, 'value': value}
            debug_print(f" - Found annotation with label: {label}", debug)
            return 'annotation', parts
    
    # Default: plain text
    return 'text', {'content': line}



all_collected_lines = []

""" States are:
    - collecting_text: - persists until the next header or annotation
            Meant for raw text (as in elaborations)
            When released, add START and END text markers
    - collcting_annotation: - persists until the next header or annotation OR blank line
            For annotations that extend beyond one line (either code or text)
            When released: checks whether the first line has START text in front
            If so, adds END_TEXT to the end
    - collecting_header:  - persists until the next header or annotation OR blank line
            For headers with a multiline one-liner
            On first line, START added after the NAME -  portion, if there's a one
            liner.
            When released, END text is added to the end 
            BUT. if there's a parenthetical at the end. the END TEXT makre is added
            between the one-liner and the parenthetical

"""
current_state = "collecting_text"

def markup_text_lines(lines: List[str], debug=False) -> List[str]:
    """
    Process the input lines using a state machine approach with simplified pattern matching.
    
    Args:
        lines (list): List of input lines
        debug (bool): Whether to enable debug logging
        
    Returns:
        list: List of processed lines with markup markers
    """
    # List of annotation labels that should NOT be marked as text
    non_text_annotations = ['parenthetical'
                            , 'Subtypes'
                            , "SubtypeOf"
                            , "BasedOn"
                            , "Subtypes"
                            , "DependentOf"
                            , "InverseOf"
                            , "Dependents"
                            , "Subtyping"
                        
                            
                            ]
    

    
    # Track all annotation labels seen for debugging
    all_annotation_labels = set()
    all_normal_labels = set()
    all_line_types = set()
    
    normal_non_text_annotations = list( map(normalize_label, non_text_annotations))
    # print("Normal nottext: ", normal_non_text_annotations)
    
    global all_marked_lines
    global all_collected_lines
    global current_state

    # Initialize state
    in_text_section = False
    special_line_type = None
    special_parts = None
    i = 0
    for line in lines:
        i += 1
        # line = lines[i]

        # Identify the type of the current line
        line_type, parts = new_identify_line_type(line, debug)
        
        all_line_types.add(line_type)
        if debug and line_type == 'annotation':
            normal_label = normalize_label(parts['label'])
            all_annotation_labels.add(parts['label'])
            all_normal_labels.add(normal_label)
        
        
        
        debug_print(f"{current_state} - Found {line_type}: {line.strip()}", debug)

        if line_type  == "blank":
            releaseAny('collecting_text')  # a blank line closes any collection, except for text
            current_state = "collecting_text"  # and next lines are presumed to be text
            collect(line)    # save this line, now as text
            
        elif line_type == "text":
            # release nothing, collect into whatever is being collected
            collect(line)   # save this line, now as text
            # and leave the state as it was
        
        # for annotations:
        #  If the value is any old text, then next lines may add to that
        #  If the value is non-text, next lines may add to that, too
        #  So, in either case, start collecting with the frist line
        #  But: note whether the annoation is non-text or text. That 
        #  will determine whether the value should be wrapped in text markers
        
        elif line_type == "annotation":
            releaseAny()    # closes anything, including text
            # print(f"Annotation parts are {parts}")
            text_or_not = "Text"
            label = parts.get("label")
            value = parts.get("value")
            
            annotation_line = line
            if normalize_label(label)  not in normal_non_text_annotations: # I.E has a text value
                # if value is free text, add the START marker befoe the value.
                # the END marker will be added by release(), based on the START marker
                # being present
                annotation_line = label + ": " + START_TEXT + value  + "\n"
            else:
                # If value is meant to be parsed, just add it
                # more can be added - up to a blank or special lize -
                # No END text marker will be added because there's no START TEXT
                annotation_line = line
            current_state = "collecting_annotation" 
        
            collect(annotation_line)   # save this line, now as text
           
            
        elif line_type == "header":
            releaseAny()    # closes anything, including text
            header_line = ""
            header = parts.get('header')
            oneliner = parts.get('oneliner')
            # Note. Not handling the parenthetical here
            # waiting until release() in case there are several lines
            # with parens at the end
            parenthetical = parts.get('parenthetical')
            # print(f'For header, parts are {parts}')


            header_line = header    # i.e. just ### SectionName or _ Class
            
            # if it has a parenthetical, that means there's no additional content to wait for.
            if parenthetical:
                if oneliner:
                    # if there's a oneliner, add it with text markers
                    header_line += " - " + START_TEXT + oneliner + END_TEXT 
                    # otherwise just add the datataype
                header_line +=  " (" + parenthetical + ")" + "\n"   
                #
                # and, if there's a parenthetical, the line is ready for release on its own
                collect(header_line)          
                
                current_state = "collecting_code"   # so that END_TEXT won't be added
                releaseAny()      
                current_state = "collecting_text"   # to restart normal operations
            else:
                # If there's no parenthetical, whether theres a one liner or not, allow for more
                # to be collected

                # if there's no parenthetical, then add the oneliner with just the start text
                header_line += " - " + START_TEXT 
                if oneliner:
                    header_line += oneliner
                header_line += "\n"
                collect(header_line)    #without releasing; waiting for more
                current_state = "collecting_header"

            # print(f"final header line: {header_line}")

        else:
            debug_print(f"What line type: {line}")

    # at end of file
    releaseAny()
 #  For , parts are {
     # 'header': '- allSubjects', 
     # 'oneliner': 'list of all classes in the model, as ordered in the definition of the model.', 
     # 'parenthetical': 'List of Classes'}   
     
    # Print all annotation labels seen
    # debug_print(f"All annotation labels seen: {all_annotation_labels}", True)
    # for label in all_annotation_labels:
    #     print(label)
    # print()
    # debug_print(f"All normal labels seen: {all_normal_labels}", True)
    # for label in sorted(all_normal_labels):
    #     print(label)
    
    # print()
        
    debug_print(f"All line types seen: {all_line_types}", True)
    for ltype in all_line_types:
        print(ltype)

    return all_marked_lines

def normalize_label(label: str):
    normal = label.replace("]", "").replace("[", "")
    normal = normal.lower()
    normal = normal.replace(" ", "")
    return normal

def collect(line: str):
    global all_collected_lines
    
    all_collected_lines.append(line)
    # print(f"==> yielding {all_collected_lines}")
   
def releaseAny(excepting:str = ''):
    global all_marked_lines
    global all_collected_lines
    global current_state
    
    global all_headers
    global all_annotations
    
    if not all_collected_lines:
        return
    
    if current_state == excepting:
        return
    # print(f"{current_state} ==> RELEASING {all_collected_lines}")
    if current_state == "collecting_text" or current_state == "collecting_header":
        first_line = all_collected_lines[0]
        if not START_TEXT in first_line:
            first_line = START_TEXT + all_collected_lines[0]
            all_collected_lines[0] = first_line
        last_line = all_collected_lines[-1]
        #
        #  to do: check for parenthetical in headers
        last_line = last_line.replace("\n", END_TEXT + "\n")
        all_collected_lines[-1] = last_line
        # print("LAST LINE OF CLOSED TEXT", last_line)

    if current_state == "collecting_annotation":
        first_line = all_collected_lines[0]
        if START_TEXT in first_line: # for text value type notes
            last_line = all_collected_lines[-1]
            last_line = last_line.replace("\n", END_TEXT + "\n")
            all_collected_lines[-1] = last_line

    # and always add a semicolon before the newl ine
    last_line = all_collected_lines[-1]
    last_line = last_line.replace("\n", " ; " + "\n")
    all_collected_lines[-1] = last_line

    # To supply additional files
    if current_state == "collecting_annotation":
        all_annotations.extend(all_collected_lines)
        n_annotations = len(all_annotations)
        # print(f"{n_annotations} annotation lines")
    if current_state == "collecting_header":
        all_headers.extend(all_collected_lines)
        n_headers = len(all_headers)
        # print(f"{n_headers} header lines")


    all_marked_lines.extend(all_collected_lines)
    all_collected_lines = []
    

def extract_parenthetical(lines, debug=False):
    """
    Check if the collected lines end with a parenthetical and extract it if present.
    
    Args:
        lines (list): Collected lines
        debug (bool): Whether to enable debug logging
        
    Returns:
        tuple: (parenthetical or None, lines with parenthetical removed)
    """
    if not lines:
        return None, lines
    
    # Check the last line for a parenthetical
    last_line = lines[-1].rstrip()
    
    if last_line.endswith(')') and '(' in last_line:
        parenthetical_start = last_line.rfind('(')
        parenthetical = last_line[parenthetical_start + 1:-1]
        
        # Remove the parenthetical from the last line
        lines[-1] = last_line[:parenthetical_start].rstrip() + '\n'
        
        debug_print(f"Extracted parenthetical: {parenthetical}", debug)
        return parenthetical, lines
    
    return None, lines



def main():
    """
    Main function for testing the text markup processor.
    """
    debug = False  # Set to True to enable debug logging
    
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        # Default test paths
        input_path = "TextMarkupExample.md"
        output_path = "TextMarkupExample_marked.md"
    
    try:
        do_text_markup(input_path, output_path, debug)
        print(f"Successfully processed {input_path} and wrote output to {output_path}")
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()