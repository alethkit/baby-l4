# L4 Language Reference

## Overview

L4 is a family of domain-specific languages designed for computational law. This reference covers both Baby-L4 (the current implementation) and the broader L4 vision.

## Baby-L4 vs Full L4

### Baby-L4
- Current implementation in this repository
- Core abstract syntax for legal concepts
- Focus on logical rules and type safety
- Supports formal verification via SMT solvers
- Natural language generation through GF (Grammatical Framework)

### Full L4
- Extended language with additional features
- Modules and imports
- Temporal logic and state machines
- Advanced defeasibility reasoning
- Contract templates and parameterization

## Baby-L4 Syntax Reference

### Basic Structure

```baby-l4
# l4version 0.3.6

lexicon
# Natural language mappings

class definitions
# Entity definitions

declarations
# Predicate and function declarations

rules
# Logical rules

facts
# Known truths

assertions
# Verification conditions
```

### Classes

Define entities and their relationships:

```baby-l4
class Party
class Company extends Party
class Individual extends Party

class Contract {
    parties: [Party]
    value: Integer
    date: Date
}
```

### Predicates

Boolean-valued functions expressing relationships:

```baby-l4
decl Owns : Party -> Asset -> Boolean
decl MustPay : Party -> Integer -> Party -> Date -> Boolean
decl ValidContract : Contract -> Boolean
```

### Rules

Conditional logic with typed variables:

```baby-l4
rule <ruleName>
for var1 : Type1, var2 : Type2
if condition
then conclusion
```

Example:
```baby-l4
rule <ownershipTransfer>
for buyer : Party, seller : Party, asset : Asset
if ValidSale buyer seller asset && PaymentComplete buyer seller
then Owns buyer asset && not Owns seller asset
```

### Facts

State known truths:

```baby-l4
fact <factName>
predicate expression

fact <contractValid>
ValidContract saleContract2024
```

### Assertions

Verify logical consequences:

```baby-l4
assert <assertionName>
expression to verify

assert <ownershipVerified>
Owns alice property123
```

### Lexicon

Map formal terms to natural language:

```baby-l4
lexicon
Landlord -> "landlord_N"
MustPay -> "must_pay_V2"
ValidContract -> "valid_contract_A"
```

## Type System

### Basic Types
- `Boolean`: Truth values
- `Integer`: Whole numbers
- `Float`: Decimal numbers
- `String`: Text values
- `Date`: Temporal points
- `Duration`: Time periods

### Class Types
- User-defined classes
- Inheritance hierarchy
- Record-like fields

### Function Types
- Predicates: `T1 -> T2 -> ... -> Boolean`
- Functions: `T1 -> T2 -> ... -> TResult`

## Advanced Features

### Temporal Logic

Model time-dependent rules:

```baby-l4
decl CurrentDate : Date
decl DateBefore : Date -> Date -> Boolean
decl ValidDuring : Contract -> Date -> Date -> Boolean

rule <contractValidity>
for c : Contract, start : Date, end : Date
if CurrentDate >= start && CurrentDate <= end
then ValidDuring c start end
```

### Defeasibility

Model exceptions and overrides:

```baby-l4
# General rule
rule <generalObligation>
for p : Party
if Condition1 p
then Obligation p

# Exception
rule <exceptionToObligation>
for p : Party
if Condition1 p && SpecialCircumstance p
then not Obligation p
```

### Quantifiers

Universal and existential quantification:

```baby-l4
# Universal (forall)
rule <allPartiesMustSign>
for c : Contract
if ValidContract c
then forall p : Party . PartyTo p c --> HasSigned p c

# Existential (exists)
rule <needsWitness>
for c : Contract
if HighValueContract c
then exists w : Witness . Witnessed w c
```

## Verification

### SMT Backend

Baby-L4 can verify assertions using SMT solvers:

```baby-l4
assert {SMT: valid}
expression

assert {SMT: consistent}
expression
```

### Model Checking

Verify temporal properties:

```baby-l4
# Eventually
assert <eventuallyPaid>
F (PaymentComplete buyer seller)

# Always
assert <alwaysOwned>
G (Owns owner asset --> not Abandoned asset)
```

## Natural Language Generation

Baby-L4 integrates with GF for NLG:

```bash
stack run l4 gf en contract.l4
```

This generates English explanations of rules.

## Module System (Full L4)

The full L4 vision includes modules:

```l4
MODULE Contract.Sales
IMPORT Contract.Base
EXPORT SalesContract, validateSale

SOURCE UCC {
    article = 2,
    url = "https://..."
}
```

## Integration Points

### Decision Tables
Baby-L4 can import/export DMN decision tables

### Workflow
Integration with BPMN for process modeling

### Expert Systems
Export to Prolog-style rules

## Common Patterns

### State Machines
```baby-l4
class State
decl Initial : State
decl Final : State
decl Transition : State -> Event -> State -> Boolean
```

### Deontic Logic
```baby-l4
# Obligations
decl Must : Party -> Action -> Boolean

# Permissions  
decl May : Party -> Action -> Boolean

# Prohibitions
decl MustNot : Party -> Action -> Boolean
```

## Resources and Links

### Documentation
- [SMUCCLAW Project](https://github.com/smucclaw)
- [Baby-L4 Repository](https://github.com/smucclaw/baby-l4)
- [L4 DSL Repository](https://github.com/smucclaw/dsl)

### Academic Papers
- "L4: A Legal DSL for Computational Law"
- "Formal Verification of Legal Contracts"

### Related Projects
- Catala (French tax law DSL)
- Accord Project (Smart legal contracts)
- OpenFisca (Rules as code)

## Quick Reference Card

| Construct | Syntax | Example |
|-----------|--------|---------|
| Class | `class Name` | `class Contract` |
| Inheritance | `class Child extends Parent` | `class Lease extends Contract` |
| Declaration | `decl name : Type` | `decl Valid : Contract -> Boolean` |
| Rule | `rule <name> for ... if ... then ...` | `rule <validity> for c : Contract if Signed c then Valid c` |
| Fact | `fact <name> expression` | `fact <signed> Signed contract123` |
| Assert | `assert <name> expression` | `assert <valid> Valid contract123` |
| Forall | `forall x : T . P x` | `forall p : Party . Must p SignContract` |
| Exists | `exists x : T . P x` | `exists w : Witness . Saw w Signing` |

## Future Directions

L4 continues to evolve with planned features:
- Probabilistic reasoning
- Multi-party protocols
- Regulatory compliance checking
- Integration with blockchain smart contracts
- Advanced explanation generation