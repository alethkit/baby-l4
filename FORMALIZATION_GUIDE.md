# Baby-L4 Contract Formalization Guide

## Introduction

This guide provides a step-by-step approach to formalizing natural language legal contracts into Baby-L4, a domain-specific language designed for computational law. Baby-L4 enables formal reasoning about legal rules, obligations, and rights while maintaining readability and connection to natural language.

## Overview of Baby-L4 for Contracts

Baby-L4 provides several key constructs for modeling contracts:

- **Classes**: Define entities (parties, objects, concepts)
- **Predicates**: Express relationships and states
- **Rules**: Encode conditional logic and obligations
- **Facts**: State known truths about specific scenarios
- **Assertions**: Verify logical consequences

## Step-by-Step Formalization Process

### Step 1: Identify Core Elements

Begin by extracting the fundamental components from your contract:

1. **Parties**: Who are the actors?
   - Map to classes extending `Party`
   - Example: `class Landlord extends Party`

2. **Objects**: What things are involved?
   - Create classes for physical items, rights, or concepts
   - Example: `class Property`, `class Payment`

3. **Relationships**: How do parties and objects relate?
   - Define predicates for relationships
   - Example: `decl Owns : Party -> Property -> Boolean`

### Step 2: Model Obligations and Rights

Transform contract clauses into rules:

#### Pattern: Basic Obligation
```
Natural Language: "The tenant must pay rent monthly"
Baby-L4:
rule <rentObligation>
for t : Tenant, amount : Integer, d : Date
if LeaseActive t && MonthlyDue d
then MustPay t amount d
```

#### Pattern: Conditional Right
```
Natural Language: "Buyer may reject goods if defective"
Baby-L4:
rule <rejectionRight>
for b : Buyer, g : Goods
if Defective g && WithinInspectionPeriod
then MayReject b g
```

### Step 3: Handle Temporal Conditions

Contracts often involve time-based conditions:

#### Pattern: Deadline
```
decl CurrentDate : Date
decl DateBefore : Date -> Date -> Boolean
decl DaysAfter : Date -> Integer -> Date -> Boolean

rule <paymentDeadline>
for p : Payment, dueDate : Date
if CurrentDate > dueDate && not Paid p
then Overdue p
```

#### Pattern: Duration
```
class Duration
decl Years : Integer -> Duration
decl ValidUntil : Agreement -> Duration -> Boolean

rule <contractExpiry>
for agr : Agreement, d : Duration
if ValidUntil agr d && CurrentDate > d
then not InEffect agr
```

### Step 4: Model Exceptions and Overrides

Legal contracts often have exceptions and hierarchical rules:

#### Pattern: Exception
```
Natural Language: "Must deliver except in case of force majeure"
Baby-L4:
rule <deliveryObligation>
for s : Seller, g : Goods
if ContractActive && not ForceMajeureEvent
then MustDeliver s g

rule <forceMajeureException>
for p : Party
if ForceMajeureEvent
then ExcusedPerformance p
```

#### Pattern: Override (Despite/Notwithstanding)
```
# Rule priority can be modeled through careful predicate design
rule <generalRule>
for x : Entity
if Condition1 x && not SpecialException x
then Consequence1 x

rule <specialException>
for x : Entity
if Condition2 x
then SpecialException x
```

### Step 5: Add Natural Language Connection

Use the lexicon to maintain connection to natural language:

```
lexicon
MustDeliver -> "must_deliver_V2"
ForceMajeure -> "force_majeure_N"
Breach -> "breach_V2"
```

## Common Contract Patterns

### 1. Payment Terms
```
class PaymentTerms
decl Immediate : PaymentTerms
decl Net30 : PaymentTerms

rule <net30Payment>
for buyer : Buyer, amount : Integer, invoiceDate : Date, dueDate : Date
if PaymentTerms buyer Net30 && DaysAfter invoiceDate 30 dueDate
then MustPay buyer amount dueDate
```

### 2. Breach and Remedies
```
decl InBreach : Party -> Agreement -> Boolean
decl MayTerminate : Party -> Agreement -> Boolean

rule <terminationForBreach>
for innocent : Party, breaching : Party, agr : Agreement
if InBreach breaching agr && Counterparty innocent breaching agr
then MayTerminate innocent agr
```

### 3. Warranties
```
decl UnderWarranty : Product -> Boolean
decl MustRepairOrReplace : Seller -> Product -> Boolean

rule <warrantyObligation>
for s : Seller, p : Product
if UnderWarranty p && Defective p
then MustRepairOrReplace s p
```

### 4. Conditions Precedent
```
decl ConditionMet : Condition -> Boolean
decl ObligationTriggered : Obligation -> Boolean

rule <conditionalObligation>
for c : Condition, o : Obligation
if RequiresCondition o c && ConditionMet c
then ObligationTriggered o
```

## Best Practices

### 1. Type Safety
- Use specific types rather than generic ones
- Create class hierarchies that reflect domain relationships
- Example: `class CommercialLease extends Lease`

### 2. Naming Conventions
- Use descriptive names for rules: `<tenantMaintenanceObligation>`
- Predicates should read naturally: `MustMaintain`, `MayOccupy`
- Keep consistent naming patterns

### 3. Modularity
- Group related rules together
- Comment sections clearly
- Consider splitting large contracts into modules

### 4. Testing with Assertions
```
# Always test your formalization with concrete scenarios
decl scenario1 : Contract
fact <setupScenario> ...
assert <expectedOutcome> MustPay tenant 1000 landlord
```

### 5. Documentation
- Comment complex rules
- Explain domain-specific logic
- Reference source contract sections

## Common Pitfalls to Avoid

1. **Over-abstraction**: Keep the formalization close to the original contract language
2. **Missing temporal logic**: Always consider when obligations apply
3. **Ignoring exceptions**: Legal language is full of exceptions - model them explicitly
4. **Ambiguous predicates**: Be precise about what predicates mean

## Example Workflow

Given this contract clause:
> "The Seller shall deliver the Goods to the Buyer within 30 days of receiving the purchase order, unless prevented by circumstances beyond Seller's reasonable control."

Formalization process:
1. Identify entities: Seller, Buyer, Goods, PurchaseOrder
2. Extract obligation: MustDeliver
3. Add temporal constraint: Within 30 days
4. Model exception: Force majeure

Result:
```baby-l4
rule <deliveryObligation>
for s : Seller, b : Buyer, g : Goods, po : PurchaseOrder, deliveryDate : Date
if Received s po && DaysAfter po.date 30 deliveryDate && 
   not BeyondReasonableControl s
then MustDeliver s g b deliveryDate
```

## Verification and Validation

After formalization:
1. Create test scenarios with facts
2. Write assertions for expected outcomes
3. Check for logical consistency
4. Verify all contract provisions are covered
5. Test edge cases and exceptions

## Resources

- See example contracts in the `l4/` directory:
  - `nda.l4` - Non-disclosure agreement
  - `rental_agreement.l4` - Residential lease
  - `employment_contract.l4` - Employment agreement
  - `sales_agreement.l4` - Commercial sales contract

## Conclusion

Formalizing contracts in Baby-L4 requires careful analysis of the legal text and systematic translation into formal rules. The key is maintaining the balance between formal precision and practical readability while ensuring all legal nuances are captured.