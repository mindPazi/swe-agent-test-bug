CATEGORY_DISCOUNTS = {
    "electronics": 0.10,
    "clothing": 0.15,
    "food": 0.05,
}

LOYALTY_DISCOUNT = 0.05

_discount_cache = {}

def calculate_discount(product, is_loyal_customer=False):
    cache_key = (id(product), is_loyal_customer)
    
    if cache_key in _discount_cache:
        return _discount_cache[cache_key]
    
    category_discount = CATEGORY_DISCOUNTS.get(product.category, 0)
    price_after_category = product.apply_category_discount(category_discount)
    
    if is_loyal_customer:
        final_price = price_after_category * (1 - LOYALTY_DISCOUNT)
    else:
        final_price = price_after_category
    
    result = round(final_price, 2)
    _discount_cache[cache_key] = result
    return result

def get_discount_info(product):
    category_discount = CATEGORY_DISCOUNTS.get(product.category, 0)
    return {
        "category": product.category,
        "discount_rate": category_discount,
        "original_price": product.get_base_price()
    }

def clear_cache():
    global _discount_cache
    _discount_cache = {}
