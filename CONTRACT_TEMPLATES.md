# Baby-L4 Contract Templates

This document provides reusable templates and patterns for common contract types in Baby-L4.

## Basic Contract Structure Template

```baby-l4
# Contract Type Name
# l4version 0.3.6

lexicon
# Natural language mappings

# ============ PARTIES ============
class Party
class [PartyType1] extends Party
class [PartyType2] extends Party

# ============ CORE ENTITIES ============
class [MainObject]
class [Agreement] {
    party1: [PartyType1]
    party2: [PartyType2]
    subject: [MainObject]
    effectiveDate: Date
    terminationDate: Date
}

# ============ PREDICATES ============
# Status predicates
decl AgreementActive : [Agreement] -> Boolean
decl InBreach : Party -> [Agreement] -> Boolean

# Obligation predicates  
decl Must[Action] : [PartyType] -> [Object] -> Boolean
decl May[Action] : [PartyType] -> [Object] -> Boolean

# ============ RULES ============
# Core obligations
rule <primaryObligation>
for p1 : [PartyType1], agr : [Agreement]
if AgreementActive agr && agr.party1 == p1
then Must[Action] p1 agr.subject

# ============ FACTS & ASSERTIONS ============
# Test scenario
decl testAgreement : [Agreement]
fact <testActive> AgreementActive testAgreement
assert <obligationHolds> Must[Action] testParty testObject
```

## Common Contract Modules

### 1. Party Management Module

```baby-l4
# Reusable party definitions
class Party
class NaturalPerson extends Party {
    name: String
    idNumber: String
}
class LegalEntity extends Party {
    registrationNumber: String
    representative: NaturalPerson
}
class Government extends LegalEntity
class Company extends LegalEntity
class Individual extends NaturalPerson

# Party relationships
decl AuthorizedRepresentative : NaturalPerson -> LegalEntity -> Boolean
decl ActsOnBehalfOf : Party -> Party -> Boolean
```

### 2. Time Management Module

```baby-l4
# Time-related types and predicates
class Date
class Duration
class Period {
    start: Date
    end: Date
}

decl CurrentDate : Date
decl DateBefore : Date -> Date -> Boolean
decl DateAfter : Date -> Date -> Boolean
decl DaysAfter : Date -> Integer -> Date -> Boolean
decl MonthsAfter : Date -> Integer -> Date -> Boolean
decl YearsAfter : Date -> Integer -> Date -> Boolean
decl WithinPeriod : Date -> Period -> Boolean

# Duration constructors
decl Days : Integer -> Duration
decl Months : Integer -> Duration
decl Years : Integer -> Duration
```

### 3. Payment Module

```baby-l4
# Payment-related definitions
class Money {
    amount: Integer
    currency: Currency
}
class Currency
decl USD : Currency
decl EUR : Currency
decl GBP : Currency

class Payment {
    payer: Party
    payee: Party
    amount: Money
    dueDate: Date
    paid: Boolean
}

class PaymentTerms
decl Immediate : PaymentTerms
decl Net : Integer -> PaymentTerms  # Net(30) for Net30
decl Installments : Integer -> PaymentTerms

# Payment predicates
decl MustPay : Party -> Money -> Party -> Date -> Boolean
decl HasPaid : Party -> Payment -> Boolean
decl PaymentOverdue : Payment -> Boolean

# Payment rules
rule <paymentOverdue>
for p : Payment
if CurrentDate > p.dueDate && not p.paid
then PaymentOverdue p
```

### 4. Breach and Remedies Module

```baby-l4
# Breach types
class BreachType
decl MaterialBreach : BreachType
decl MinorBreach : BreachType
decl AnticipatedBreach : BreachType

# Remedy types
class Remedy
decl Damages : Money -> Remedy
decl SpecificPerformance : Remedy
decl Termination : Remedy
decl Cure : Duration -> Remedy

# Breach predicates
decl InBreach : Party -> Agreement -> BreachType -> Boolean
decl CurePeriod : Party -> Duration -> Boolean
decl RemedyAvailable : Party -> Remedy -> Boolean

# Breach rules
rule <materialBreachRemedies>
for innocent : Party, breaching : Party, agr : Agreement
if InBreach breaching agr MaterialBreach
then RemedyAvailable innocent Termination &&
     RemedyAvailable innocent (Damages (exists m : Money . m))
```

### 5. Termination Module

```baby-l4
# Termination reasons
class TerminationReason
decl ForCause : TerminationReason
decl ForConvenience : TerminationReason
decl ByMutualAgreement : TerminationReason
decl Expiration : TerminationReason

# Termination predicates
decl MayTerminate : Party -> Agreement -> TerminationReason -> Boolean
decl TerminationNotice : Party -> Integer -> Boolean  # days notice
decl EffectiveTerminationDate : Agreement -> Date -> Boolean

# Termination rules
rule <terminationNotice>
for p : Party, agr : Agreement
if MayTerminate p agr ForConvenience
then TerminationNotice p 30  # 30 days notice
```

## Specific Contract Templates

### Service Agreement Template

