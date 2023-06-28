from classes import *
from database import *

def get_location_serv(location_id):
    location, err = getLocation(location_id=location_id)
    return location, err

def get_locations_serv():
    locations, err = getLocations()
    return locations, err
    
def add_location_serv(location:Location):
    location, err = addLocation(location=location)
    return location, err
    
def update_location_serv(location:Location):
    location, err = updateLocation(location=location)
    return location, err
    
def delete_location_serv(location_id):
    res, err = deleteLocation(location_id=location_id)
    return res, err