from classes import *
from database import *

def get_item_serv(item_id = None, item_name = None):
    item, err = getItem(item_id=item_id, item_name=item_name)
    return item, err
    
def get_items_serv(cat1=None, cat2=None, cat3=None, discount=None):
    items, err = getItems(cat1=cat1, cat2=cat2, cat3=cat3, discount=discount)
    return items, err

def get_items_search_serv(name):
    items, err = getItemsSearch(name)
    return items, err
    
def get_items_id_list_serv(idList=None):
    items, err = getItemsInList(idList=idList)
    return items, err
    
def add_item_serv(item:Item):
    item, err = addItem(item=item)
    return item, err
    
def update_item_serv(item:Item):
    item, err = updateItem(item=item)
    return item, err
    
def delete_item_serv(item_id):
    res, err = deleteItem(item_id=item_id)
    return res, err
    