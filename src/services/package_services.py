from classes import *
from database import *

def get_package_serv(package_id =None, package_name = None):
    package, err = getPackage(package_id=package_id, package_name=package_name)
    return package, err
    
def get_packages_serv(name=None, start_date=None, expire_date=None):
    packages, err = getPackages(name=name, start_date=start_date, expire_date=expire_date)
    return packages, err
    
def get_packages_id_list_serv(idList=None):
    packages, err = getPackagesInList(idList=idList)
    return packages, err
    
def add_package_serv(package:Package):
    package, err = addPackage(package=package)
    return package, err
    
def update_package_serv(package:Package):
    package, err = updatePackage(package=package)
    return package, err
    
def delete_package_serv(package_id):
    res, err = deletePackage(package_id=package_id)
    return res, err