```baby-l4
# SERVICE AGREEMENT TEMPLATE
# l4version 0.3.6

lexicon
ServiceProvider -> "service_provider_N"
Client -> "client_N"
Services -> "services_N"
Deliverable -> "deliverable_N"

# Parties
class Party
class ServiceProvider extends Party
class Client extends Party

# Service-specific
class Services {
    description: String
    scope: String
}

class Deliverable {
    description: String
    dueDate: Date
    accepted: Boolean
}

class ServiceAgreement {
    provider: ServiceProvider
    client: Client
    services: Services
    deliverables: [Deliverable]
    monthlyFee: Integer
    startDate: Date
    term: Duration
}

# Service obligations
decl MustProvideServices : ServiceProvider -> Services -> Boolean
decl MustPayFees : Client -> Integer -> Date -> Boolean
decl MustDeliverByDate : ServiceProvider -> Deliverable -> Date -> Boolean
decl AcceptanceRequired : Deliverable -> Boolean

# Quality standards
decl MeetsQualityStandards : Deliverable -> Boolean
decl MayRejectDeliverable : Client -> Deliverable -> Boolean

rule <serviceObligation>
for sa : ServiceAgreement, sp : ServiceProvider
if AgreementActive sa && sa.provider == sp
then MustProvideServices sp sa.services

rule <paymentObligation>
for sa : ServiceAgreement, c : Client, d : Date
if AgreementActive sa && sa.client == c && MonthlyDue d
then MustPayFees c sa.monthlyFee d

rule <deliverableAcceptance>
for d : Deliverable, c : Client
if MeetsQualityStandards d
then not MayRejectDeliverable c d
```

### License Agreement Template

```baby-l4
# LICENSE AGREEMENT TEMPLATE
# l4version 0.3.6

lexicon
Licensor -> "licensor_N"
Licensee -> "licensee_N"
License -> "license_V2"

# Parties
class Licensor extends Party
class Licensee extends Party

# License types
class LicenseType
decl Exclusive : LicenseType
decl NonExclusive : LicenseType
decl Sole : LicenseType

# License scope
class LicenseScope {
    territory: [Country]
    field: String
    duration: Duration
}

class IntellectualProperty {
    description: String
    registrations: [String]
}

class LicenseAgreement {
    licensor: Licensor
    licensee: Licensee
    ip: IntellectualProperty
    licenseType: LicenseType
    scope: LicenseScope
    royaltyRate: Float
}

# License grants and restrictions
decl MayUse : Licensee -> IntellectualProperty -> LicenseScope -> Boolean
decl MayNotSublicense : Licensee -> Boolean
decl MustPayRoyalties : Licensee -> Float -> Integer -> Boolean  # rate, sales
decl MustMaintainQuality : Licensee -> Boolean

rule <licenseGrant>
for la : LicenseAgreement, licensee : Licensee
if AgreementActive la && la.licensee == licensee
then MayUse licensee la.ip la.scope

rule <exclusivity>
for la : LicenseAgreement, otherParty : Licensee
if la.licenseType == Exclusive && otherParty /= la.licensee
then not MayUse otherParty la.ip la.scope
```

## Contract Formalization Checklist

When formalizing a contract, ensure you have:

### 1. Structure
- [ ] Identified all parties and their types
- [ ] Defined the main agreement class
- [ ] Created classes for key objects/concepts
- [ ] Added lexicon entries for natural language

### 2. Obligations & Rights
- [ ] Listed all "must" obligations as Must[Action] predicates
- [ ] Listed all "may" rights as May[Action] predicates  
- [ ] Identified prohibitions as MustNot[Action]
- [ ] Mapped each contract clause to a rule

### 3. Temporal Aspects
- [ ] Defined effective dates and term
- [ ] Created rules for time-based obligations
- [ ] Handled expiration and renewal
- [ ] Modeled notice periods

### 4. Conditions & Exceptions
- [ ] Identified all conditions precedent
- [ ] Modeled force majeure and exceptions
- [ ] Handled defeasibility ("despite", "notwithstanding")
- [ ] Created hierarchy of rules

### 5. Breach & Remedies
- [ ] Defined what constitutes breach
- [ ] Specified available remedies
- [ ] Modeled cure periods
- [ ] Created termination conditions

### 6. Testing
- [ ] Created example scenario with facts
- [ ] Written assertions for key obligations
- [ ] Tested edge cases
- [ ] Verified logical consistency

## Reusable Patterns

### Mutual Obligations
```baby-l4
rule <mutualNDA>
for p1 : Party, p2 : Party, info : ConfidentialInfo
if Discloses p1 info p2
then MustProtect p2 info &&
     MustNotDisclose p2 info (forall p3 : Party . p3 /= p1)
```

### Condition Precedent
```baby-l4
decl ConditionSatisfied : Condition -> Boolean
decl ObligationActive : Obligation -> Boolean

rule <conditionalObligation>
for c : Condition, o : Obligation
if DependsOn o c && ConditionSatisfied c
then ObligationActive o
```

### Graduated Remedies
```baby-l4
rule <firstBreach>
for p : Party
if BreachCount p 1
then Warning p

rule <secondBreach>
for p : Party
if BreachCount p 2
then Penalty p 1000

rule <thirdBreach>
for p : Party
if BreachCount p 3
then MayTerminate (exists other : Party . other) Agreement
```

## Best Practices

1. **Start Simple**: Begin with core obligations before adding complexity
2. **Test Incrementally**: Add facts and assertions as you build
3. **Document Assumptions**: Comment any implicit assumptions
4. **Reuse Common Patterns**: Use the modules above as building blocks
5. **Maintain Traceability**: Reference source contract sections in comments