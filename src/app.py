from flask import Flask, request, jsonify, send_file
from classes import *
from services import *
from flask_cors import CORS
import random, string
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

def save_image(req, loc):
    try:
        allowed = set(['png'])
        filename = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=40))+'.png'
        if 'file' not in req.files:
            return False
        file = req.files['file']
        if file:
            file.save(os.path.join(loc, filename))
            return filename
    except Exception as e:
        print(e, '---------')

################ Admin ##################
@app.route("/api/admin/get", methods = ["POST"])
def get_admin():
    try:
        args = request.form
        if len(args) > 0:
            admin = None
            err = None
            key = list(args.keys())[0]
            value = list(args.values())[0]
            if key == 'admin_id':
                admin, err = get_admin_serv(admin_id=value)
            if key == 'username':
                admin, err = get_admin_serv(username=value)
            if key == 'phone_number':
                admin, err = get_admin_serv(phone_number=value)
            if err is not None:
                return jsonify({'error':err}), 400
            if admin is None:
                return jsonify({}), 404
            return admin.tojson(), 200
        return jsonify({}), 404
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500
    
@app.route("/api/admins/get", methods = ["POST"])
def get_admins():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        admins, err = get_admins_serv()
        if err is not None:
            return jsonify({'error':err}), 400
        if admins is None:
            return jsonify({}), 404
        admins_json = []
        for admin in admins:
            admins_json.append(admin.tojson())
        return jsonify(admins_json), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500
    
@app.route("/api/admin", methods = ["POST", "PUT", "DELETE"])
def cud_admin():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        if request.method == 'POST':
            admin = Admin()
            for key, value in args.items():
                if key == 'name':
                    admin.name = value
                elif key == 'password':
                    admin.password = value
                elif key == 'phone_number':
                    admin.phone_number = value
                elif key == 'last_login':
                    admin.last_login = value
                elif key == 'priviledge':
                    admin.priviledge = value
            if admin.complete():
                admin, err = add_admin_serv(admin=admin)
                if err is not None:
                    return jsonify({'error':err}), 400
                if admin:
                    return admin.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'PUT':
            if admin:
                oldpass = None
                newpass = None
                for key, value in args.items():
                    if key == 'password':
                        oldpass = value
                    elif key == 'newpassword':
                        newpass = value
                    elif key == 'phone_number':
                        admin.phone_number = value
                    elif key == 'last_login':
                        admin.last_login = value
                    elif key == 'priviledge':
                        admin.priviledge = value
                admin, err = update_admin_serv(admin=admin, oldpass=oldpass, newpass=newpass)
                if err is not None:
                    return jsonify({'error':err}), 400
                if admin:
                    return admin.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'DELETE':
            admin_id = args.get('admin_id')
            if not admin_id:
                return jsonify({}), 400
            admin = Admin(id=admin_id)
            res, err = delete_admin_serv(admin=admin)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/adminlogin/get", methods = ["POST"])
