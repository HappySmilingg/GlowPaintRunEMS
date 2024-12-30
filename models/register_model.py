import json

class UserModel:
    def __init__(self, db):
        self.db = db

    def insert_user(self, user_data):
        try:
            query = '''
                INSERT INTO users (userName, userEmail, userPhone, userType, userStatus, userDescription, registeredDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            db = self.db.cursor()
            db.execute(query, (
                user_data['name'], 
                user_data['email'], 
                user_data['phone'], 
                user_data['userType'],  
                'registered', 
                json.dumps(user_data['userDescription']),
                user_data['now']
            ))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error inserting user: {e}")
            return False
        finally:
            db.close()

class PaymentModel:
    def __init__(self, db):
        self.db = db
    
    def get_active_students(self, number):
        query = """
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.matricNumber')) AS matricNumber,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
            userEmail AS email
        FROM users
        WHERE JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.matricNumber')) = %s 
        AND userType = 'student' AND userStatus = 'registered';
        """
        self.db.execute(query, (number,))
        return self.db.fetchall()

    def get_active_public_users(self, number):
        query = """
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.ICNumber')) AS ICNumber,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
            userEmail AS email
        FROM users
        WHERE JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.ICNumber')) = %s 
        AND userType = 'public' AND userStatus = 'registered';
        """
        self.db.execute(query, (number,))
        return self.db.fetchall()
    
    def get_package_details(self, package):
        query = """
            SELECT packageName, price
            FROM packages
            WHERE packageName = %s AND packageStatus = 'active';
        """
        self.db.execute(query, (package,))
        return self.db.fetchall()

    def get_tshirt_sizes(self, size):
        query = """
            SELECT sizeName, sizePrice
            FROM tshirt_size
            WHERE sizeName = %s
            ORDER BY sizeID;
        """
        self.db.execute(query, (size,))
        return self.db.fetchall()

    def save_payment(self, order_number, number, total_amount, file_content, file_name):
        try:
            query = """
                INSERT INTO payment (orderNumber, userNumber, totalAmount, fileUploaded, fileName)
                VALUES (%s, %s, %s, %s, %s)
            """
            db = self.db.cursor()
            db.execute(query, (order_number, number, total_amount, file_content, file_name))
            self.db.commit()
            db.close()
        except Exception as e:
            print(f"Error saving payment: {e}")
            raise e