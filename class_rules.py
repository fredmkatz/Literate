from __future__ import annotations

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from dataclasses import is_dataclass, fields, field


@dataclass
class Rule:
    name: str
    text: str
    
    def __str__(self):
        core =  f"{self.name}:\t{self.text}"
        return core

@dataclass
class DisjunctiveRule(Rule):
    text: str = field(init=False)
    disjuncts: List[str] 
    
    
    def __init__(self, name, disjuncts):
        self.name = name
        self.disjuncts = disjuncts
        full_text = "\n\t\t|\t".join(self.disjuncts)

        super().__init__(name, full_text)
        
class RuleComment(Rule):
    comment: str = ""
    
    def __init__(self, comment):
        self.comment  = comment
        super().__init__("---",  "// " + comment)

        