from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask import jsonify, json
from datetime import datetime
from flask_migrate import Migrate


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = '1234'  
app.config['MYSQL_DB'] = 'gprems'  

mysql = MySQL(app)
migrate = Migrate(app, mysql)

@app.route('/')
def homepage():
    return render_template('Public/homepage.html')

@app.route('/Public/route')
def route():
    return render_template('Public/route.html')

@app.route('/Public/public_register')
def public_register():
    return render_template('Public/public_register.html')

@app.route('/Public/student_register')
def student_register():
    return render_template('Public/student_register.html')

@app.route('/submit-form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form['full-name']
        matric_number = request.form['matric-number']
        phone = request.form['phone-number']
        email = request.form['email']
        campus = request.form['campus']
        school = request.form['school']
        package = request.form['package-details']
        t_shirt_size = request.form['t-shirt-size']
        
        user_description = {
            "matricNumber": matric_number,
            "package": package,
            "tShirtSize": t_shirt_size,
            "campus": campus,
            "school": school
        }

        now = datetime.now()

        db = mysql.connection.cursor()
        try:
            query = '''
                INSERT INTO users (
                    userName, 
                    userEmail, 
                    userPhone, 
                    userType, 
                    userStatus, 
                    userDescription,
                    registeredDate
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            db.execute(query, (
                name, 
                email, 
                phone, 
                'student',  
                'registered', 
                json.dumps(user_description),
                now
            ))
            mysql.connection.commit()

        except Exception as e:
            mysql.connection.rollback()
            print(f"Error inserting user: {e}")
            return "Error occurred while inserting the record."
        finally:
            db.close()
        
        return redirect(url_for('payment', package=package, t_shirt_size=t_shirt_size))
    
    return render_template('Public/student_register.html')


@app.route('/submit-form2', methods=['POST'])
def submit_form2():
    if request.method == 'POST':
        name = request.form['full-name']
        ic_number = request.form['ic-passport-number']
        phone = request.form['phone-number']
        email = request.form['email']
        package = 'Pro'
        t_shirt_size = request.form['t-shirt-size']
        
        user_description = {
            "ICNumber": ic_number,
            "package": package,
            "tShirtSize": t_shirt_size
        }

        now = datetime.now()

        db = mysql.connection.cursor()
        try:
            query = '''
                INSERT INTO users (
                    userName, 
                    userEmail, 
                    userPhone, 
                    userType, 
                    userStatus, 
                    userDescription,
                    registeredDate
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            db.execute(query, (
                name, 
                email, 
                phone, 
                'public',  
                'registered', 
                json.dumps(user_description),
                now
            ))
            mysql.connection.commit()

        except Exception as e:
            mysql.connection.rollback()
            print(f"Error inserting user: {e}")
            return "Error occurred while inserting the record."
        finally:
            db.close()
        
        return redirect(url_for('payment', package=package, t_shirt_size=t_shirt_size))
    
    return render_template('Public/public_register.html')

@app.route('/Public/payment')
def payment():
    package = request.args.get('package')
    t_shirt_size = request.args.get('t_shirt_size')

    package_price = {
        'Pro': 50,
        'Lite': 35,
        'Starter': 15
    }
    
    additional_price = {
        '3XL': 3,  
        '4XL': 5,
        '5XL': 7,  
        '6XL': 9,  
        '7XL': 11
    }
    
    package_price = package_price.get(package, 0)
    additional_price = additional_price.get(t_shirt_size, 0)
    
    total_amount = package_price + additional_price

    return render_template('Public/payment.html', package=package, t_shirt_size=t_shirt_size, package_price=package_price, additional_price=additional_price, total_amount=total_amount)

@app.route('/Public/packages')
def packages():
    return render_template('Public/packages.html')

@app.route('/Public/about_us')
def about_us():
    return render_template('Public/about_us.html')

@app.route('/Public/contact_us')
def contact_us():
    return render_template('Public/contact_us.html')

@app.route('/Organiser/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       email = request.form['email']
       password = request.form['password']
       
       if email == '123@gmail.com' and password == '123':
          return redirect(url_for('admin_homepage')) 
       else:
          flash('Invalid email or password.', 'error')
          return redirect(url_for('login'))
    return render_template('Organiser/login.html')

@app.route('/Organiser/homepage')
def admin_homepage():
    return render_template('Organiser/homepage.html')

@app.route('/Organiser/student_participant_list')
def student_participant_list():
    db = mysql.connection.cursor()
    query = '''
        SELECT 
            userName,
            userEmail,
            userPhone,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.matricNumber')) AS matricNumber,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.campus')) AS campus,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.school')) AS school,
            userStatus
        FROM Users
        WHERE userType = 'student';
    '''
    db.execute(query)
    students = db.fetchall()  
    db.close() 

    students_data = [
        {
            'name': student[0],
            'email': student[1],
            'phone': student[2],
            'matricNumber': student[3],
            'package': student[4],
            'tShirtSize': student[5],
            'campus': student[6],
            'school': student[7],
            'status': student[8]
        }
        for student in students
    ]
    
    return render_template('Organiser/student_participant_list.html', students=students_data)

@app.route('/update-status/<matricNumber>', methods=['POST'])
def update_status(matricNumber):
    data = request.get_json()
    status = data.get('status')

    db = mysql.connection
    cursor = db.cursor()
    cursor.execute('UPDATE users SET userStatus = %s WHERE JSON_UNQUOTE(JSON_EXTRACT(userDescription, "$.matricNumber")) = %s', (status, matricNumber))
    db.commit()

    return jsonify({'success': True})


@app.route('/Organiser/public_participant_list')
def public_participant_list():
    db = mysql.connection.cursor()
    query = '''
        SELECT 
            userName,
            userEmail,
            userPhone,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.ICNumber')) AS ICNumber,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
            userStatus
        FROM Users
        WHERE userType = 'public';  
    '''
    db.execute(query)
    publics = db.fetchall()  
    db.close() 

    publics_data = [
        {
            'name': public[0],
            'email': public[1],
            'phone': public[2],
            'ICNumber': public[3],
            'package': public[4],
            'tShirtSize': public[5],
            'status': public[6]
        }
        for public in publics
    ]

    return render_template('Organiser/public_participant_list.html', publics=publics_data)

@app.route('/update-status2/<ICNumber>', methods=['POST'])
def update_status2(ICNumber):
    data = request.get_json()
    status = data.get('status')

    db = mysql.connection
    cursor = db.cursor()
    cursor.execute('UPDATE users SET userStatus = %s WHERE JSON_UNQUOTE(JSON_EXTRACT(userDescription, "$.ICNumber")) = %s', (status, ICNumber))
    db.commit()

    return jsonify({'success': True})

@app.route('/Organiser/info_list')
def info_list():
    return render_template('Organiser/info_list.html')

if __name__ == '__main__':
    app.run(debug=True)

