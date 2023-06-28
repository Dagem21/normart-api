class Item:
    def __init__(self, id=None, name=None, category1=None, category2=None, category3=None, unit=None, price=None, image=None, discount=None, taxable=None):
        self.id = id
        self.name = name
        self.category1 = category1
        self.category2 = category2
        self.category3 = category3
        self.unit = unit
        self.price = price
        self.image = image
        self.discount = discount
        self.taxable = taxable
    
    def tojson(self):
        return {
            "id" : self.id, 
            "name" : self.name,
            "category1" : self.category1,
            "category2" : self.category2,
            "category3" : self.category3,
            "unit" : self.unit,
            "price" : self.price,
            "image" : self.image,
            "discount" : self.discount,
            "taxable" : self.taxable
        }
    
    def complete(self):
        if self.name is None:
            return False
        if self.category1 is None:
            return False
        if self.unit is None:
            return False
        if self.price is None:
            return False
        if self.image is None:
            return False
        return True