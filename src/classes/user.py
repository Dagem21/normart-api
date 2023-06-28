class User:
    
    def __init__(self, id=None, username=None, name=None, password=None, avatar=None, api_key=None):
        self.id = id
        self.username = username
        self.name = name
        self.password = password
        self.avatar = avatar
        self.api_key = api_key
        self.phone_numbers = []
        self.addresses = []
        self.coupons = []
        
    def tojson(self):
        return {
            "id" : self.id, 
            "username" : self.username,
            "name" : self.name,
            "avatar" : self.avatar,
            "api_key" : self.api_key
        }
    
    def tojsonall(self):
        return {
            "id" : self.id, 
            "username" : self.username,
            "name" : self.name,
            "avatar" : self.avatar,
            "phone_numbers" : self.phone_numbers,
            "addresses" : self.addresses,
            "coupons" : self.coupons
        }
        
    def complete(self):
        if self.username is None:
            return False
        if self.name is None:
            return False
        if self.password is None:
            return False
        return True