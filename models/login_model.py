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
    