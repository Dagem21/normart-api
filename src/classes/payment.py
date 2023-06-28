class Payment:
    def __init__(self, id=None, order_id=None, price=None, payed=None, date=None, payment_date=None):
        self.id = id
        self.order_id = order_id
        self.price = price
        self.payed = payed
        self.date = date
        self.payment_date = payment_date
    
    def tojson(self):
        return {
            "id" : self.id, 
            "order_id" : self.order_id,
            "price" : self.price,
            "payed" : self.payed,
            "date" : self.date,
            "payment_date" : self.payment_date
        }
        
    def complete(self):
        if self.order_id is None:
            return False
        if self.price is None:
            return False
        if self.payed is None:
            return False
        if self.date is None:
            return False
        return True
