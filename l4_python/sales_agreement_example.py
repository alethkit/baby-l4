#!/usr/bin/env python3
"""
Sales Agreement Example in Python L4
Demonstrates a commercial sale of goods contract
"""

from l4_core import *
from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto


# Define custom classes for sales agreement
class Buyer(Party):
    pass


class Seller(Party):
    pass


@dataclass
class Product:
    name: str
    sku: str
    unit_price: int


@dataclass
class Goods:
    product: Product
    quantity: int
    
    @property
    def total_price(self):
        return self.product.unit_price * self.quantity


class PaymentTerms(Enum):
    IMMEDIATE = auto()
    NET30 = auto()
    NET60 = auto()
    INSTALLMENTS = auto()


class DeliveryMethod(Enum):
    FOB = auto()  # Free on Board
    CIF = auto()  # Cost, Insurance, Freight
    EX_WORKS = auto()


@dataclass
class SalesAgreement:
    buyer: Buyer
    seller: Seller
    goods: Goods
    payment_terms: PaymentTerms
    delivery_method: DeliveryMethod
    delivery_date: Date
    agreement_date: Date


def create_sales_contract():
    """Create a sales agreement contract"""
    contract = L4Contract("Commercial Sales Agreement")
    
    # Add lexicon mappings
    contract.add_lexicon("Buyer", "buyer")
    contract.add_lexicon("Seller", "seller")
    contract.add_lexicon("Deliver", "deliver")
    contract.add_lexicon("Pay", "pay")
    
    # Define predicates
    agreement_active = lambda agreement: True  # Simplified
    has_delivered = lambda seller, goods: contract.context.get('goods_delivered', False)
    has_paid = lambda buyer, amount: contract.context.get('payment_made', False)
    
    contract.add_predicate('AgreementActive', agreement_active)
    contract.add_predicate('HasDelivered', has_delivered)
    contract.add_predicate('HasPaid', has_paid)
    
    # Delivery obligation rule
    def delivery_obligation_condition(**ctx):
        return ('sales_agreement' in ctx and 
                agreement_active(ctx['sales_agreement']))
    
    def delivery_obligation_consequence(**ctx):
        sa = ctx['sales_agreement']
        return must(sa.seller, "deliver", sa.goods)
    
    contract.add_rule(Rule(
        name="deliveryObligation",
        condition=delivery_obligation_condition,
        consequence=delivery_obligation_consequence
    ))
    
    # Payment rule for Net30
    def payment_net30_condition(**ctx):
        sa = ctx.get('sales_agreement')
        if not sa:
            return False
        return (agreement_active(sa) and 
                sa.payment_terms == PaymentTerms.NET30 and
                has_delivered(sa.seller, sa.goods))
    
    def payment_net30_consequence(**ctx):
        sa = ctx['sales_agreement']
        pay_date = sa.delivery_date.days_after(30)
        return must(sa.buyer, "pay", {
            "amount": sa.goods.total_price,
            "to": sa.seller,
            "by": pay_date
        })
    
    contract.add_rule(Rule(
        name="paymentNet30",
        condition=payment_net30_condition,
        consequence=payment_net30_consequence
    ))
    
    # Title transfer rule (FOB)
    def title_transfer_fob_condition(**ctx):
        sa = ctx.get('sales_agreement')
        if not sa:
            return False
        return (sa.delivery_method == DeliveryMethod.FOB and
                has_delivered(sa.seller, sa.goods))
    
    def title_transfer_fob_consequence(**ctx):
        sa = ctx['sales_agreement']
        return {"title_passed": True, "to": sa.buyer, "goods": sa.goods}
    
    contract.add_rule(Rule(
        name="titleTransferFOB",
        condition=title_transfer_fob_condition,
        consequence=title_transfer_fob_consequence
    ))
    
    # Create scenario
    widget_corp = Seller("WidgetCorp")
    acme = Buyer("Acme Manufacturing")
    
    industrial_widget = Product(
        name="Industrial Widget XL",
        sku="IW-XL-2024",
        unit_price=1000
    )
    
    order_goods = Goods(
        product=industrial_widget,
        quantity=100
    )
    
    sales_agreement = SalesAgreement(
        buyer=acme,
        seller=widget_corp,
        goods=order_goods,
        payment_terms=PaymentTerms.NET30,
        delivery_method=DeliveryMethod.FOB,
        delivery_date=Date(datetime(2024, 2, 1)),
        agreement_date=Date(datetime(2024, 1, 1))
    )
    
    # Add facts
    contract.add_fact(Fact(
        name="contractActive",
        predicate=lambda: True,
        args={"sales_agreement": sales_agreement}
    ))
    
    contract.add_fact(Fact(
        name="goodsDelivered",
        predicate=lambda: True,
        args={"goods_delivered": True}
    ))
    
    # Add assertions to verify
    contract.add_assertion(Assertion(
        name="sellerMustDeliver",
        predicate=lambda sales_agreement: agreement_active(sales_agreement),
        args={"sales_agreement": sales_agreement}
    ))
    
    contract.add_assertion(Assertion(
        name="buyerMustPay",
        predicate=lambda sales_agreement, goods_delivered: (
            sales_agreement.payment_terms == PaymentTerms.NET30 and goods_delivered
        ),
        args={"sales_agreement": sales_agreement, "goods_delivered": True}
    ))
    
    return contract


def main():
    print("=== Baby-L4 Python: Sales Agreement Example ===\n")
    
    # Create and evaluate contract
    contract = create_sales_contract()
    
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
    
    # Check specific obligations
    sa = contract.context['sales_agreement']
    print(f"\n=== Contract Analysis ===")
    print(f"Product: {sa.goods.product.name}")
    print(f"Quantity: {sa.goods.quantity}")
    print(f"Total Price: ${sa.goods.total_price:,}")
    print(f"Payment Terms: {sa.payment_terms.name}")
    print(f"Delivery Method: {sa.delivery_method.name}")
    
    # Show obligations
    print("\n=== Obligations ===")
    if 'deliveryObligation' in results:
        obligation = results['deliveryObligation']
        print(f"- {obligation['party']} MUST {obligation['action']} {obligation['object']}")
    
    if 'paymentNet30' in results:
        payment = results['paymentNet30']
        print(f"- {payment['party']} MUST {payment['action']} ${payment['object']['amount']:,} to {payment['object']['to']} by {payment['object']['by']}")
    
    if 'titleTransferFOB' in results:
        title = results['titleTransferFOB']
        print(f"- Title passed to {title['to']} for {title['goods']}")


if __name__ == "__main__":
    main()