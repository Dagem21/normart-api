from classes import *
from database import *

def get_user_serv(user_id = None, username = None):
    user, err = getUser(user_id=user_id, username=username)
    return user, err
def get_users_serv():
    users, err = getUsers()
    return users, err
def add_user_serv(user:User):
    user, err = addUser(user=user)
    return user, err
def update_user_serv(user:User, oldpass=None, newpass=None):
    user, err = updateUser(user=user, oldpass=oldpass, newpass=newpass)
    return user, err
def delete_user_serv(user_id):
    res, err = deleteUser(user_id=user_id)
    return res, err

def login_serv(username, password):
    res, err = userLogin(username=username, password=password)
    return res, err

def get_phone_number_serv(user_id):
    res, err = getPhone_numbers(user_id=user_id)
    return res, err
def add_phone_number_serv(user_id, phone_number):
    res, err = addPhone_number(user_id=user_id, phone_number=phone_number)
    return res, err
def delete_phone_number_serv(id, user_id, phone_number):
    res, err = deletePhone_number(id=id, user_id=user_id, phone_number=phone_number)
    return res, err
    
def get_address_serv(user_id):
    res, err = getAddress(user_id=user_id)
    return res, err
def add_address_serv(user_id, location):
    res, err = addAddress(user_id=user_id, location=location)
    return res, err
def delete_address_serv(id, user_id, location):
    res, err = deleteAddress(id=id, user_id=user_id, location=location)
    return res, err
    
def get_user_coupons_serv(user_id):
    res, err = getUser_coupon(user_id=user_id)
    return res, err
def add_user_coupon_serv(user_id, coupon_tag, reason):
    res, err = addUser_coupon(user_id=user_id, coupon_tag=coupon_tag, reason=reason)
    return res, err
def delete_user_coupon_serv(id, user_id, coupon_id):
    res, err = deleteUser_coupon(id=id, user_id=user_id, coupon_id=coupon_id)
    return res, err