#!/usr/bin/env python3
"""
Simple Example: Service Agreement
Shows how to create a basic contract in Python L4
"""

from l4_core import *
from datetime import datetime


# Define parties
class Client(Party):
    pass


class ServiceProvider(Party):
    pass


# Create a simple service agreement
def create_service_agreement():
    # Initialize contract
    contract = L4Contract("Service Agreement")
    
    # Define parties
    client = Client("ABC Corp")
    provider = ServiceProvider("Tech Solutions Inc")
    
    # Add a simple predicate
    service_completed = lambda: contract.context.get('service_completed', False)
    contract.add_predicate('ServiceCompleted', service_completed)
    
    # Add payment obligation rule
    def payment_due_condition(**ctx):
        return service_completed()
    
    def payment_due_consequence(**ctx):
        return must(client, "pay", {"amount": 5000, "to": provider})
    
    contract.add_rule(Rule(
        name="paymentDueOnCompletion",
        condition=payment_due_condition,
        consequence=payment_due_consequence
    ))
    
    # Add fact that service is completed
    contract.add_fact(Fact(
        name="serviceIsComplete",
        predicate=lambda: True,
        args={"service_completed": True}
    ))
    
    # Add assertion to verify payment is due
    contract.add_assertion(Assertion(
        name="clientMustPay",
        predicate=lambda service_completed: service_completed,
        args={"service_completed": True}
    ))
    
    return contract, client, provider


def main():
    print("=== Simple Service Agreement ===\n")
    
    # Create contract
    contract, client, provider = create_service_agreement()
    
    # Show natural language
    print(contract.to_natural_language())
    
    # Evaluate rules
    print("\n=== Contract Evaluation ===")
    results = contract.evaluate_rules()
    
    for rule_name, result in results.items():
        if isinstance(result, dict) and result.get('type') == Obligation.MUST:
            party = result['party']
            action = result['action']
            obj = result['object']
            print(f"\n{rule_name}:")
            print(f"  {party} MUST {action} ${obj['amount']} to {obj['to']}")
    
    print("\n=== How to extend this example ===")
    print("1. Add more parties: class Subcontractor(Party)")
    print("2. Add conditions: if service_quality == 'excellent'")
    print("3. Add time constraints: if current_date > due_date")
    print("4. Add exceptions: if not force_majeure_event")
    print("5. Chain obligations: service leads to payment leads to receipt")


if __name__ == "__main__":
    main()