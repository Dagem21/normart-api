from classes import *
from database import *

def get_payment_serv(payment_id=None, order_id=None):
    payment, err = getPayment(payment_id=payment_id, order_id=order_id)
    return payment, err
    
def add_payment_serv(payment:Payment):
    payment, err = addPayment(payment=payment)
    return payment, err
    
def update_payment_serv(payment:Payment):
    payment, err = updatePayment(payment=payment)
    return payment, err
    
def delete_payment_serv(payment_id):
    res, err = deletePayment(payment_id=payment_id)
    return res, err