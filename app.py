import os
import random
import base64
from datetime import datetime
from flask_migrate import Migrate
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, json
from flask import Response
from flask_mysqldb import MySQL
from flask_mail import Mail, Message

app = Flask(__name__)

secret_key = os.urandom(24)

app.config['SECRET_KEY'] = secret_key
app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = '1234'  
app.config['MYSQL_DB'] = 'gprems'  

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tankaixin02@gmail.com' 
app.config['MAIL_PASSWORD'] = 'tiat nhzn imzd jnpi'          
mail = Mail(app)

mysql = MySQL(app)
migrate = Migrate(app, mysql)

@app.route('/')
def homepage():
    db = mysql.connection.cursor()

    # Get the event data from the Event table
    db.execute("""
        SELECT eventName, eventDate, eventStartTime, eventEndTime, eventLocation, routeDistance 
        FROM Event
    """)
    events = db.fetchall()

    # Retrieve 'Past Event Images'
    db.execute("SELECT detailPicture FROM EventDetails WHERE eventID = 1 AND detailName = 'Past Event Images'")
    past_event_images = db.fetchall()

    db.close()

    # Convert binary images to base64 encoding
    past_images = []
    for image in past_event_images:
        image_data = image[0]
        base64_encoded_image = base64.b64encode(image_data).decode('utf-8')
        past_images.append(base64_encoded_image)

    if events:
        event_date = events[0][1]  # second column is eventDate
    else:
        event_date = None
    return render_template('Public/homepage.html', events=events, event_date=event_date, past_images=past_images)

@app.route('/upload_images')
def upload_images():
    db = mysql.connection.cursor()

    image_files = [
        'static/Image/past 1.png',
        'static/Image/past 2.png',
        'static/Image/past 3.png',
        'static/Image/past 4.png',
        'static/Image/past 5.png',
    ]

    event_id = 1
    detail_name = 'Past Event Images'
    
    for image_file in image_files:
        with open(image_file, 'rb') as file:
            # Convert image to binary
            binary_data = file.read()

            sql = """
                INSERT INTO EventDetails (eventID, detailName, detailPicture)
                VALUES (%s, %s, %s)
            """
            db.execute(sql, (event_id, detail_name, binary_data))
    
    db.connection.commit()
    db.close()

    return "Images uploaded successfully!"

@app.route('/Public/route')
def route():
    return render_template('Public/route.html')

@app.route('/Public/route/<selected_option>', methods=['GET'])
def get_route_image(selected_option):
    db = mysql.connection.cursor()

    db.execute("SELECT detailPicture FROM EventDetails WHERE eventID = 1 AND detailName = 'Route Images'")
    route_images = db.fetchall()
    db.close()

    # Map selected_option to the corresponding index in the result set
    index = {
        'cafe': 0,      # Bumbledees Cafe
        'muzium': 1,    # Muzium
        'bukit': 2,     # Bukit Cinta
        'hbp': 3,       # HBP
        'fajar': 4,     # Fajar
        'bhepa': 5,     # BHEPA
        'kok': 6,       # Rancangan KOK
        'start': 7,     # Start/Finish
    }

    print(f"index: {index}")

    if selected_option in index:
        print(f"selectedoption:{selected_option}")
        image_index = index[selected_option]
        try:
            route_image = route_images[image_index][0] 
            base64_encoded_image = base64.b64encode(route_image).decode('utf-8')
            return {'image': base64_encoded_image}
        except IndexError:
            return {'error': 'Image not found'}, 404
    else:
        return {'error': 'Invalid selection'}, 400

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
        
        return redirect(url_for('payment', package=package, t_shirt_size=t_shirt_size, matric_number=matric_number, type='student', email=email))
    
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
        
        return redirect(url_for('payment', package=package, t_shirt_size=t_shirt_size, ic_number=ic_number, type='public', email=email))
    
    return render_template('Public/public_register.html')

@app.route('/Public/payment')
def payment():
    package = request.args.get('package')
    t_shirt_size = request.args.get('t_shirt_size')
    user_type = request.args.get('type')
    ic_number = request.args.get('ic_number')
    martic_number = request.args.get('matric_number')
    email = request.args.get('email')
    number = 0

    if user_type == 'public':
        number = ic_number
    elif user_type == 'student':
        number = martic_number

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

    return render_template('Public/payment.html', package=package, t_shirt_size=t_shirt_size, 
                       package_price=package_price, additional_price=additional_price, 
                       total_amount=total_amount, number=number, email=email)

