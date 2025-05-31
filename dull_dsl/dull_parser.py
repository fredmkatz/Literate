from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Any
from abc import ABC
import re

import os
from utils.util_fmk import write_text
from utils.util_json import as_json, write_yaml
from utils.util_fmk import create_fresh_directory

from emoji import emoji_list, replace_emoji

# from utils.util_json_pom import as_json
# from utils.util_fmk_pom import as_yaml


from utils.util_fmk import read_lines


from dull_dsl.dull_parser_classes import (
    PartStarter,
    TypedLine,
    Clause,
    ClauseLine,
)


from dull_dsl.dull_parser_core import DocPart

all_clauses_by_priority = None
part_plurals = None
part_parts = None


def parse_model_doc(dull_specs: Dict, model_doc_path: str) -> DocPart:

    doc_part = DocPart("Document", None)
    current_part = doc_part
    current_part_type = "Document"

    global all_clauses_by_priority, part_plurals, part_parts
    all_clauses_by_priority = dull_specs["all_clauses_by_priority"]
    part_plurals = dull_specs["part_plurals"]
    part_parts = dull_specs["part_parts"]

    print(f"PARSING {model_doc_path}")
    current_eligible_parts = part_parts.get(current_part.part_type)

    lines = read_lines(model_doc_path)

    # note. Looping through all lines, but
    # will have inner loops to collect text paras and blocks;
    # those inner loops will alter k
    open_elaboration = []
    open_paragraph = []
    next_k = 0
    while next_k < len(lines):
        line = lines[next_k]
        next_k += 1

        typed_line = assess_line(line)
        type_label = typed_line.type_label
        line_Type = typed_line.line_Type  # the object for the LineType

        # print(f"Found {typed_line}")
        # if "AnnotationType" in str(typed_line):
        #     print("STOPPING")
        #     next_k = len(lines) + 10
        #     break

        # Collect consecutive loose text blocks, blank lines, and code blocks into elaborations
        if type_label == "BLANK_LINE":
            # a blank line signals the end of a paragraph
            # if the paragraph is not empty, add it to the current elaboration
            if open_paragraph:
                # print("Closing paragraph")
                # print("..open_paragraph: ", open_paragraph)
                paragraph = TypedLine("PARAGRAPH", None, open_paragraph)
                open_elaboration.append(paragraph)
                open_paragraph = []  # reset the paragraph
            continue
        if type_label == "TEXT_LINE":
            # current_part.add_line(typed_line)  # for text-lines and blank-lines
            open_paragraph.append(typed_line)
            continue

        if type_label == "CODE_FENCE":  # just read until end of block, accum lines
            if open_paragraph:
                # print("Closing paragraph for code block")
                # print("..open_paragraph: ", open_paragraph)
                paragraph = TypedLine("PARAGRAPH", None, open_paragraph)
                open_elaboration.append(paragraph)
                open_paragraph = []  # reset the paragraph
            # print(f"Starting code bock - for label {type_label}")

            # note: next_k has already been incremented at the top of the loop
            (next_k, extra_text) = consume_through("CODE_FENCE", lines, next_k)
            # if extra_text:
            # print("FOUND CODE BLOCK:", extra_text)
            typed_line.extra_text = extra_text

            # current_part.add_line(typed_line)
            open_elaboration.append(typed_line)  # add the code block to the elaboration
            continue  # proceed with main loop.

        # if we find something other than a blank line or text line, we need to close any open paragraph
        # or open  elaboration
        # and add it to the current part
        if open_paragraph:
            paragraph = TypedLine("PARAGRAPH", None, open_paragraph)
            open_elaboration.append(paragraph)
            open_paragraph = []
        if open_elaboration:
            # print("Closing elaboration on finding Something Special")
            # print("..open_elaboration: ", open_elaboration)
            elaboration = TypedLine("ELABORATION", None, open_elaboration)

            current_part.add_line(
                elaboration
            )  # add the elaboration to the current part
            # print("..added Elaboration to current part (for Something Special): ", elaboration)
            open_paragraph = []  # reset the paragraph
            open_elaboration = []
        # for all clauses and headers, except text and blanks, gather addiional text
        (next_k, extra_text) = consume_while("TEXT_LINE", lines, next_k)
        if extra_text:
            typed_line.extra_text = extra_text
            # print("FOUND EXTRA TEXT")
            # print("..now included in: ", typed_line)

        # current_part.add_line(typed_line)

        class_to_start = ""
        part_type = ""
        if isinstance(line_Type, PartStarter):
            class_to_start = line_Type.class_started
            part_type = class_to_start
            # print(f"For {typed_line}\n  new: {class_to_start}")

        if part_type:  # i.e not just text or a minor clause
            # print(f"Found new part: {part_type}")
            while part_type not in current_eligible_parts:
                # print(f"..But {part_type} not eligible for {current_part_type}")
                parent_part = current_part.parent_part
                if not parent_part:  # doesn't seem to belong anywere
                    # print(f"..But {line_type} doesn't belong anywhere; placing in Document")
                    break
                current_part = parent_part
                current_part_type = parent_part.part_type
                current_eligible_parts = part_parts.get(current_part_type, [])
            # print(
            #     f"... {part_type} does fit into {current_part_type}; creating subpart"
            # )
            new_part = create_doc_part(part_type, current_part)
            current_part = new_part
            current_part_type = part_type
            current_eligible_parts = part_parts.get(part_type, [])
            ## .. and then put the line into the new current part
        current_part.add_line(typed_line)  # for text-lines and blank-lines
        if typed_line.type_label in ["TEXT_LINE", "PARAGRAPH", "ELABORATION"]:
            current_part.add_line(typed_line)
            # print(f"Directly Added {typed_line} to {current_part_type}")
    return doc_part
    # displayed = doc_part.displayed()
    # return displayed


