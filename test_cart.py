import pytest
from product import Product
from cart import ShoppingCart

def test_single_product_no_loyalty():
    laptop = Product("Laptop", 1000, "electronics")
    cart = ShoppingCart(customer_is_loyal=False)
    cart.add_item(laptop)
    
    assert cart.get_total() == 900.0

def test_single_product_with_loyalty():
    shirt = Product("Shirt", 50, "clothing")
    cart = ShoppingCart(customer_is_loyal=True)
    cart.add_item(shirt)
    
    assert cart.get_total() == 40.38

def test_multiple_same_category():
    phone = Product("Phone", 800, "electronics")
    tablet = Product("Tablet", 600, "electronics")
    
    cart = ShoppingCart(customer_is_loyal=False)
    cart.add_item(phone)
    cart.add_item(tablet)
    
    expected = 1260.0
    actual = cart.get_total()
    
    print(f"\nExpected: {expected}")
    print(f"Actual: {actual}")
    
    assert actual == expected, f"Expected {expected} but got {actual}"

def test_reused_product_different_carts():
    laptop = Product("Laptop", 1000, "electronics")
    
    cart1 = ShoppingCart(customer_is_loyal=False)
    cart1.add_item(laptop)
    total1 = cart1.get_total()
    print(f"\nCart1 (no loyalty): {total1}")
    
    cart2 = ShoppingCart(customer_is_loyal=True)
    cart2.add_item(laptop)
    total2 = cart2.get_total()
    print(f"Cart2 (with loyalty): {total2}")
    
    assert total1 == 900.0, f"Expected 900.0 but got {total1}"
    assert total2 == 855.0, f"Expected 855.0 but got {total2}"

def test_multiple_calls_same_product():
    phone = Product("Phone", 500, "electronics")
    
    cart1 = ShoppingCart(customer_is_loyal=False)
    cart1.add_item(phone)
    
    cart2 = ShoppingCart(customer_is_loyal=False)
    cart2.add_item(phone)
    cart2.add_item(phone)
    
    total1 = cart1.get_total()
    total2 = cart2.get_total()
    
    print(f"\nCart1 (1 phone): {total1}")
    print(f"Cart2 (2 phones): {total2}")
    
    assert total1 == 450.0, f"Expected 450.0 but got {total1}"
    assert total2 == 900.0, f"Expected 900.0 (450*2) but got {total2}"

def test_details_affects_calculation():
    tv = Product("TV", 1200, "electronics")
    
    cart = ShoppingCart(customer_is_loyal=False)
    cart.add_item(tv)
    
    details = cart.get_item_details()
    total = cart.get_total()
    
    print(f"\nDetails: {details}")
    print(f"Total: {total}")
    
    expected = 1080.0
    assert total == expected, f"Expected {expected} but got {total}"
