from classes import *
from database import *

def get_categories_serv():
    categories, err = getCategories()
    return categories, err
     
def add_category_serv(category:Category):
    category, err = addCategory(category=category)
    return category, err

def delete_category_serv(category_id):
    res, err = deleteCategory(category_id=category_id)
    return res, err