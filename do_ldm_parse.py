from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Any
from abc import ABC
import re

from emoji import emoji_list, replace_emoji
# from utils_pom.util_json_pom import as_json
# from utils_pom.util_fmk_pom import as_yaml


from utils_pom.util_fmk_pom import read_lines
from ldm_parse_bits import (
    parse_attribute_reference,
    parse_full_header,
    parse_input_line,
    parse_name,
    parse_input_line2,
    parse_name_list,
    parse_trivial,
)

from ldm_parse_ldm import part_parts, part_labels, all_line_types

from ldm_parse_core import (
    DocPart,
    PartStarter,
    TypedLine,
    
    ComponentChunk,
    FormulaChunk,


)

# exit(0)

def parse_ldm(path: str):
    doc_part = DocPart("Document")
    current_part = doc_part
    current_part_type = "Document"
    current_eligible_parts = part_parts.get(current_part.part_type)
    lines = read_lines(path)
    in_code_block = False
    
    # note. Looping through all lines, but
    # will have inner loops to collect text paras and blocks;
    # those inner loops will alter k
    next_k = 0
    while next_k < len(lines):  
        line = lines[next_k]
        next_k += 1
    
        typed_line = assess_line(line)
        type_label = typed_line.type_label
        line_Type = typed_line.line_Type  # the object for the LineType

        print(f"Found {typed_line}")

        if type_label in ["BLANK_LINE", "TEXT_LINE"]:
            current_part.add_line(typed_line)  # for text-lines and blank-lines
            continue

        # for all clauses and headers, except text and blanks, gather addiional text
        (next_k, extra_text) = consume_while("TEXT_LINE", lines, next_k)
        if extra_text:
            typed_line.extra_text = extra_text
            print("FOUND EXTRA TEXT")
            print("..now included in: ", typed_line)

        # current_part.add_line(typed_line)

        class_to_start = ""
        part_type = ""
        if isinstance(line_Type, PartStarter):
            class_to_start = line_Type.class_started
            part_type = class_to_start
            print(f"For {typed_line}\n  new: {class_to_start}")
        

        # note, no part_type for text and blank lines and code_block
        if part_type == "CodeBlock":  # just read until end of block, accum lines
            print(f"Starting code bock - {part_type} with label {type_label}")
            
            # note: next_k has already been incremented at the top of the loop
            (next_k, extra_text) = consume_until("CodeBlock_Head", lines, next_k)
            if extra_text:
                print("FOUND CODE BLOCK:", extra_text)
            typed_line.extra_text = extra_text
            
            current_part.add_line(typed_line)
            continue    # proceed with main loop.


        if part_type: # i.e not just text or a minor clause
            print(f"Found new part: {part_type}")
            while part_type not in current_eligible_parts:
                print(f"..But {part_type} not eligible for {current_part_type}")
                parent_part = current_part.parent_part
                if not parent_part:  # doesn't seem to belong anywere
                    # print(f"..But {line_type} doesn't belong anywhere; placing in Document")
                    break
                current_part = parent_part
                current_part_type = parent_part.part_type
                current_eligible_parts = part_parts.get(current_part_type, [])
            print(
                f"... {part_type} does fit into {current_part_type}; creating subpart"
            )
            new_part = create_doc_part(part_type, current_part)
            current_part = new_part
            current_part_type = part_type
            current_eligible_parts = part_parts.get(part_type, [])
            ## .. and then put the line into the new current part
        current_part.add_line(typed_line)  # for text-lines and blank-lines
    print("Displaying parsed document")
    doc_part.display()
    return doc_part.process()

def consume_until(final_label: str, lines: List[str], next_k: int) -> Tuple[int, List[str]]:
    extra_text = []
    while next_k < len(lines):
        line = lines[next_k]
        typed_line = assess_line(line)
        type_label = typed_line.type_label
        print("Consumed through  {final_label}: ", typed_line)
        extra_text.append(typed_line.content)
        next_k += 1 # i.e. consumed the end marker

        if type_label == final_label: # time to wrap the code block
            break
    return (next_k, extra_text)
    
def consume_while(final_label: str, lines: List[str], next_k: int) -> Tuple[int, List[str]]:
    extra_text = []
    while next_k < len(lines):
        next_line = lines[next_k]
        typed_next_line = assess_line(next_line)
        next_line_label = typed_next_line.type_label
        if next_line_label != final_label:
            break
        # so. text just after the minor clause. 
        # gather it up
        extra_text.append(typed_next_line.content)
        next_k += 1
    return (next_k, extra_text)

def create_doc_part(line_type, parent_part) -> DocPart:
    # print(f"creating docpart for {line_type}")
    if line_type == "LDM":
        return ComponentChunk(line_type, parent_part)
    if line_type.startswith("Section"):
        return ComponentChunk(line_type, parent_part)

    if line_type == "Class":
        return ComponentChunk(line_type, parent_part)
    if line_type == "Attribute":
        return ComponentChunk(line_type, parent_part)
    if line_type == "AttSection":
        return ComponentChunk(line_type, parent_part)
    if line_type == "Derivation":
        return FormulaChunk(line_type, parent_part)
    if line_type == "Default":
        return FormulaChunk(line_type, parent_part)
    if line_type == "Constraint":
        return FormulaChunk(line_type, parent_part)
    return DocPart(line_type, parent_part)


def assess_line(line: str) -> TypedLine:
    trimmed = line.strip()
    if trimmed == "":
        return TypedLine("BLANK_LINE", None, trimmed)

    # get rid of underscores used for italics

    emojis = emoji_list(trimmed)
    if emojis:
        # print(f"found EMOJIS {emojis}: {trimmed}")
        trimmed = replace_emoji(trimmed, "").strip()

    for lineType in all_line_types:
        if lineType.matches(trimmed):
            return TypedLine(lineType.line_label, lineType, trimmed)

    return TypedLine("TEXT_LINE", None, trimmed)


if __name__ == "__main__":
    path = "samples/LDMMeta.md"
    parse_ldm(path)
