from classes import *
from database import *

def get_admin_serv(admin_id = None, username = None, phone_number = None):
    admin, err = getAdmin(admin_id=admin_id, username=username, phone_number=phone_number)
    return admin, err
    
def get_admins_serv():
    admins, err = getAdmins()
    return admins, err
    
def add_admin_serv(admin:Admin):
    admin, err = addAdmin(admin=admin)
    return admin, err
    
def update_admin_serv(admin:Admin, oldpass = None, newpass = None):
    admin, err = updateAdmin(admin=admin, oldpass=oldpass, newpass=newpass)
    return admin, err
    
def delete_admin_serv(admin:Admin):
    res, err = deleteAdmin(admin=admin)
    return res, err
    
def admin_login_serv(phone_number, password):
    res, err = adminLogin(phone_number=phone_number, password=password)
    return res, err