def consume_until(
    final_label: str, lines: List[str], next_k: int
) -> Tuple[int, List[str]]:
    extra_text = []
    while next_k < len(lines):
        line = lines[next_k]
        typed_line = assess_line(line)
        type_label = typed_line.type_label
        # print("Consumed through  {final_label}: ", typed_line)
        extra_text.append(typed_line.content)
        next_k += 1  # i.e. consumed the end marker

        if type_label == final_label:  # time to wrap the code block
            break
    return (next_k, extra_text)


def consume_through(
    final_label: str, lines: List[str], next_k: int
) -> Tuple[int, List[str]]:
    extra_text = []
    first = True
    while next_k < len(lines):
        line = lines[next_k]
        typed_line = assess_line(line)
        type_label = typed_line.type_label
        # print(f"Consumed through  {final_label}: ", typed_line)
        extra_text.append(typed_line.content)
        next_k += 1  # i.e. consumed the end marker

        if not first and type_label == final_label:  # time to wrap the code block
            break
        first = False
        # print(f"{type_label} != {final_label}. continuing")
    return (next_k, extra_text)


def consume_while(
    final_label: str, lines: List[str], next_k: int
) -> Tuple[int, List[str]]:
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
    # print(f"creating DocPart for {line_type}")
    chunk = DocPart(line_type, parent_part)
    parent_part.add_doc_part(chunk)
    return chunk


def assess_line(line: str) -> TypedLine:
    trimmed = line.strip()
    if trimmed == "":
        return TypedLine("BLANK_LINE", None, trimmed)

    # get rid of underscores used for italics

    trimmed_bare = trimmed  # will be line wo emojis
    emojis = emoji_list(trimmed)
    if emojis:
        # print(f"found EMOJIS {emojis}: {trimmed}")
        trimmed_bare = replace_emoji(trimmed, "").strip()

    # for lineType in all_line_types:
    for lineType in all_clauses_by_priority:
        if lineType.matches(trimmed_bare):
            # print(f"found a {lineType} line")

            # but put the line with original emojis into the result
            # TODO. retreated to bare until emojis work ok
            typed_line = ClauseLine(lineType.line_label, lineType, trimmed_bare)

            # print(f"assess() returning {repr(typed_line)}")
            return typed_line

    if trimmed.startswith("```"):
        return TypedLine("CODE_FENCE", None, trimmed)
    return TypedLine("TEXT_LINE", None, trimmed)
