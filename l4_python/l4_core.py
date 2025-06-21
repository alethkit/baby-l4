#!/usr/bin/env python3
"""
Baby-L4 Python Implementation
A simplified Python version for contract specification
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from enum import Enum, auto


class L4Type:
    """Base class for L4 types"""
    pass


class Party(L4Type):
    """Base party class"""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class Date(L4Type):
    """Date wrapper"""
    def __init__(self, date: datetime):
        self.date = date
    
    def days_after(self, days: int) -> 'Date':
        return Date(self.date + timedelta(days=days))
    
    def is_before(self, other: 'Date') -> bool:
        return self.date < other.date
    
    def __repr__(self):
        return f"Date({self.date.strftime('%Y-%m-%d')})"


class Obligation(Enum):
    """Deontic modalities"""
    MUST = auto()
    MAY = auto()
    MUST_NOT = auto()


@dataclass
class Rule:
    """Rule representation"""
    name: str
    condition: Callable[..., bool]
    consequence: Callable[..., Any]
    variables: List[str] = field(default_factory=list)
    
    def evaluate(self, context: Dict[str, Any]) -> Optional[Any]:
        """Evaluate rule in given context"""
        try:
            if self.condition(**context):
                return self.consequence(**context)
        except (KeyError, TypeError):
            pass
        return None


@dataclass
class Fact:
    """Fact representation"""
    name: str
    predicate: Callable[..., bool]
    args: Dict[str, Any]
    
    def holds(self) -> bool:
        """Check if fact holds"""
        return self.predicate(**self.args)


@dataclass
class Assertion:
    """Assertion for testing"""
    name: str
    predicate: Callable[..., bool]
    args: Dict[str, Any]
    
    def check(self) -> bool:
        """Check if assertion holds"""
        return self.predicate(**self.args)


class L4Contract:
    """Base contract class"""
    def __init__(self, name: str):
        self.name = name
        self.lexicon: Dict[str, str] = {}
        self.classes: Dict[str, type] = {}
        self.predicates: Dict[str, Callable] = {}
        self.rules: List[Rule] = []
        self.facts: List[Fact] = []
        self.assertions: List[Assertion] = []
        self.context: Dict[str, Any] = {}
        
    def add_lexicon(self, l4_term: str, natural_term: str):
        """Add lexicon mapping"""
        self.lexicon[l4_term] = natural_term
    
    def add_class(self, name: str, cls: type):
        """Register a class"""
        self.classes[name] = cls
    
    def add_predicate(self, name: str, func: Callable):
        """Register a predicate"""
        self.predicates[name] = func
        # Make predicate available in context
        self.context[name] = func
    
    def add_rule(self, rule: Rule):
        """Add a rule"""
        self.rules.append(rule)
    
    def add_fact(self, fact: Fact):
        """Add a fact"""
        self.facts.append(fact)
        # Update context with fact
        for key, value in fact.args.items():
            self.context[key] = value
    
    def add_assertion(self, assertion: Assertion):
        """Add an assertion"""
        self.assertions.append(assertion)
    
    def evaluate_rules(self) -> Dict[str, Any]:
        """Evaluate all rules and return results"""
        results = {}
        for rule in self.rules:
            result = rule.evaluate(self.context)
            if result is not None:
                results[rule.name] = result
        return results
    
    def check_assertions(self) -> Dict[str, bool]:
        """Check all assertions"""
        results = {}
        for assertion in self.assertions:
            try:
                # Try with just the assertion args first
                results[assertion.name] = assertion.predicate(**assertion.args)
            except TypeError:
                # If that fails, try with merged context
                merged_args = {**self.context, **assertion.args}
                try:
                    results[assertion.name] = assertion.predicate(**merged_args)
                except:
                    results[assertion.name] = False
        return results
    
    def to_natural_language(self) -> str:
        """Generate natural language description"""
        output = [f"Contract: {self.name}\n"]
        
        # Rules in natural language
        output.append("Terms:")
        for rule in self.rules:
            output.append(f"- {rule.name}: If conditions are met, then consequences follow")
        
        # Facts
        output.append("\nEstablished Facts:")
        for fact in self.facts:
            output.append(f"- {fact.name}")
        
        # Assertions
        output.append("\nVerifications:")
        results = self.check_assertions()
        for name, result in results.items():
            status = "✓" if result else "✗"
            output.append(f"- {name}: {status}")
        
        return "\n".join(output)


# Helper functions for common patterns
def must(party: Party, action: str, obj: Any = None) -> Dict[str, Any]:
    """Obligation helper"""
    return {
        "type": Obligation.MUST,
        "party": party,
        "action": action,
        "object": obj
    }


def may(party: Party, action: str, obj: Any = None) -> Dict[str, Any]:
    """Permission helper"""
    return {
        "type": Obligation.MAY,
        "party": party,
        "action": action,
        "object": obj
    }


def must_not(party: Party, action: str, obj: Any = None) -> Dict[str, Any]:
    """Prohibition helper"""
    return {
        "type": Obligation.MUST_NOT,
        "party": party,
        "action": action,
        "object": obj
    }