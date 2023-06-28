class Admin:
    def __init__(self, id=None, name=None, password=None, phone_number=None, last_login=None, priviledge=None, api_key=None):
        self.id = id
        self.name = name
        self.password = password
        self.phone_number = phone_number
        self.last_login = last_login
        self.priviledge = priviledge
        self.api_key = api_key
        
    def tojson(self):
        return {
            "id" : self.id, 
            "name" : self.name,
            "phone_number" : self.phone_number,
            "last_login" : self.last_login,
            "priviledge" : self.priviledge,
            "api_key" : self.api_key
        }
        
    def complete(self):
        if self.name is None:
            return False
        if self.password is None:
            return False
        if self.phone_number is None:
            return False
        if self.priviledge is None:
            return False
        return True