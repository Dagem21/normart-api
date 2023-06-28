from datetime import datetime

class Order:
    def __init__(self, id=None, user_id=None, items=None, packages=None, date=None, status=None, delivery_location=None):
        self.id = id
        self.user_id = user_id
        self.items = items
        self.packages = packages
        self.date = datetime.strftime(date, '%d-%m-%Y') if date is not None else None
        self.status = status
        self.delivery_location = delivery_location
        
    def tojson(self):
        return {
            "id" : self.id, 
            "user_id" : self.user_id,
            "items" : self.items,
            "packages" : self.packages,
            "date" : self.date,
            "status" : self.status,
            "delivery_location" : self.delivery_location
        }
    
    def complete(self):
        if self.user_id is None:
            return False
        if self.items is None and self.packages is None:
            return False
        if self.date is None:
            return False
        if self.status is None:
            return False
        if self.delivery_location is None:
            return False
        return True