class Location:
    def __init__(self, id=None, location=None, name=None, working=None, phone_number=None):
        self.id = id
        self.location = location
        self.name = name
        self.working = working
        self.phone_number = phone_number
        
    def tojson(self):
        return {
            "id" : self.id, 
            "location" : self.location,
            "name" : self.name,
            "working" : self.working,
            "phone_number" : self.phone_number
        }

    def complete(self):
        if self.location is None:
            return False
        if self.name is None:
            return False
        if self.working is None:
            return False
        if self.phone_number is None:
            return False
        return True