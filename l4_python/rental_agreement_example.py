#!/usr/bin/env python3
"""
Rental Agreement Example in Python L4
Demonstrates a residential lease agreement
"""

from l4_core import *
from datetime import datetime
from dataclasses import dataclass


# Define custom classes for rental agreement
class Landlord(Party):
    pass


class Tenant(Party):
    pass


@dataclass
class Property:
    address: str
    monthly_rent: int
    security_deposit: int


@dataclass
class Lease:
    property: Property
    landlord: Landlord
    tenant: Tenant
    start_date: Date
    end_date: Date
    
    @property
    def monthly_rent(self):
        return self.property.monthly_rent


@dataclass
class Payment:
    amount: int
    due_date: Date
    paid: bool = False


def create_rental_contract():
    """Create a rental agreement contract"""
    contract = L4Contract("Residential Lease Agreement")
    
    # Add lexicon
    contract.add_lexicon("Landlord", "landlord")
    contract.add_lexicon("Tenant", "tenant")
    contract.add_lexicon("Rent", "rent")
    contract.add_lexicon("Occupy", "occupy")
    
    # Define predicates
    lease_active = lambda lease: contract.context.get('lease_active', True)
    has_paid_rent = lambda tenant, payment: payment.paid
    late_payments = lambda tenant: contract.context.get('late_payment_count', 0)
    property_condition = lambda prop: contract.context.get('property_condition', 'good')
    caused_damage = lambda tenant, prop: contract.context.get('tenant_damage', False)
    
    contract.add_predicate('LeaseActive', lease_active)
    contract.add_predicate('HasPaid', has_paid_rent)
    contract.add_predicate('LatePayments', late_payments)
    contract.add_predicate('PropertyCondition', property_condition)
    contract.add_predicate('CausedDamage', caused_damage)
    
    # Occupancy right rule
    def occupancy_right_condition(**ctx):
        lease = ctx.get('lease')
        if not lease:
            return False
        return (lease_active(lease) and 
                late_payments(lease.tenant) == 0)
    
    def occupancy_right_consequence(**ctx):
        lease = ctx['lease']
        return may(lease.tenant, "occupy", lease.property)
    
    contract.add_rule(Rule(
        name="occupancyRight",
        condition=occupancy_right_condition,
        consequence=occupancy_right_consequence
    ))
    
    # Rent obligation rule
    def rent_obligation_condition(**ctx):
        lease = ctx.get('lease')
        return lease and lease_active(lease)
    
    def rent_obligation_consequence(**ctx):
        lease = ctx['lease']
        return must(lease.tenant, "pay rent", {
            "amount": lease.monthly_rent,
            "to": lease.landlord,
            "due": "1st of each month"
        })
    
    contract.add_rule(Rule(
        name="rentObligation",
        condition=rent_obligation_condition,
        consequence=rent_obligation_consequence
    ))
    
    # Eviction rule
    def eviction_for_nonpayment_condition(**ctx):
        lease = ctx.get('lease')
        if not lease:
            return False
        return late_payments(lease.tenant) >= 3
    
    def eviction_for_nonpayment_consequence(**ctx):
        lease = ctx['lease']
        return may(lease.landlord, "evict", lease.tenant)
    
    contract.add_rule(Rule(
        name="evictionForNonPayment",
        condition=eviction_for_nonpayment_condition,
        consequence=eviction_for_nonpayment_consequence
    ))
    
    # Security deposit refund rule
    def deposit_refund_full_condition(**ctx):
        lease = ctx.get('lease')
        if not lease:
            return False
        return (not lease_active(lease) and
                property_condition(lease.property) == 'good' and
                not caused_damage(lease.tenant, lease.property))
    
    def deposit_refund_full_consequence(**ctx):
        lease = ctx['lease']
        return must(lease.landlord, "refund deposit", {
            "amount": lease.property.security_deposit,
            "to": lease.tenant
        })
    
    contract.add_rule(Rule(
        name="depositRefundFull",
        condition=deposit_refund_full_condition,
        consequence=deposit_refund_full_consequence
    ))
    
    # Create scenario
    jane_smith = Landlord("Jane Smith")
    john_doe = Tenant("John Doe")
    
    apt_123 = Property(
        address="123 Main St, Apt 4B",
        monthly_rent=1500,
        security_deposit=3000
    )
    
    lease_2024 = Lease(
        property=apt_123,
        landlord=jane_smith,
        tenant=john_doe,
        start_date=Date(datetime(2024, 1, 1)),
        end_date=Date(datetime(2024, 12, 31))
    )
    
    # Add facts
    contract.add_fact(Fact(
        name="leaseActive",
        predicate=lambda: True,
        args={"lease": lease_2024, "lease_active": True}
    ))
    
    contract.add_fact(Fact(
        name="noLatePayments",
        predicate=lambda: True,
        args={"late_payment_count": 0}
    ))
    
    contract.add_fact(Fact(
        name="propertyInGoodCondition",
        predicate=lambda: True,
        args={"property_condition": "good", "tenant_damage": False}
    ))
    
    # Add assertions
    contract.add_assertion(Assertion(
        name="tenantMayOccupy",
        predicate=lambda lease, late_payments: lease_active(lease) and late_payments == 0,
        args={"lease": lease_2024, "late_payments": 0}
    ))
    
    contract.add_assertion(Assertion(
        name="tenantMustPayRent",
        predicate=lambda lease: lease_active(lease),
        args={"lease": lease_2024}
    ))
    
    contract.add_assertion(Assertion(
        name="landlordCannotEvict",
        predicate=lambda late_payments: late_payments < 3,
        args={"late_payments": 0}
    ))
    
    return contract


