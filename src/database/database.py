from dotenv import load_dotenv
import psycopg2
from psycopg2 import errors
import hashlib, base64
import random, string
from classes import Admin, Coupon, Item, Location, Order, Package, Payment, User, Category

load_dotenv()
# url = os.getenv("DATABASE_URL")
# connection = psycopg2.connect(url)


def close(conn):
    if conn is not None:
        conn.close()

def connect():
    try:
        connection = psycopg2.connect(
            host="localhost",
            port="5433",
            database="normart",
            user="postgres",
            password="postgres")
        return connection, None

    except (Exception, psycopg2.DatabaseError):
        return None, 'An error has occured. Please try again!'

############  User  ####################

def getUser(user_id = None, username = None) -> tuple[User, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if user_id is not None and username is not None:
            return None, "Only one argument must be passed!"
        if user_id is None and username is None:
            return None, "Atleast one argument must be passed!"
        curr = conn.cursor()
        query = "SELECT * FROM users WHERE id = %s;" if user_id is not None else "SELECT * FROM users WHERE username = %s;"
        if user_id is not None:
            curr.execute(query,(user_id,))
        else:
            curr.execute(query, (username,))
        row = curr.fetchone()
        if row:
            user = User(row[0], row[1], row[2], row[3], row[4], row[5])
            close(conn)
            return user, None
        else:
            close(conn)
            return None, "User not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getUsers() -> tuple[list[User], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM users ORDER BY username;"
        curr.execute(query,)
        rows = curr.fetchall()
        users = []
        for row in rows:
            user = User(row[0], row[1], row[2], row[3], row[4], row[5])
            phone_numbers, err = getPhone_numbers(user_id=user.id)
            addresses, err = getAddress(user_id=user.id)
            coupons, err = getUser_coupon(user_id=user.id)
            user.phone_numbers = phone_numbers
            user.addresses = addresses
            user.coupons = coupons
            users.append(user)
        close(conn)
        return users, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addUser(user:User) -> tuple[User, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO users (username, name, password, avatar, api_key) VALUES ( %s, %s, %s, %s, %s) RETURNING id; "
            user.api_key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=40))
            curr.execute(query, (
                user.username,
                user.name,
                hashlib.sha512(base64.b64encode(user.password.encode("utf-8"))).hexdigest(),
                user.avatar,
                user.api_key,
                ))
            conn.commit()
            user.id = curr.fetchone()[0]
        close(conn)
        return user, None
    except errors.UniqueViolation:
        return False, "Username already taken!"
    except errors.NotNullViolation:
        return False, "Please complete the form!"
    except errors.IntegrityError:
        return False, "Username already taken!"
    except Exception:
        return False, 'An error has occured. Please try again!'
    
