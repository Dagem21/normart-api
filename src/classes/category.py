class Category:
    def __init__(self, id=None, name=None, image=None):
        self.id = id
        self.name = name
        self.image = image
        
    def tojson(self):
        return {
            "id" : self.id, 
            "name" : self.name,
            "image" : self.image
        }
        
    def complete(self):
        if self.name is None:
            return False
        if self.image is None:
            return False
        return True