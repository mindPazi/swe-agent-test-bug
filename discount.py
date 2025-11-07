CATEGORY_DISCOUNTS = {
    "electronics": 0.10,
    "clothing": 0.15,
    "food": 0.05,
}

LOYALTY_DISCOUNT = 0.05

def calculate_discount(product, is_loyal_customer=False):
    # Calculate fresh every time - no caching
    base_price = product.price
    
    # Apply category discount
    category_discount = CATEGORY_DISCOUNTS.get(product.category, 0)
    if category_discount > 0:
        base_price *= (1 - category_discount)
    
    # Apply loyalty discount on already-discounted price
    if is_loyal_customer:
        base_price *= (1 - LOYALTY_DISCOUNT)
    
    result = round(base_price, 2)
    return result

def get_discount_info(product):
    category_discount = CATEGORY_DISCOUNTS.get(product.category, 0)
    return {
        "category": product.category,
        "discount_rate": category_discount,
        "original_price": product.price
    }

