from dataclasses import dataclass, field
from typing import Optional, List
from class_casing import  NTCase, TokenCase

@dataclass
class AbstractClause:
    clause_text: str = ""
    node_name: str = ""
    full_text: str = ""
    
    def __init__(self, clause_text: str, name_text: str = ""):
        self.clause_text = clause_text
        self.node_name = name_text
        full_text = clause_text
        if name_text:
            full_text = f"{self.clause_text} -> {self.node_name}"
        self.full_text = full_text
        

    def __str__(self):
        return self.full_text

    # def __repr__(self):
    #     if self.node_name:
    #         return f"{self.clause_text} ==> {self.node_name}"
    #     return self.clause_text


@dataclass
class AbstractDisjunction(AbstractClause):
    disjuncts: List[AbstractClause] = field(default_factory=list)
    
    def __init__(self, disjuncts: List[AbstractClause]):
        self.disjuncts = disjuncts
        self.full_text = "\n\t\t|\t".join(str(x) for x in self.disjuncts)
        # super.__init__(self.full_text, "")
        


@dataclass
class AbstractRule:
    def __init__(self, lhs: str, rhs: str, priority: int = None):
        self.lhs = lhs
        self.rhs = rhs
        self.priority = priority

    def __str__(self):
        priority_str = ""
        if self.priority:
            priority_str = f".{self.priority}"
        return self.lhs  + priority_str + ": " + self.rhs
    
@dataclass
class AbstractTRule(AbstractRule):
    def __init__(self, lhs: str, rhs: str, priority: int = None):
        super().__init__(lhs, rhs, priority)


    def __str__(self):
        priority_str = ""
        if self.priority:
            priority_str = f".{self.priority}"
        return str(TokenCase(self.lhs))  + priority_str + ": " + self.rhs
    
@dataclass
class AbstractNTRule(AbstractRule):
    def __init__(self, lhs: str, rhs: str, priority: int = None):
        super().__init__(lhs, rhs, priority)

    def __str__(self):
        priority_str = ""
        if self.priority:
            priority_str = f".{self.priority}"
            
        rule_name = self.lhs
        if any(char.isupper() for char in rule_name):
            rule_name = str(NTCase(rule_name))
        print("RHS is ", repr(self.rhs))
        return rule_name  + priority_str + ": " + self.rhs



@dataclass
class AbstractGrammar():
    
    def __init__(self):
        self.rules = []
        self.sections = []
        self.name = "Top Level"
    
    def add_section(self, section_name: str) -> "AbstractSection":
        section = AbstractSection(section_name)
        self.sections.append(section)
        return section
    
    def displayed(self) -> str:
        display = ""
        if len(self.rules) > 0:
            display = f"// === Abstract display: {self.name} ===" + "\n"

            for rule in self.rules:
                display += (str(rule)) + "\n"
            display += f"// === End of abstract section {self.name} ===\n"
        
        for section in self.sections:
            display += section.displayed() + "\n"
        return display
        
    def display(self):
        print(f"=== Abstract display: {self.name} ===")

        for rule in self.rules:
            print(str(rule))
        print(f"=== End of abstract section {self.name} ===")
        
        for section in self.sections:
            section.display()
        
    # def add_rule(self, lhs: str, rhs: str, priority: Optional[int] = None, alias: Optional[str] = None):
    #     if priority:
    #         lhs += f".{priority}"
    #     rule = AbstractRule(lhs, rhs, alias)
    #     self.rules.append(rule)
    
    def add_rule2(self, rule: AbstractNTRule) -> AbstractRule:
        self.rules.append(rule)
        return rule
    
    def add_t_rule(self, lhs: str, rhs: str, priority: Optional[int] = None) ->AbstractTRule:
        rule = AbstractTRule(lhs, rhs, priority)
        self.rules.append(rule)
        return rule
        
    def add_nt_rule(self, lhs: str, rhs: str, priority: Optional[int] = None) -> AbstractNTRule:
        rule = AbstractNTRule(lhs, rhs, priority)
        self.rules.append(rule)
        return rule
    
    def add_nt_rule2(self, lhs: str, rhs: AbstractClause, priority: Optional[int] = None) -> AbstractNTRule:
        rule = AbstractNTRule(lhs, str(rhs), priority)
        print("Adding rule2: ", repr(rule))
        print(f"for {lhs} to {rhs}")
        self.rules.append(rule)
        return rule
    
    def add_disjunctive_rule(self, lhs, disjuncts: List[str]) -> AbstractNTRule:
    
        full_text = "\n\t\t|\t".join(disjuncts)

        return self.add_nt_rule(lhs, full_text)

       
        
    def add_comment(self, comment):
        self.rules.append("//")
        self.rules.append("// " + comment)
        
    def add_space(self, spacer):
        self.rules.append(spacer)

@dataclass
class AbstractSection(AbstractGrammar):
    def __init__(self, section_name: str):
        self.name = section_name
        self.rules = []
        self.sections = []

    