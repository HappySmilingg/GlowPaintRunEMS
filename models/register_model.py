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
            self.db.execute(query, (
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
            self.db.connection.rollback()
            print(f"Error inserting user: {e}")
            return False
        finally:
            self.db.close()

class PaymentModel:
    def __init__(self, db):
        self.db = db

    def insert_payment(self, payment_data):
        try:
            query = """
                INSERT INTO payment (orderNumber, userNumber, totalAmount, fileUploaded, fileName)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute(query, (
                payment_data['order_number'],
                payment_data['number'],
                payment_data['total_amount'],
                payment_data['file_content'],
                payment_data['file_name']
            ))
            self.db.commit()
            return True
        except Exception as e:
            self.db.connection.rollback()
            print(f"Error saving transaction: {e}")
            return False
        finally:
            self.db.close()

    def save_payment(self, order_number, number, total_amount, file_content, file_name):
        try:
            query = """
                INSERT INTO payment (orderNumber, userNumber, totalAmount, fileUploaded, fileName)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute(query, (order_number, number, total_amount, file_content, file_name))
            self.db.commit()
            self.db.close()
        except Exception as e:
            print(f"Error saving payment: {e}")
            raise e