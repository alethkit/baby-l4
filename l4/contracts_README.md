# Baby-L4 Contract Examples

This directory contains example legal contracts formalized in Baby-L4. These examples demonstrate how to translate natural language legal agreements into formal, machine-readable specifications.

## Overview of Examples

### 1. Non-Disclosure Agreement (`nda.l4`)

**Purpose**: Mutual confidentiality agreement between parties

**Key Concepts Demonstrated**:
- Confidential information classification
- Disclosure and protection obligations
- Permitted use restrictions
- Need-to-know exceptions
- Time-based validity
- Breach conditions

**Notable Features**:
```baby-l4
# Exception for public information
rule <publicInfoException>
for info : Information
if IsPublic info
then not exists ci : ConfidentialInformation . ci == info

# Need-to-know basis disclosure
rule <needToKnowException>
for rp : ReceivingParty, ci : ConfidentialInformation, emp : Party, ap : AuthorizedPurpose
if MustProtect rp ci && HasNeedToKnow emp ci ap
then not MustNotDisclose rp ci emp
```

### 2. Rental Agreement (`rental_agreement.l4`)

**Purpose**: Residential lease agreement between landlord and tenant

**Key Concepts Demonstrated**:
- Monthly payment obligations
- Property maintenance duties
- Security deposit handling
- Eviction conditions
- Normal wear and tear exceptions
- Notice requirements

**Notable Features**:
```baby-l4
# Late payment tracking
rule <latePaymentRule>
for t : Tenant, p : Payment, d : Date
if CurrentDate == d && DateBefore p.dueDate d && 
   not HasPaid t p && p.amount > 0
then LatePayment t p

# Security deposit refund logic
rule <depositRefundPartial>
for l : Lease, lord : Landlord, t : Tenant, damagesCost : Integer
if not LeaseActive l && l.landlord == lord && l.tenant == t &&
   CausedDamage t l.property && damagesCost > 0 &&
   damagesCost < l.property.securityDeposit
then MustRefundDeposit lord t (l.property.securityDeposit - damagesCost)
```

### 3. Employment Contract (`employment_contract.l4`)

**Purpose**: Comprehensive employment agreement with benefits and obligations

**Key Concepts Demonstrated**:
- Salary and compensation structure
- Benefits package (health, vacation, etc.)
- Performance-based bonuses
- Probation period
- Non-compete clauses
- Termination conditions
- Notice periods
- Severance calculations

**Notable Features**:
```baby-l4
# Overtime compensation
rule <overtimeCompensation>
for emp : Employment, e : Employee, hours : Integer, d : Date
if emp.employee == e && WorkedOvertime e hours d && hours > 40
then exists overtime : Integer . 
     overtime == ((hours - 40) * 15 / 10) &&  # 1.5x rate
     MustPay emp.employer e overtime d

# Post-employment obligations
rule <nonCompeteObligation>
for emp : Employment, e : Employee, c : Company
if not EmploymentActive emp && emp.employee == e &&
   CompetingBusiness c emp.employer
then MayNotCompete e c (Years 2)  # 2-year non-compete
```

### 4. Sales Agreement (`sales_agreement.l4`)

**Purpose**: Commercial sale of goods contract

**Key Concepts Demonstrated**:
- Delivery obligations
- Payment terms (immediate, net 30/60)
- Quality inspection rights
- Title and risk transfer
- Warranties
- Force majeure
- Liquidated damages
- Breach and termination

**Notable Features**:
```baby-l4
# Different payment terms
rule <paymentNet30>
for sa : SalesAgreement, b : Buyer, s : Seller, payDate : Date
if AgreementActive sa && sa.buyer == b && sa.seller == s &&
   sa.paymentTerms == Net30 && HasDelivered s sa.goods &&
   DaysAfter sa.deliveryDate 30 payDate
then MustPay b sa.goods.totalPrice s payDate

# Risk transfer varies by delivery terms
rule <riskTransferFOB>
for sa : SalesAgreement, g : Goods, b : Buyer
if sa.deliveryMethod == FOB && sa.goods == g && sa.buyer == b &&
   exists shipped : Boolean . shipped
then RiskPassed g b
```

## How to Use These Examples

### Running the Examples

To process any example through Baby-L4:

```bash
# Check syntax and type checking
stack run l4 parse l4/nda.l4

# Generate natural language
stack run l4 gf en l4/nda.l4

# Verify assertions with SMT solver
stack run l4 smt l4/nda.l4
```

### Understanding the Structure

Each contract follows this general pattern:

1. **Lexicon**: Natural language mappings
2. **Classes**: Define entities and relationships
3. **Declarations**: Define predicates and functions
4. **Rules**: Encode the contract logic
5. **Facts**: Set up test scenarios
6. **Assertions**: Verify expected outcomes

### Extending the Examples

To adapt these for your own contracts:

1. **Identify Similar Pattern**: Find the example closest to your contract type
2. **Modify Classes**: Adjust entities to match your domain
3. **Update Rules**: Change the logical rules to match your contract terms
4. **Test Thoroughly**: Create facts for various scenarios and verify with assertions

## Key Concepts Across All Examples

### Temporal Logic
All contracts handle time through:
- `CurrentDate`: The present moment
- `DateBefore/DateAfter`: Temporal comparisons
- `DaysAfter/MonthsAfter`: Duration calculations

### Obligations and Permissions
Standard deontic patterns:
- `Must[Action]`: Obligations
- `May[Action]`: Permissions
- `MustNot[Action]`: Prohibitions

### Contract Lifecycle
Common states:
- `AgreementActive`: Contract is in effect
- `InBreach`: Party has violated terms
- `MayTerminate`: Termination rights

### Hierarchical Rules
Exceptions and overrides:
- General rules with specific exceptions
- Force majeure clauses
- Conditional obligations

## Learning Path

1. **Start with NDA**: Simplest structure, clear obligations
2. **Study Rental Agreement**: Adds temporal payments and conditions
3. **Examine Employment Contract**: Complex multi-faceted agreement
4. **Analyze Sales Agreement**: Commercial transactions with delivery/payment coordination

## Common Patterns to Reuse

### Breach Detection
```baby-l4
rule <breachByNonPerformance>
for p : Party, obligation : Obligation
if MustPerform p obligation && not HasPerformed p obligation
then InBreach p agreement
```

### Notice Requirements
```baby-l4
rule <noticeRequired>
for p : Party, action : Action
if IntendsToDo p action
then MustGiveNotice p 30  # days
```

### Conditional Rights
```baby-l4
rule <conditionalRight>
for p : Party, right : Right
if Condition1 && Condition2 && not Exception
then MayExercise p right
```

## Debugging Tips

1. **Type Errors**: Ensure all variables are properly typed in rules
2. **Assertion Failures**: Check that facts properly set up the scenario
3. **Missing Rules**: Verify all contract clauses are encoded
4. **Logical Inconsistencies**: Look for contradicting rules

## Further Resources

- See `../FORMALIZATION_GUIDE.md` for step-by-step formalization process
- See `../L4_REFERENCE.md` for language syntax reference
- See `../CONTRACT_TEMPLATES.md` for reusable patterns

## Contributing

To add new contract examples:
1. Follow the established structure
2. Include comprehensive comments
3. Provide test scenarios with facts
4. Add assertions to verify correctness
5. Update this README with your example