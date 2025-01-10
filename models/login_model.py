from MySQLdb.cursors import DictCursor

class LoginModel:
    def __init__(self, db):
        self.db = db
    
    def check_user_credentials(self, email):
        db = self.db.cursor(DictCursor)
        db.execute("SELECT userEmail, userPassword FROM users WHERE userType = 'admin' AND userEmail = %s", (email,))
        user = db.fetchone()
        db.close()
        return user
    
    def update_user_password(self, email, hashed_password):
        try:
            db = self.db.cursor()
            db.execute("UPDATE users SET userPassword = %s WHERE userType = 'admin' AND userEmail = %s", (hashed_password, email))
            self.db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False
    