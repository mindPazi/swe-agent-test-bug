from discount import calculate_discount, get_discount_info

class ShoppingCart:
    def __init__(self, customer_is_loyal=False):
        self.items = []
        self.customer_is_loyal = customer_is_loyal
    
    def add_item(self, product, quantity=1):
        self.items.append({
            "product": product,
            "quantity": quantity
        })
    
    def get_total(self):
        total = 0
        for item in self.items:
            product = item["product"]
            quantity = item["quantity"]
            
            discounted_price = calculate_discount(product, self.customer_is_loyal)
            total += discounted_price * quantity
        
        return round(total, 2)
    
    def get_item_details(self):
        details = []
        for item in self.items:
            product = item["product"]
            quantity = item["quantity"]
            
            discount_info = get_discount_info(product)
            discounted_price = calculate_discount(product, self.customer_is_loyal)
            
            details.append({
                "product_name": product.name,
                "quantity": quantity,
                "original_price": discount_info["original_price"],
                "discounted_price": discounted_price,
                "subtotal": discounted_price * quantity
            })
        
        return details
    
    def clear(self):
        self.items = []

