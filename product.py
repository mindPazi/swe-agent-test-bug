class Product:
    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category
        self._cached_discount = None
    
    def get_base_price(self):
        return self.price
    
    def apply_category_discount(self, discount_rate):
        if self._cached_discount is None:
            self._cached_discount = self.price * discount_rate
        return self.price - self._cached_discount
    
    def __repr__(self):
        return f"Product({self.name}, ${self.price}, {self.category})"