@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    if request.method == 'POST':
        number = request.form.get('number')
        total_amount = request.form.get('total_amount')
        uploaded_file = request.files.get('receipt_upload')  
        email = request.form.get('email')
        package = request.form.get('package')
        t_shirt_size = request.form.get('t_shirt_size')
        package_price = request.form.get('package_price')
        additional_price = request.form.get('additional_price')

        print(f"Email: {email}")
        subject = "Order Confirmation - Glow Paint Run 3KPP"
        message_body = f"""
        <html>
            <body>
                <p>Dear Participant,</p>

                <p>Thank you for your payment of <strong>RM {total_amount}</strong>!</p>

                <p>Here are the details of your order:</p>

                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Order Number:</strong> #123456</p>
                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Selected Package:</strong> {package}</p>
                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Selected T-Shirt Size:</strong> {t_shirt_size}</p>
                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Package Amount:</strong> RM {package_price}</p>
                """
        if float(additional_price) > 0:
            message_body += f"""
                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Additional Price for {t_shirt_size} size:</strong> RM {additional_price}</p>
            """
        message_body += f"""
                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Total Amount:</strong> RM {total_amount}</p>

                <p>We have received your payment receipt. Please stay tuned for our notifications on when to collect your package.</p>

                <p>Thank you for your participation, and we look forward to seeing you soon!</p>

                <p>Best regards,<br>3KPP Team</p>
            </body>
        </html>
        """
        try:
            msg = Message(subject, sender='tankaixin02@gmail.com', recipients=[email])
            msg.html = message_body 
            mail.send(msg)
            print(f"Email2: {email}")
        except Exception as e:
            print(f"Email3: {email}")
            return redirect(request.url)

            
        if uploaded_file and uploaded_file.filename: 
            try:
                # Read the file content and filename
                file_content = uploaded_file.read()
                file_name = uploaded_file.filename

                # Insert file data into the database
                db = mysql.connection.cursor()
                query = """
                    INSERT INTO transaction (userNumber, totalAmount, fileUploaded, fileName)
                    VALUES (%s, %s, %s, %s)
                """
                db.execute(query, (number, total_amount, file_content, file_name))
                mysql.connection.commit()
                db.close()

                return jsonify({"success": True}), 200

            except Exception as e:
                 print(f"Error: {str(e)}")  
                 return jsonify({"success": False, "error": str(e)}), 500

        else:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

@app.route('/download_file/<string:number>')
def download_file(number):
    db = mysql.connection.cursor()
    query = '''
        SELECT T.fileUploaded, T.fileName 
        FROM transaction T
        WHERE T.userNumber = %s
    '''
    db.execute(query, (number,))
    result = db.fetchone()
    db.close()

    if result:
        file_data, file_name = result

        # Determine MIME type based on the file name extension
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = 'application/octet-stream'  # Fallback for unknown file types

        # Return the file as a downloadable response
        return Response(
            file_data,
            mimetype=mime_type,
            headers={"Content-Disposition": f"attachment;filename={file_name}"}
        )
    else:
        return "File not found", 404
        
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
            U.userName,
            U.userEmail,
            U.userPhone,
            JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.matricNumber')) AS matricNumber,
            JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.tShirtSize')) AS tShirtSize,
            JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.campus')) AS campus,
            JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.school')) AS school,
            U.userStatus,
            T.totalAmount, 
            T.fileUploaded,
            T.fileName
        FROM Users U
        LEFT JOIN transaction T ON T.userNumber = JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.matricNumber'))
        WHERE U.userType = 'student';
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
            'status': student[8],
            'totalAmount': student[9],
            'fileUploaded': student[10],
            'fileName': student[11]
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
            userStatus,
            T.totalAmount, 
            T.fileUploaded,
            T.fileName
        FROM Users U
        LEFT JOIN transaction T ON T.userNumber = JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.ICNumber'))
        WHERE U.userType = 'public'; 
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
            'status': public[6],
            'totalAmount': public[7],
            'fileUploaded': public[8],
            'fileName': public[9]
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

@app.route('/Organiser/response')
def response():
    return render_template('Organiser/response.html')

@app.route('/Organiser/about_us')
def o_about_us():
    return render_template('Organiser/about_us.html')

@app.route('/Organiser/contact_us')
def o_contact_us():
    return render_template('Organiser/contact_us.html')

if __name__ == '__main__':
    app.run(debug=True)