def admin_login():
    try:
        args = request.form
        password = args.get('password')
        phone_number = args.get('phone_number')
        res, err = admin_login_serv(phone_number=phone_number, password=password)
        if err is not None:
            return jsonify({'error':err}), 400
        if res:
            admin, err = get_admin_serv(phone_number=phone_number)
            curr_date = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            admin.last_login = curr_date
            admin, err = update_admin_serv(admin=admin)
            if err is not None:
                return jsonify({'error':err}), 400
            res = admin.tojson()
            res['login'] = 'True'
            return res, 200
        return jsonify({'error':err}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500


############# Coupon ###############
@app.route("/api/coupon/get", methods = ["POST"])
def get_coupon():
    try:
        args = request.form
        coupon_id = args.get('coupon_id')
        if not coupon_id:
            return jsonify({}), 400
        coupon, err = get_coupon_serv(coupon_id=coupon_id)
        if err is not None:
            return jsonify({'error':err}), 400
        return coupon.tojson(), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/coupons/get", methods = ["POST"])
def get_coupons():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if err is not None:
            return jsonify({'error':err}), 400
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        coupons, err = get_coupons_serv()
        if err is not None:
            return jsonify({'error':err}), 400
        coupons_json = []
        for coupon in coupons:
            coupons_json.append(coupon.tojson())
        return jsonify(coupons_json), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/usercoupons/get", methods = ["POST"])
def get_user_coupons():
    try:
        args = request.form
        user_id = args.get('user_id')
        coupons, err = get_user_coupons_serv(user_id=user_id)
        if err is not None:
            return jsonify({'error':err}), 400
        coupons_json = []
        for coupon in coupons:
            coupons_json.append(coupon.tojson())
        return jsonify(coupons_json), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/coupon", methods = ["POST", "PUT", "DELETE"])
def cud_coupon():
    try:
        args = request.form
        if request.method == 'POST':
            admin_id = args.get('admin_id')
            admin_api_key = args.get('api_key')
            admin, err = get_admin_serv(admin_id=admin_id)
            if admin_api_key != admin.api_key:
                return jsonify({}), 403
            coupon = Coupon()
            for key, value in args.items():
                if key == 'coupon_value':
                    coupon.coupon_value = value
                elif key == 'start_date':
                    coupon.start_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else package.start_date
                elif key == 'expire_date':
                    coupon.expire_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else datetime.strptime('2099-12-31', '%Y-%m-%d')
                elif key == 'reusable':
                    coupon.reusable = value
            coupon.used = False
            if coupon.complete():
                coupon, err = add_coupon_serv(coupon=coupon)
                if err is not None:
                    return jsonify({'error':err}), 400
                if coupon:
                    return coupon.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'PUT':
            coupon_id = args.get('coupon_id')
            coupon, err = get_coupon_serv(coupon_id=coupon_id)
            if coupon:
                for key, value in args.items():
                    if key == 'coupon_value':
                        coupon.coupon_value = value
                    elif key == 'start_date':
                        coupon.start_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else coupon.start_date
                    elif key == 'expire_date':
                        coupon.expire_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else datetime.strptime('2099-12-31', '%Y-%m-%d')
                    elif key == 'reusable':
                        coupon.reusable = value
                    elif key == 'used':
                        coupon.used = value
                    elif key == 'used_date':
                        coupon.used_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else coupon.used_date
                coupon, err = update_coupon_serv(coupon=coupon)
                if err is not None:
                    return jsonify({'error':err}), 400
                if coupon:
                    return coupon.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'DELETE':
            admin_id = args.get('admin_id')
            admin_api_key = args.get('api_key')
            admin, err = get_admin_serv(admin_id=admin_id)
            if admin_api_key != admin.api_key:
                return jsonify({}), 403
            coupon_id = args.get('coupon_id')
            res, err = delete_coupon_serv(coupon_id=coupon_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500
    
################## Item #################
@app.route("/api/item/get", methods = ["POST"])
def get_item():
    try:
        args = request.form
        item_id = args.get('item_id')
        item_name = args.get('item_name')
        if not item_id and not item_name:
            return jsonify({}), 400
        item, err = get_item_serv(item_id=item_id, item_name=item_name)
        if err is not None:
            return jsonify({'error':err}), 400
        if item:
            return item.tojson(), 200
        return jsonify({}), 404
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/items/get", methods = ["POST"])
def get_items():
    try:
        args = request.form
        category1 = args.get('category1')
        category2 = args.get('category2')
        category3 = args.get('category3')
        discount = args.get('discount')
        id_list = args.get('id_list')
        items = None
        if id_list:
            items, err = get_items_id_list_serv(idList=id_list)
            if err is not None:
                return jsonify({'error':err}), 400
        else:
            items, err = get_items_serv(cat1=category1, cat2=category2, cat3=category3, discount=discount)
            if err is not None:
                return jsonify({'error':err}), 400
        items_json = []
        for item in items:
            items_json.append(item.tojson())
        return jsonify(items_json), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/items/search/get", methods = ["POST"])
def get_search_items():
    try:
        args = request.form
        name = args.get('name')
        print(args)
        items, err = get_items_search_serv(name)
        if err is not None:
            return jsonify({'error':err}), 400
        items_json = []
        for item in items:
            items_json.append(item.tojson())
        return jsonify(items_json), 200
    except Exception as e:
        print(e)
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/item", methods = ["POST", "PUT", "DELETE"])
def cud_item():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        if request.method == 'POST':
            filename = save_image(req=request, loc='images/items')
            item = Item()
            for key, value in args.items():
                if key == 'name':
                    item.name = value.capitalize()
                elif key == 'category1':
                    item.category1 = value
                elif key == 'category2':
                    item.category2 = value if value != '' else None
                elif key == 'category3':
                    item.category3 = value if value != '' else None
                elif key == 'unit':
                    item.unit = value.upper()
                elif key == 'price':
                    item.price = value
                elif key == 'discount':
                    item.discount = value if value != '' else None
                elif key == 'taxable':
                    item.taxable = value if value != '' else None
            item.image = filename
            if item.complete():
                item, err = add_item_serv(item=item)
                if err is not None:
                    return jsonify({'error':err}), 400
                if item:
                    return item.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'PUT':
            item_id = args.get('item_id')
            item, err = get_item_serv(item_id=item_id)
            if item:
                filename = save_image(req=request, loc='images/items')
                for key, value in args.items():
                    if key == 'name':
                        item.name = value
                    elif key == 'category1':
                        item.category1 = value
                    elif key == 'category2':
                        item.category2 = value if value != '' else item.category2
                    elif key == 'category3':
                        item.category3 = value if value != '' else item.category3
                    elif key == 'unit':
                        item.unit = value.upper()
                    elif key == 'price':
                        item.price = value
                    elif key == 'discount':
                        item.discount = value if value != '' else item.discount
                        if value == '' and item.discount != None:
                            item.discount = None
                    elif key == 'taxable':
                        item.taxable = value if value != '' else item.taxable
                if filename:
                    item.image = filename
                item, err = update_item_serv(item=item)
                if err is not None:
                    return jsonify({'error':err}), 400
                if item:
                    return item.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'DELETE':
            item_id = args.get('item_id')
            res, err = delete_item_serv(item_id=item_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

    
############# Location ##################
@app.route("/api/locations/get", methods = ["POST"])
def get_locations():
    try:
        locations, err = get_locations_serv()
        if err is not None:
            return jsonify({'error':err}), 400
        locations_json = []
        for location in locations:
            locations_json.append(location.tojson())
        return jsonify(locations_json), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/location", methods = ["POST", "PUT", "DELETE"])
def cud_location():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        if request.method == 'POST':
            location = Location()
            for key, value in args.items():
                if key == 'location':
                    location.location = value.capitalize()
                elif key == 'name':
                    location.name = value.capitalize()
                elif key == 'working':
                    location.working = value
                elif key == 'phone_number':
                    location.phone_number = value
            if location.complete():
                location, err = add_location_serv(location=location)
                if err is not None:
                    return jsonify({'error':err}), 400
                if location:
                    return location.tojson(), 201
            return jsonify({}), 400
            
        elif request.method == 'PUT':
            location_id = args.get('location_id')
            location, err = get_location_serv(location_id=location_id)
            for key, value in args.items():
                if key == 'location':
                    location.location = value.capitalize()
                elif key == 'name':
                    location.name = value.capitalize()
                elif key == 'working':
                    location.working = value
                elif key == 'phone_number':
                    location.phone_number = value
            location, err = update_location_serv(location=location)
            if err is not None:
                return jsonify({'error':err}), 400
            if location:
                return location.tojson(), 201
            return jsonify({}), 400
            
        elif request.method == 'DELETE':
            location_id = args.get('location_id')
            res, err = delete_location_serv(location_id=location_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500


############### Order ###############
@app.route("/api/order/get", methods = ["POST"])
def get_order():
    try:
        args = request.form
        order_id = args.get('order_id')
        order, err = get_order_serv(order_id=order_id)
        if err is not None:
            return jsonify({'error':err}), 400
        if order:
            return order.tojson(), 200
        return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/orders/get", methods = ["POST"])
def get_orders():
    try:
        args = request.form
        user_id = args.get('user_id')
        date = args.get('date')
        status = args.get('status')
        location = args.get('location')
        orders, err = get_orders_serv(user_id=user_id, date=date, status=status, location=location)
        if err is not None:
            return jsonify({'error':err}), 400
        orders_json = []
        for order in orders:
            jsonorder = order.tojson()
            user, err = get_user_serv(user_id = order.user_id)
            jsonorder['name'] = user.name
            orders_json.append(jsonorder)
        return jsonify(orders_json), 200
        return jsonify({}), 404
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/order", methods = ["POST", "PUT", "DELETE"])
def cud_order():
    try:
        args = request.form
        if request.method == 'POST':
            order = Order()
            for key, value in args.items():
                if key == 'user_id':
                    order.user_id = value
                elif key == 'items':
                    order.items = [i for i in value.split(',')]
                elif key == 'packages':
                    order.packages = [i for i in value.split(',')]
                elif key == 'date':
                    order.date = datetime.strptime(value, '%Y-%m-%d')
                elif key == 'status':
                    order.status = value
                elif key == 'delivery_location':
                    order.delivery_location = value
            if order.complete():
                order, err = add_order_serv(order=order)
                if err is not None:
                    return jsonify({'error':err}), 400
                if order:
                    return order.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'PUT':
            order_id = args.get('order_id')
            order, err = get_order_serv(order_id=order_id)
            for key, value in args.items():
                if key == 'status':
                    order.status = value
                elif key == 'delivery_location':
                    order.delivery_location = value
            order, err = update_order_serv(order=order)
            if err is not None:
                return jsonify({'error':err}), 400
            if order:
                return order.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'DELETE':
            order_id = args.get('order_id')
            res, err = delete_order_serv(order_id=order_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500


############# Package #################
@app.route("/api/package/get", methods = ["POST"])
def get_package():
    try:
        args = request.form
        package_id = args.get('package_id')
        package_name = args.get('package_name')
        package, err = get_package_serv(package_id=package_id, package_name=package_name)
        if err is not None:
            return jsonify({'error':err}), 400
        if package:
            return package.tojson(), 200
        return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/packages/get", methods = ["POST"])
def get_packages():
    try:
        args = request.form
        name = args.get('name')
        start_date = args.get('start_date')
        expire_date = args.get('expire_date')
        id_list = args.get('id_list')
        packages = None
        if id_list:
            packages, err = get_packages_id_list_serv(idList=id_list)
            if err is not None:
                return jsonify({'error':err}), 400
        else:
            if start_date is None:
                start_date = datetime.today().strftime('%Y/%m/%d')
            if expire_date is None:
                expire_date = datetime.today().strftime('%Y/%m/%d')
            packages, err = get_packages_serv(name=name, start_date=start_date, expire_date=expire_date)
            if err is not None:
                return jsonify({'error':err}), 400
        if packages:
            packages_json = []
            for package in packages:
                packages_json.append(package.tojson())
            return jsonify(packages_json), 200
        return jsonify({}), 404
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/package", methods = ["POST", "PUT", "DELETE"])
def cud_package():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        if request.method == 'POST':
            filename = save_image(req=request, loc='images/packages')
            package = Package()
            for key, value in args.items():
                if key == 'name':
                    package.name = value.capitalize()
                elif key == 'description':
                    package.description = value.capitalize()
                elif key == 'start_date':
                    package.start_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else package.start_date
                elif key == 'expire_date':
                    package.expire_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else datetime.strptime('2099-12-31', '%Y-%m-%d')
                elif key == 'items':
                    package.items = [i for i in value.split(',')]
                elif key == 'price':
                    package.price = value
            package.image = filename
            if package.complete():
                package, err = add_package_serv(package=package)
                if err is not None:
                    return jsonify({'error':err}), 400
                if package:
                    return package.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'PUT':
            package_id = args.get('package_id')
            package_name = args.get('package_name')
            package, err = get_package_serv(package_id=package_id, package_name=package_name)
            if package:
                filename = save_image(req=request, loc='images/packages')
                for key, value in args.items():
                    if key == 'description':
                        package.description = value.capitalize() if value != '' else package.description
                    elif key == 'expire_date':
                        package.expire_date = datetime.strptime(value, '%Y-%m-%d') if value != '' else package.expire_date
                if filename:
                    package.image = filename
                package, err = update_package_serv(package=package)
                if err is not None:
                    return jsonify({'error':err}), 400
                if package:
                    return package.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'DELETE':
            package_id = args.get('package_id')
            res, err = delete_package_serv(package_id=package_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception:
        return jsonify({'error':'An error has occured. Please try again!'}), 500


############# Category #################
@app.route("/api/categories/get", methods = ["POST"])
def get_categories():
    try:
        categories, err = get_categories_serv()
        if err is not None:
            return jsonify({'error':err}), 400
        if categories:
            categories_json = []
            for category in categories:
                categories_json.append(category.tojson())
            return jsonify(categories_json), 200
        return jsonify({}), 404
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/category", methods = ["POST", "DELETE"])
def cud_category():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        if request.method == 'POST':
            filename = save_image(req=request, loc='images/categories')
            category = Category()
            for key, value in args.items():
                if key == 'name':
                    category.name = value.capitalize()
            category.image = filename
            if category.complete():
                category, err = add_category_serv(category=category)
                if err is not None:
                    return jsonify({'error':err}), 400
                if category:
                    return category.tojson(), 201
            return jsonify({}), 400

        elif request.method == 'DELETE':
            category_id = args.get('category_id')
            res, err = delete_category_serv(category_id=category_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500


############# Payment ###############
@app.route("/api/payment/get", methods = ["POST"])
def get_payment():
    try:
        args = request.form
        payment_id = args.get('payment_id')
        payment, err = get_payment_serv(payment_id=payment_id)
        if err is not None:
            return jsonify({'error':err}), 400
        if payment:
            return payment.tojson(), 200
        return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/payment", methods = ["POST", "PUT", "DELETE"])
def cud_payment():
    try:
        args = request.form
        if request.method == 'POST':
            payment = Payment()
            for key, value in args.items():
                if key == 'order_id':
                    payment.order_id = value
                elif key == 'price':
                    payment.price = value
                elif key == 'payed':
                    payment.payed = value
                elif key == 'date':
                    payment.date = value
                elif key == 'payment_date':
                    payment.payment_date = value
            if payment.complete():
                payment, err = add_payment_serv(payment=payment)
                if err is not None:
                    return jsonify({'error':err}), 400
                if payment:
                    return payment.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'PUT':
            payment_id = args.get('payment_id')
            payment, err = get_payment_serv(payment_id=payment_id)
            if payment:
                for key, value in args.items():
                    if key == 'payed':
                        payment.payed = value
                    elif key == 'payment_date':
                        payment.payment_date = value
                payment, err = update_payment_serv(payment=payment)
                if err is not None:
                    return jsonify({'error':err}), 400
                if payment:
                    return payment.tojson(), 201
            return jsonify({}), 400
        
        elif request.method == 'DELETE':
            payment_id = args.get('payment_id')
            res, err = delete_payment_serv(payment_id=payment_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500


############### User ###################
@app.route("/api/userdetails/get", methods = ["POST"])
def get_user_details():
    try:
        args = request.form
        user_id = args.get('user_id')
        user, err = get_user_serv(user_id=user_id)
        if user:
            user.phone_numbers, err = get_phone_number_serv(user_id=user_id)
            user.addresses, err = get_address_serv(user_id=user_id)
            coupons, err = get_user_coupons_serv(user_id=user_id)
            if err is not None:
                return jsonify({'error':err}), 400
            coupons_json = []
            for coupon in coupons:
                coupons_json.append(coupon.tojson())
            user.coupons = coupons_json
            return user.tojsonall(), 200
        return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/userdetails", methods = ["POST", "DELETE"])
def cd_user_details():
    try:
        args = request.form
        user_id = args.get('user_id')
        datatype = args.get('datatype')
        if request.method == "POST":
            if datatype == 'phone_number':
                user_api_key = args.get('api_key')
                user, err = get_user_serv(user_id=user_id)
                if user_api_key != user.api_key:
                    return jsonify({}), 403
                phone_number = args.get('phone_number')
                res, err = add_phone_number_serv(user_id=user_id, phone_number=phone_number)
                if err is not None:
                    return jsonify({'error':err}), 400
                if res:
                    return jsonify({}), 201
            elif datatype == 'address':
                user_api_key = args.get('api_key')
                user, err = get_user_serv(user_id=user_id)
                if user_api_key != user.api_key:
                    return jsonify({}), 403
                location = args.get('location')
                res, err = add_address_serv(user_id=user_id, location=location)
                if err is not None:
                    return jsonify({'error':err}), 400
                if res:
                    return jsonify({}), 201
            elif datatype == 'coupon':
                coupon_tag = args.get('tag')
                reason = args.get('reason')
                res, err = add_user_coupon_serv(user_id=user_id, coupon_tag=coupon_tag, reason=reason)
                print(err, '-============')
                if err is not None:
                    return jsonify({'error':err}), 400
                if res:
                    return jsonify({}), 201
            return jsonify({}), 400
    
        elif request.method == "DELETE":
            data_id = args.get('id')
            if datatype == 'phone_number':
                phone_number = args.get('phone_number')
                res, err = delete_phone_number_serv(id=data_id, user_id=user_id, phone_number=phone_number)
                if err is not None:
                    return jsonify({'error':err}), 400
                if res:
                    return jsonify({}), 200
            elif datatype == 'address':
                location = args.get('location')
                res, err = delete_address_serv(id=data_id, user_id=user_id, location=location)
                if err is not None:
                    return jsonify({'error':err}), 400
                if res:
                    return jsonify({}), 200
            elif datatype == 'coupon':
                coupon_id = args.get('coupon_id')
                res, err = delete_user_coupon_serv(id=data_id, user_id=user_id, coupon_id=coupon_id)
                if err is not None:
                    return jsonify({'error':err}), 400
                if res:
                    return jsonify({}), 200
            return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/user/get", methods = ["POST"])
def get_user():
    try:
        args = request.form
        user_id = args.get('user_id')
        username = args.get('username')
        if username:
            username = username.upper()
        user, err = get_user_serv(user_id=user_id, username=username)
        if err is not None:
            return jsonify({'error':err}), 400
        if user:
            return user.tojson(), 200
        return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/users/get", methods = ["POST"])
def get_users():
    try:
        args = request.form
        admin_id = args.get('admin_id')
        admin_api_key = args.get('api_key')
        admin, err = get_admin_serv(admin_id=admin_id)
        if admin_api_key != admin.api_key:
            return jsonify({}), 403
        users, err = get_users_serv()
        if err is not None:
            return jsonify({'error':err}), 400
        if users:
            users_json = []
            for user in users:
                user.coupons = [coupon.tojson() for coupon in user.coupons]
                users_json.append(user.tojsonall())
            return jsonify(users_json), 200
        return jsonify({}), 404
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/user", methods = ["POST", "PUT", "DELETE"])
def cud_user():
    try:
        args = request.form
        if request.method == 'POST':
            user = User(
                name=args.get("name"),
                username=args.get("username").upper(),
                password=args.get("password"),
                avatar=1 if (args.get("avatar") == None) else args.get("avatar")
            )
            if user.complete():
                user, err = add_user_serv(user=user)
                if err is not None:
                    return jsonify({'error':err}), 400
                if user:
                    return user.tojson(), 201
            return jsonify({}), 400
        elif request.method == 'PUT':
            user_id = args.get('user_id')
            user_api_key = args.get('api_key')
            user, err = get_user_serv(user_id=user_id)
            if user_api_key != user.api_key:
                return jsonify({}), 403
            if user:
                oldpass = None
                newpass = None
                for key, value in args.items():
                    if key == 'name':
                        user.name = value
                    elif key == 'password':
                        oldpass = value
                    elif key == 'newpassword':
                        newpass = value
                    elif key == 'avatar':
                        user.avatar = value
                user, err = update_user_serv(user=user, oldpass=oldpass, newpass=newpass)
                if err is not None:
                    return jsonify({'error':err}), 400
                if user:
                    return user.tojson(), 201
            return jsonify({}), 400
        elif request.method == 'DELETE':
            user_id = args.get('user_id')
            user_api_key = args.get('api_key')
            user, err = get_user_serv(user_id=user_id)
            if user_api_key != user.api_key:
                return jsonify({}), 403
            res, err = delete_user_serv(user_id=user_id)
            if err is not None:
                return jsonify({'error':err}), 400
            if res:
                return jsonify({}), 200
            else:
                return jsonify({}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.route("/api/login/get", methods = ["POST"])
def user_login():
    try:
        args = request.form
        password = args.get('password')
        username = args.get('username').upper()
        res, err = login_serv(username=username, password=password)
        if err is not None:
            return jsonify({'error':err}), 400
        if res:
            user, err = get_user_serv(username=username)
            if err is not None:
                return jsonify({'error':err}), 400
            res = user.tojson()
            res['login'] = 'True'
            return res, 200
        return jsonify({"error":err}), 400
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

@app.get("/")
def home():
    return jsonify({
        'get admin' : "POST - /api/admin/get?admin_id='',username='',phone_number=''",
        'get admins' : "POST - /api/admins/get?admin_id='',api_key=''",
        'add admin' : "POST - /api/admin?name='',password='',phone_number='',last_login='',priviledge='',admin_id='',api_key=''",
        'update admin' : "PUT - /api/admin?password='', phone_number='',last_login='',priviledge='',admin_id='',api_key=''",
        'delete admin' : "DELETE - /api/admin?admin_id='',admin_id='',api_key=''",
        'admin login' : "POST - /api/adminlogin/get?phone_number='',password=''",
        'get coupon' : "POST - /api/coupon/get?coupon_id=''",
        'get coupons' : "POST - /api/coupons/get?admin_id='',api_key=''",
        'add coupon' : "POST - /api/coupon?admin_id='',api_key='',coupon_value='',start_date='',expire_date='',reusable=''",
        'update coupon' : "PUT - /api/coupon?admin_id='',api_key='',coupon_id='',coupon_value='',start_date='',expire_date='',reusable=''",
        'delete coupon' : "DELETE - /api/coupon?admin_id='',api_key='',coupon_id=''",
        'get item' : "POST - /api/item/get?item_id=''",
        'get items' : "POST - /api/items/get?category1='',category2='',category3='',discount=''",
        'add item' : "POST - /api/item?admin_id='',api_key='',name='',category1='',category2='',category3='',unit='',price='',image='',discount='',taxable=''",
        'update item' : "PUT - /api/item?admin_id='',api_key='',item_id='',name='',category1='',category2='',category3='',price='',image='',discount='',taxable=''",
        'delete item' : "DELETE - /api/item?admin_id='',api_key='',item_id=''",
        'get locations' : "POST - /api/locations/get",
        'add location' : "POST - /api/location?admin_id='',api_key='',location='',name='',working='',phone_number=''",
        'update location' : "PUT - /api/location?admin_id='',api_key='',location_id='',location='',name='',working='',phone_number=''",
        'delete location' : "DELETE - /api/locaiton?admin_id='',api_key='',location_id=''",
        'get order' : "POST - /api/order/get?order_id=''",
        'get orders' : "POST - /api/orders/get?user_id='',date='',status='',location=''",
        'add order' : "POST - /api/order?user_id='',items='',date='',status='',delivery_location=''",
        'update order' : "PUT - /api/order?order_id='',status='',delivery_location=''",
        'delete order' : "DELETE - /api/order?order_id=''",
        'get package' : "POST - /api/package/get?package_id=''",
        'get packages' : "POST - /api/packages/get?name='',start_date='',expire_date=''",
        'add package' : "POST - /api/package?admin_id='',api_key='',name='',description='',image='',start_date='',expire_date='',items='',price=''",
        'update package' : "PUT -/api/package?admin_id='',api_key='',description='',image='',expire_date=''",
        'delete package' : "DELETE - /api/package?admin_id='',api_key='',package_id=''",
        'get payment' : "POST - /api/payment/get?payment_id=''",
        'add payment' : "POST - /api/payment?order_id='',price='',payed='',date='',payment_date=''",
        'update payment' : "PUT - /api/payment?payment_id='',payed='',payment_date=''",
        'delete payment' : "DELETE - /api/payment?payment_id=''",
        'get user details' : "POST - /api/userdetails/get?user_id=''",
        'add user details' : "POST - /api/userdetails?user_id='',datatype='',api_key='',phone_number='',location='',coupon_id='', reason=''",
        'delete user details' : "DLETE - /api/userdetails?id='',datatype='',phone_number='',location='',coupon_id=''",
        'get user' : "POST - /api/user/get?user_id,username=''",
        'get users' : "POST - /api/users/get?admin_id='',api_key=''",
        'add user' : "POST - /api/user?name='',username='',password='',avatar=''",
        'update user' : "PUT - /api/user?user_id='',api_key='',name='',password='',avatar=''",
        'delete user' : "DELETE - /api/user?user_id='',api_key='',",
        'login' : "POST - /api/login/get?username='',password=''",
    }), 200

@app.route("/api/image")
def image_server():
    try:
        args = request.args
        loc = args.get('type')
        if loc == 'item':
            loc = 'images/items'
        elif loc == 'package':
            loc = 'images/packages'
        elif loc == 'category':
            loc = 'images/categories'
        else:
            loc = 'images'
        filename = args.get('filename')
        fullpath = os.path.join(loc, filename)
        return send_file(fullpath, mimetype='image/png'), 200
    except Exception as e:
        return jsonify({'error':'An error has occured. Please try again!'}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")