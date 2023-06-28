from datetime import datetime

class Package:
    def __init__(self, id=None, name=None, description=None, image=None, start_date=None, expire_date=None, items=None, price=None):
        self.id = id
        self.name = name
        self.description = description
        self.image = image
        self.start_date = start_date
        self.expire_date = expire_date
        self.items = items
        self.price = price
        
    def tojson(self):
        return {
            "id" : self.id, 
            "name" : self.name,
            "description" : self.description,
            "image" : self.image,
            "start_date" : self.start_date.strftime('%Y-%m-%d') if self.start_date != None else None,
            "expire_date" : self.expire_date.strftime('%Y-%m-%d') if self.expire_date != None else None,
            "items" : self.items,
            "price" : self.price
        }
    def complete(self):
        if self.name is None:
            return False
        if self.description is None:
            return False
        if self.image is None:
            return False
        if self.start_date is None:
            return False
        if self.expire_date is None:
            return False
        if self.items is None:
            return False
        if self.price is None:
            return False
        return True
