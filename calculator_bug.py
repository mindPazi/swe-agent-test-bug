# calculator.py
def calculate_discount(price, customer_type, quantity):
    """
    Calculate discount based on customer type and quantity.
    Bug: The function returns wrong discount for VIP customers buying more than 10 items.
    Expected: VIP customers get 20% + 5% extra for bulk (total 25%)
    Actual: Returns 15% instead of 25%
    """
    discount = 0
    if customer_type == "VIP":
        discount = 0.15  # Bug: should be 0.20
    elif customer_type == "REGULAR":
        discount = 0.05
    
    if quantity > 10:
        discount += 0.05
    
    return price * (1 - discount)

# Test case:
if __name__ == "__main__":
    result = calculate_discount(100, "VIP", 15)
    print(f"Price for VIP customer buying 15 items: ${result}")
    print(f"Expected: $75.0 (25% discount)")
    print(f"Actual: ${result}")