def simulate_scenarios(contract):
    """Simulate different rental scenarios"""
    print("\n=== Scenario Simulations ===")
    
    # Scenario 1: Late payments
    print("\n--- Scenario 1: Tenant has 3 late payments ---")
    original_late_payments = contract.context['late_payment_count']
    contract.context['late_payment_count'] = 3
    
    results = contract.evaluate_rules()
    if 'evictionForNonPayment' in results:
        eviction = results['evictionForNonPayment']
        print(f"Result: {eviction['party']} MAY {eviction['action']} {eviction['object']}")
    
    # Reset
    contract.context['late_payment_count'] = original_late_payments
    
    # Scenario 2: Lease ended with damage
    print("\n--- Scenario 2: Lease ended with property damage ---")
    contract.context['lease_active'] = False
    contract.context['tenant_damage'] = True
    
    results = contract.evaluate_rules()
    if 'depositRefundFull' not in results:
        print("Result: Full deposit refund NOT required (due to damage)")
    
    # Calculate partial refund
    lease = contract.context['lease']
    damage_cost = 500  # Example damage cost
    refund_amount = lease.property.security_deposit - damage_cost
    print(f"Partial refund: ${refund_amount} (${lease.property.security_deposit} - ${damage_cost} damage)")


def main():
    print("=== Baby-L4 Python: Rental Agreement Example ===\n")
    
    # Create and evaluate contract
    contract = create_rental_contract()
    
    # Show natural language version
    print(contract.to_natural_language())
    
    # Evaluate rules
    print("\nRule Evaluation Results:")
    results = contract.evaluate_rules()
    for rule_name, result in results.items():
        print(f"\n{rule_name}:")
        if isinstance(result, dict):
            for k, v in result.items():
                print(f"  {k}: {v}")
    
    # Show lease details
    lease = contract.context['lease']
    print(f"\n=== Lease Details ===")
    print(f"Property: {lease.property.address}")
    print(f"Monthly Rent: ${lease.monthly_rent:,}")
    print(f"Security Deposit: ${lease.property.security_deposit:,}")
    print(f"Term: {lease.start_date} to {lease.end_date}")
    print(f"Landlord: {lease.landlord}")
    print(f"Tenant: {lease.tenant}")
    
    # Show current obligations
    print("\n=== Current Obligations & Rights ===")
    if 'occupancyRight' in results:
        right = results['occupancyRight']
        print(f"- {right['party']} MAY {right['action']} {right['object']}")
    
    if 'rentObligation' in results:
        obligation = results['rentObligation']
        obj = obligation['object']
        print(f"- {obligation['party']} MUST {obligation['action']}: ${obj['amount']:,} to {obj['to']} {obj['due']}")
    
    # Run scenario simulations
    simulate_scenarios(contract)


if __name__ == "__main__":
    main()