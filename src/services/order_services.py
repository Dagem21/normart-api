from classes import *
from database import *

def get_order_serv(order_id):
    order, err = getOrder(order_id=order_id)
    return order, err
    
def get_orders_serv(user_id=None, date=None, status=None, location=None):
    orders, err = getOrders(user_id=user_id, date=date, status=status, location=location)
    return orders, err
    
def add_order_serv(order:Order):
    order, err = addOrder(order=order)
    return order, err
    
def update_order_serv(order:Order):
    order, err = updateOrder(order=order)
    return order, err
    
def delete_order_serv(order_id):
    res, err = deleteOrder(order_id=order_id)
    return res, err