def updateUser(user:User, oldpass=None, newpass=None) -> tuple[User, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user is None:
            return False, "Please complete the form!"
        if newpass and oldpass:
            if hashlib.sha512(base64.b64encode(oldpass.encode("utf-8"))).hexdigest() == user.password:
                query = "UPDATE users SET password = %s WHERE id = %s;"
                curr.execute(query, (
                    hashlib.sha512(base64.b64encode(newpass.encode("utf-8"))).hexdigest(),
                    user.id,
            ))
            else:
                return None, 'The password provided does not match the previous password.'
        else:
            query = "UPDATE users SET name = %s, avatar = %s WHERE id = %s;"
            curr.execute(query, (
                user.name,
                user.avatar,
                user.id,
            ))
        conn.commit()
        close(conn)
        return user, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteUser(user_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM users WHERE id = %s;"
            curr.execute(query, (user_id,))
            conn.commit()
            res, err = deleteAll_user_phone_number(user_id=user_id)
            if res:
                res, err = deleteAll_user_address(user_id=user_id)
                if res:
                    res, err = deleteAll_user_coupon(user_id=user_id)
                    if res:
                        close(conn)
                        return True, None
            return False, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def userLogin(username, password) -> bool:
    try:
        if username is None or password is None:
            return False, "Username or password missing!"
        user, err = getUser(username=username)
        if err is None:
            if hashlib.sha512(base64.b64encode(password.encode("utf-8"))).hexdigest() == user.password:
                return True, None
        return False, "Invalid credentials provided!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Admin  ####################

def getAdmin(admin_id = None, username = None, phone_number = None) -> tuple[Admin, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if not ((admin_id is not None) ^ (username is not None) ^ (phone_number is not None)):
            return None, "One argument must be passed!"
        curr = conn.cursor()
        
        if admin_id is not None:
            query = "SELECT * FROM admin WHERE id = %s;"
            curr.execute(query,(admin_id,))
        elif username is not None:
            query = "SELECT * FROM admin WHERE username = %s;"
            curr.execute(query, (username,))
        elif phone_number is not None:
            query = "SELECT * FROM admin WHERE phone_number = %s;"
            curr.execute(query, (phone_number,))
        row = curr.fetchone()
        close(conn)
        if row:
            admin = Admin(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            return admin, None
        else:
            return None, "Admin not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getAdmins() -> tuple[list[Admin], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM admin ORDER BY username;"
        curr.execute(query,)
        rows = curr.fetchall()
        admins = []
        for row in rows:
            admin = Admin(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            admins.append(admin)
        close(conn)
        return admins, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addAdmin(admin:Admin) -> tuple[Admin, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if admin is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO admin (username, password, phone_number, last_login, priviledge, api_key) VALUES ( %s, %s, %s, %s, %s, %s) RETURNING id; "
            admin.api_key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=40))
            curr.execute(query, (
                admin.name,
                hashlib.sha512(base64.b64encode(admin.password.encode("utf-8"))).hexdigest(),
                admin.phone_number,
                admin.last_login,
                admin.priviledge,
                admin.api_key,
                ))
            conn.commit()
            admin.id = curr.fetchone()[0]
        close(conn)
        return admin, None
    except errors.UniqueViolation:
        return False, 'This phone number has already been registered!'
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except psycopg2.IntegrityError:
        return False, "Phone number already registered!"
    except Exception:
        return False, 'An error has occured. Please try again!'
    
def updateAdmin(admin:Admin, oldpass = None, newpass = None) -> tuple[Admin, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if admin is None:
            return False, "Please complete the form!"
        
        if newpass and oldpass:
            if hashlib.sha512(base64.b64encode(oldpass.encode("utf-8"))).hexdigest() == admin.password:
                query = "UPDATE admin SET password = %s WHERE id = %s;"
                curr.execute(query, (
                    hashlib.sha512(base64.b64encode(newpass.encode("utf-8"))).hexdigest(),
                    admin.id,
            ))
            else:
                return None, 'The password provided does not match the previous password.'
        else:
            query = "UPDATE admin SET phone_number = %s, last_login = %s, priviledge = %s WHERE id = %s;"
            curr.execute(query, (
                admin.phone_number,
                admin.last_login,
                admin.priviledge,
                admin.id,
                ))
        conn.commit()
        close(conn)
        return admin, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteAdmin(admin:Admin) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if admin is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM admin WHERE id = %s;"
            curr.execute(query, (admin.id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def adminLogin(phone_number, password) -> bool:
    try:
        if phone_number is None or password is None:
            return False, "Phone number or password missing!"
        admin, err = getAdmin(phone_number=phone_number)
        if err is None:
            if hashlib.sha512(base64.b64encode(password.encode("utf-8"))).hexdigest() == admin.password:
                return True, None
        return False, 'Invalid credentials provided.'
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Phone Number  ####################

def getPhone_numbers(user_id) -> tuple[list, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        
        if user_id is None:
            return None, "One argument missing!"
        query = "SELECT * FROM phone_number WHERE user_id = %s;"
        curr.execute(query,(user_id,))
        rows = curr.fetchall()
        numbers = []
        for row in rows:
            numbers.append({row[0]:row[2]})
        close(conn)
        return numbers, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addPhone_number(user_id, phone_number) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None or phone_number is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO phone_number (user_id, phone_number) VALUES ( %s, %s); "
            curr.execute(query, (
                user_id,
                phone_number,
                ))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deletePhone_number(id=None, user_id=None, phone_number=None) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if id is None:
            if user_id is None or phone_number is None:
                return False, "Missing 1 or 2 required arguments!"
            else:
                query = "DELETE FROM phone_number WHERE user_id = %s AND phone_number = %s;"
                curr.execute(query, (user_id, phone_number,))
        else:
            query = "DELETE FROM phone_number WHERE id = %s;"
            curr.execute(query, (id))
        conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteAll_user_phone_number(user_id=None) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None:
            return False, "Missing 1 required arguments!"
        else:
            query = "DELETE FROM phone_number WHERE user_id = %s;"
            curr.execute(query, (user_id,))
        conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Address  ####################

def getAddress(user_id) -> tuple[list, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        
        if user_id is None:
            return None, "One argument missing!"
        query = "SELECT * FROM address WHERE user_id = %s;"
        curr.execute(query,(user_id,))
        rows = curr.fetchall()
        addresses = []
        for row in rows:
            addresses.append({row[0]:row[2]})
        close(conn)
        return addresses, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addAddress(user_id, location) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None or location is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO address (user_id, location) VALUES ( %s, %s); "
            curr.execute(query, (
                user_id,
                location,
                ))
            conn.commit()
        conn.close()
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteAddress(id=None, user_id=None, location=None) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if id is None:
            if user_id is None or location is None:
                return False, "Missing 1 or 2 required arguments!"
            else:
                query = "DELETE FROM address WHERE user_id = %s AND location = %s;"
                curr.execute(query, (user_id, location,))
        else:
            query = "DELETE FROM address WHERE id = %s;"
            curr.execute(query, (id,))
        conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteAll_user_address(user_id=None) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None:
            return False, "Missing 1 required arguments!"
        else:
            query = "DELETE FROM address WHERE user_id = %s;"
            curr.execute(query, (user_id,))
        conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  User Coupon  ####################

def getUser_coupon(user_id) -> tuple[list, str]:
    try:
        conn, err = connect()
        if err is not None:
            return [], "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        
        if user_id is None:
            return [], "One argument missing!"
        query = "SELECT coupon_tag FROM user_coupon WHERE user_id = %s;"
        curr.execute(query,(user_id,))
        rows = curr.fetchall()
        coupons = []
        if len(rows)>0:
            tags = []
            for row in rows:
                tags.append(row)
            coupons, err = getCoupons(tags)
        close(conn)
        return coupons, None
    except errors.NotNullViolation:
        return [], 'Please fill all required fields!'
    except Exception:
        return [], e

def addUser_coupon(user_id, coupon_tag, reason) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None or coupon_tag is None or reason is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO user_coupon (user_id, coupon_tag, reason) VALUES ( %s, %s, %s); "
            curr.execute(query, (
                user_id,
                coupon_tag,
                reason,
                ))
            conn.commit()
        conn.close()
        return True, None
    except errors.ForeignKeyViolation:
        return False, 'Invalid coupon tag!'
    except errors.UniqueViolation:
        return False, 'This coupon has already been claimed!'
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteUser_coupon(id=None, user_id=None, coupon_id=None) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if id is None:
            if user_id is None or coupon_id is None:
                return False, "Missing 1 or 2 required arguments!"
            else:
                query = "DELETE FROM user_coupon WHERE user_id = %s AND coupon_id = %s;"
                curr.execute(query, (user_id, coupon_id,))
        else:
            query = "DELETE FROM user_coupon WHERE id = %s;"
            curr.execute(query, (id,))
        conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

def deleteAll_user_coupon(user_id=None) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if user_id is None:
            return False, "Missing 1 required arguments!"
        else:
            query = "DELETE FROM user_coupon WHERE user_id = %s;"
            curr.execute(query, (user_id,))
        conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Item  ####################

def getItem(item_id, item_name) -> tuple[Item, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if item_id is None and item_name is None:
            return None, "Missing 1 required argument!"
        curr = conn.cursor()
        if item_id:
            query = "SELECT * FROM item WHERE id = %s;"
            curr.execute(query, (item_id,))
        else:
            query = "SELECT * FROM item WHERE name = %s;"
            curr.execute(query, (item_name,))
        row = curr.fetchone()
        close(conn)
        if row:
            item = Item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
            return item, None
        else:
            return None, "Item not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getItems(cat1=None, cat2=None, cat3=None, discount=None) -> tuple[list[Item], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM item"
        params = ""
        if cat1 is not None:
            params += "category1 = '" + cat1 + "'"
        if cat2 is not None:
            if params is not None:
                params += " AND "
            params += "category2 = '" + cat2 + "'"
        if cat3 is not None:
            if params is not None:
                params += " AND "
            params += "category3 = '" + cat3 + "'"
        if discount is not None:
            if params is not None:
                params += " AND "
            params += "discount >= " + str(discount)
        if params != "":
            query += " WHERE " + params
        query += ';'
        curr.execute(query,)
        rows = curr.fetchall()
        items = []
        for row in rows:
            item = Item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
            items.append(item)
        close(conn)
        return items, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getItemsSearch(name) -> tuple[list[Item], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM item where lower(name) like lower(%s);"
        curr.execute(query,('%'+name+'%', ))
        rows = curr.fetchall()
        items = []
        for row in rows:
            item = Item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
            items.append(item)
        close(conn)
        return items, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception as e:
        print(e)
        return None, 'An error has occured. Please try again!'


def getItemsInList(idList=None) -> tuple[list[Item], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if idList is None:
            return None, "One argument missing!"
        query = "SELECT * FROM item where id in %s"
        curr.execute(query,(tuple(idList.split(',')),))
        rows = curr.fetchall()
        items = []
        for row in rows:
            item = Item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
            items.append(item)
        close(conn)
        return items, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addItem(item:Item) -> tuple[Item, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if item is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO item (name, category1, category2, category3, unit, price, image, discount, taxable) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id; "
            curr.execute(query, (
                item.name,
                item.category1,
                item.category2,
                item.category3,
                item.unit,
                item.price,
                item.image,
                item.discount,
                item.taxable,
                ))
            conn.commit()
            item.id = curr.fetchone()[0]
        close(conn)
        return item, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except errors.UniqueViolation:
        return False, 'An item with the same name already exists!'
    except Exception:
        return False, 'An error has occured. Please try again!'
    
def updateItem(item:Item) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if item is None:
            return None, "Missing 1 required argument!"
        
        query = "UPDATE item SET category1 = %s, category2 = %s, category3 = %s, price = %s, image = %s, discount = %s, taxable = %s WHERE id = %s;"
        curr.execute(query, (
            item.category1,
            item.category2,
            item.category3,
            item.price,
            item.image,
            item.discount,
            item.taxable,
            item.id,
            ))
        conn.commit()
        close(conn)
        return item, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deleteItem(item_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if item_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM item WHERE id = %s;"
            curr.execute(query, (item_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception as e:
        print(e)
        return False, 'An error has occured. Please try again!'

############  Location  ####################

def getLocation(location_id) -> tuple[list[Location], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if location_id is None:
            return None, "Missing 1 required argument!"
        curr = conn.cursor()
        query = "SELECT * FROM location WHERE id = %s"
        curr.execute(query,(location_id,))
        row = curr.fetchone()
        location = Location(row[0], row[1], row[2], row[3], row[4])
        close(conn)
        return location, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getLocations() -> tuple[list[Location], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM location"
        curr.execute(query,)
        rows = curr.fetchall()
        locations = []
        for row in rows:
            location = Location(row[0], row[1], row[2], row[3], row[4])
            locations.append(location)
        close(conn)
        return locations, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addLocation(location:Location) -> tuple[Location, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if location is None:
            return False, "Please complete the form!"
        else:
            query = "INSERT INTO location (location, name, working, phone_number) VALUES ( %s, %s, %s, %s) RETURNING id; "
            curr.execute(query, (
                location.location,
                location.name,
                location.working,
                location.phone_number,
                ))
            conn.commit()
            location.id = curr.fetchone()[0]
        close(conn)
        return location, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'
    
def updateLocation(location:Location) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if location is None:
            return None, "Missing 1 required argument!"
        
        query = "UPDATE location SET name = %s, working = %s, phone_number = %s WHERE id = %s;"
        curr.execute(query, (
            location.name,
            location.working,
            location.phone_number,
            location.id,
            ))
        conn.commit()
        close(conn)
        return location, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deleteLocation(location_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if location_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM location WHERE id = %s;"
            curr.execute(query, (location_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Order  ####################

def getOrder(order_id) -> tuple[Order, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if order_id is None:
            return None, "Missing 1 required argument!"
        curr = conn.cursor()
        query = "SELECT * FROM orders WHERE id = %s;"
        curr.execute(query, (order_id,))
        row = curr.fetchone()
        close(conn)
        if row:
            order = Order(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            if order.items is None:
                order.items = []
            if order.packages is None:
                order.packages = []
            return order, None
        else:
            return None, "Order not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getOrders(user_id=None, date=None, status=None, location=None) -> tuple[list[Order], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM orders"
        params = ""
        if user_id is not None:
            params += "user_id = '" + user_id + "'"
        if date is not None:
            if params != "":
                params += " AND "
            params += "date = '" + date + "'"
        if status is not None:
            if params != "":
                params += " AND "
            params += "status = '" + status + "'"
        if location is not None:
            if params != "":
                params += " AND "
            params += "delivery_location = '" + location + "'"
        if params != "":
            query += " WHERE " + params
        query += ' ORDER BY date DESC, id ASC;'
        curr.execute(query,)
        rows = curr.fetchall()
        orders = []
        for row in rows:
            order = Order(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            if order.items is None:
                order.items = []
            if order.packages is None:
                order.packages = []
            orders.append(order)
        close(conn)
        return orders, None
    except errors.NotNullViolation:
        return [], 'Please fill all required fields!'
    except Exception:
        return [], 'An error has occured. Please try again!'

def addOrder(order:Order) -> tuple[Order, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if order is None:
            return False, "Missing 1 required argument!"
        else:
            query = "INSERT INTO orders (user_id, items, packages, date, status, delivery_location) VALUES ( %s, %s, %s, %s, %s, %s) RETURNING id; "
            curr.execute(query, (
                order.user_id,
                order.items,
                order.packages,
                order.date,
                order.status,
                order.delivery_location,
                ))
            conn.commit()
            order.id = curr.fetchone()[0]
        close(conn)
        return order, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'
    
def updateOrder(order:Order) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if order is None:
            return None, "Missing 1 required argument!"
        
        query = "UPDATE orders SET status = %s, delivery_location = %s WHERE id = %s;"
        curr.execute(query, (
            order.status,
            order.delivery_location,
            order.id,
            ))
        conn.commit()
        close(conn)
        return order, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deleteOrder(order_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if order_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM orders WHERE id = %s;"
            curr.execute(query, (order_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Package  ####################

def getPackage(package_id = None, package_name = None) -> tuple[Package, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if package_id is None and package_name is None:
            return None, "Missing 1 required argument!"
        curr = conn.cursor()
        if package_id:
            query = "SELECT * FROM package WHERE id = %s;"
            curr.execute(query, (package_id,))
        else:
            query = "SELECT * FROM package WHERE name = %s;"
            curr.execute(query, (package_name,))
        row = curr.fetchone()
        close(conn)
        if row:
            package = Package(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            return package, None
        else:
            return None, "Package not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getPackages(name=None, start_date=None, expire_date=None) -> tuple[list[Package], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM package"
        params = ""
        if name is not None:
            params += "name = '" + name+ "'"
        if start_date is not None:
            if params != '':
                params += " AND "
            params += "start_date <= '" + start_date + "'"
        if expire_date is not None:
            if params != '':
                params += " AND "
            params += "expire_date >= '" + expire_date + "'"
        if params != "":
            query += " WHERE " + params
        query += ';'
        curr.execute(query,)
        rows = curr.fetchall()
        packages = []
        for row in rows:
            package = Package(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            packages.append(package)
        close(conn)
        return packages, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getPackagesInList(idList=None) -> tuple[list[Package], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if idList is None:
            return None, "One argument missing!"
        query = "SELECT * FROM package where id in %s"
        curr.execute(query,(tuple(idList.split(',')),))
        rows = curr.fetchall()
        packages = []
        for row in rows:
            package = Package(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            packages.append(package)
        close(conn)
        return packages, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addPackage(package:Package) -> tuple[Package, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if package is None:
            return None, "Please complete the form!"
        else:
            query = "INSERT INTO package (name, description, image, start_date, expire_date, items, price) VALUES ( %s, %s, %s, %s, %s, %s, %s) RETURNING id; "
            curr.execute(query, (
                package.name,
                package.description,
                package.image,
                package.start_date,
                package.expire_date,
                package.items,
                package.price,
                ))
            conn.commit()
            package.id = curr.fetchone()[0]
        close(conn)
        return package, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except errors.UniqueViolation:
        return False, 'A package with the same name already exists!'
    except Exception:
        return None, 'An error has occured. Please try again!'
    
def updatePackage(package:Package) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if package is None:
            return None, "Missing 1 required argument!"
        
        query = "UPDATE package SET description = %s, image = %s, expire_date = %s WHERE id = %s;"
        curr.execute(query, (
            package.description,
            package.image,
            package.expire_date,
            package.id,
            ))
        conn.commit()
        close(conn)
        return package, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deletePackage(package_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if package_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM package WHERE id = %s;"
            curr.execute(query, (package_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Payment  ####################

def getPayment(payment_id=None, order_id=None) -> tuple[Payment, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if payment_id is None and order_id is None:
            return None, "Missing 1 required argument!"
        if payment_id is not None and order_id is not None:
            return None, "Only one argument must be provided!"
        curr = conn.cursor()
        if payment_id is not None:
            query = "SELECT * FROM payment WHERE id = %s;"
            curr.execute(query, (payment_id,))
        else:
            query = "SELECT * FROM payment WHERE order_id = %s;"
            curr.execute(query, (order_id,))
        row = curr.fetchone()
        close(conn)
        if row:
            payment = Payment(row[0], row[1], row[2], row[3], row[4], row[5])
            return payment, None
        else:
            return None, "Payment not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addPayment(payment:Payment) -> tuple[Payment, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if payment is None:
            return False, "Missing 1 required argument!"
        else:
            query = "INSERT INTO payment (order_id, price, payed, date, payment_date) VALUES ( %s, %s, %s, %s, %s) RETURNING id; "
            curr.execute(query, (
                payment.order_id,
                payment.price,
                payment.payed,
                payment.date,
                payment.payment_date,
                ))
            conn.commit()
            payment.id = curr.fetchone()[0]
        close(conn)
        return payment, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except errors.UniqueViolation:
        return False, 'An order with the same id already exists!'
    except Exception:
        return False, 'An error has occured. Please try again!'
    
def updatePayment(payment:Payment) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if payment is None:
            return None, "Missing 1 required argument!"
        
        query = "UPDATE payment SET payed = %s, payment_date = %s WHERE id = %s;"
        curr.execute(query, (
            payment.payed,
            payment.payment_date,
            payment.id,
            ))
        conn.commit()
        close(conn)
        return payment, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deletePayment(payment_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if payment_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM payment WHERE id = %s;"
            curr.execute(query, (payment_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return False, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Coupon  ####################

def getCoupon(coupon_id) -> tuple[Coupon, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        if coupon_id is None:
            return None, "Missing 1 required argument!"
        curr = conn.cursor()
        query = "SELECT * FROM coupon WHERE id = %s;"
        curr.execute(query, (coupon_id,))
        row = curr.fetchone()
        if row:
            coupon = Coupon(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            query = "SELECT user_id FROM user_coupon WHERE coupon_tag = %s;"
            curr.execute(query, (coupon.tag,))
            row = curr.fetchone()
            if row:
                coupon.user_id = row[0]
                user, err = getUser(user_id=coupon.user_id)
                if err is None:
                    coupon.owner = user.username
            close(conn)
            return coupon, None
        else:
            close(conn)
            return None, "Coupon not found!"
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def getCoupons(coupon_list=None) -> tuple[list[Coupon], str]:
    try:
        conn, err = connect()
        if err is not None:
            return [], "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if coupon_list is not None:
            query = "SELECT * FROM coupon where tag in %s AND used = False;"
            curr.execute(query,(tuple(coupon_list),))
        else:
            query = "SELECT * FROM coupon;"
            curr.execute(query,)
        rows = curr.fetchall()
        coupons = []
        for row in rows:
            coupon = Coupon(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            query = "SELECT user_id FROM user_coupon WHERE coupon_tag = %s;"
            curr.execute(query, (coupon.tag,))
            row = curr.fetchone()
            if row:
                coupon.user_id = row[0]
                user, err = getUser(user_id=coupon.user_id)
                if err is None:
                    coupon.owner = user.username
            coupons.append(coupon)
        close(conn)
        return coupons, None
    except errors.NotNullViolation:
        return [], 'Please fill all required fields!'
    except Exception:
        return [], e

def addCoupon(coupon:Coupon) -> tuple[Coupon, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if coupon is None:
            return None, "Please complete the form!"
        else:
            tag = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10))
            coupon.tag = tag
            query = "INSERT INTO coupon (tag, coupon_value, start_date, expire_date, used, reusable) VALUES ( %s, %s, %s, %s, %s, %s) RETURNING id; "
            curr.execute(query, (
                coupon.tag,
                coupon.coupon_value,
                coupon.start_date,
                coupon.expire_date,
                coupon.used,
                coupon.reusable,
                ))
            conn.commit()
            coupon.id = curr.fetchone()[0]
        close(conn)
        return coupon, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except errors.UniqueViolation:
        return False, 'A coupon with the same tag already exists!'
    except Exception:
        return None, 'An error has occured. Please try again!'
    
def updateCoupon(coupon:Coupon) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if coupon is None:
            return None, "Missing 1 required argument!"
        
        query = "UPDATE coupon SET coupon_value = %s, expire_date = %s, used = %s, used_date = %s, reusable = %s WHERE id = %s;"
        curr.execute(query, (
            coupon.coupon_value,
            coupon.expire_date,
            coupon.used,
            coupon.used_date,
            coupon.reusable,
            coupon.id,
            ))
        conn.commit()
        close(conn)
        return coupon, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deleteCoupon(coupon_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if coupon_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM coupon WHERE id = %s;"
            curr.execute(query, (coupon_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'

############  Category  ####################

def getCategories() -> tuple[list[Category], str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        query = "SELECT * FROM category;"
        curr.execute(query,)
        rows = curr.fetchall()
        categories = []
        for row in rows:
            category = Category(row[0], row[1], row[2])
            categories.append(category)
        close(conn)
        return categories, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def addCategory(category:Category) -> tuple[Category, str]:
    try:
        conn, err = connect()
        if err is not None:
            return None, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if category is None:
            return None, "Please complete the form!"
        else:
            query = "INSERT INTO category (name, image) VALUES ( %s, %s) RETURNING id; "
            curr.execute(query, (
                category.name,
                category.image,
                ))
            conn.commit()
            category.id = curr.fetchone()[0]
        close(conn)
        return category, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except errors.UniqueViolation:
        return False, 'A category with the same name already exists!'
    except Exception:
        return None, 'An error has occured. Please try again!'

def deleteCategory(category_id) -> tuple[bool, str]:
    try:
        conn, err = connect()
        if err is not None:
            return False, "An error occurred while processing Your request! Please try again."
        curr = conn.cursor()
        if category_id is None:
            return False, "Missing 1 required argument!"
        else:
            query = "DELETE FROM category WHERE id = %s;"
            curr.execute(query, (category_id,))
            conn.commit()
        close(conn)
        return True, None
    except errors.NotNullViolation:
        return None, 'Please fill all required fields!'
    except Exception:
        return False, 'An error has occured. Please try again!'


