class Coupon:
    def __init__(self, id=None, tag=None, coupon_value=None, start_date=None, expire_date=None, used=None, used_date=None, reusable=None, user_id=None, owner=None):
        self.id = id
        self.tag = tag
        self.coupon_value = coupon_value
        self.start_date = start_date
        self.expire_date = expire_date
        self.used = used
        self.used_date = used_date
        self.reusable = reusable
        self.user_id = user_id
        self.owner = owner
        
    def tojson(self):
        return {
            "id" : self.id, 
            "tag" : self.tag,
            "coupon_value" : self.coupon_value,
            "start_date" : self.start_date.strftime('%Y-%m-%d') if self.start_date != None else None,
            "expire_date" : self.expire_date.strftime('%Y-%m-%d') if self.expire_date != None else None,
            "used" : self.used,
            "used_date" : self.used_date,
            "reusable" : self.reusable,
            "user_id" : self.user_id,
            "owner" : self.owner
        }
        
    def complete(self):
        if self.coupon_value is None:
            return False
        if self.start_date is None:
            return False
        if self.expire_date is None:
            return False
        if self.reusable is None:
            return False
        return True