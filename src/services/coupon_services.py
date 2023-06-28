from classes import *
from database import *

def get_coupon_serv(coupon_id = None):
    coupon, err = getCoupon(coupon_id=coupon_id)
    return coupon, err
    
def get_coupons_serv():
    coupons, err = getCoupons()
    return coupons, err
    
def add_coupon_serv(coupon:Coupon):
    coupon, err = addCoupon(coupon=coupon)
    return coupon, err
    
def update_coupon_serv(coupon:Coupon):
    coupon, err = updateCoupon(coupon=coupon)
    return coupon, err
    
def delete_coupon_serv(coupon_id):
    res, err = deleteCoupon(coupon_id=coupon_id)
    return res, err