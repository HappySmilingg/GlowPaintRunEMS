import os
from io import BytesIO
import logging
logging.basicConfig(level=logging.DEBUG)
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

    db.execute("""
        SELECT eventName, eventDate, eventStartTime, eventEndTime, eventLocation, routeDistance 
        FROM Event
    """)
    events = db.fetchall()

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

# @app.route('/upload_images')
# def upload_images():
#     db = mysql.connection.cursor()

#     # Define image categories with corresponding file paths
#     image_categories = {
#         'Past Event Images': [
#             'static/Image/past 1.png',
#             'static/Image/past 2.png',
#             'static/Image/past 3.png',
#             'static/Image/past 4.png',
#             'static/Image/past 5.png',
#         ],
#         'Route Images': [
#             'static/Image/bumbledees.jpg',
#             'static/Image/muzium.jpg',
#             'static/Image/bukit cinta.jpg',
#             'static/Image/hbp.jpg',
#             'static/Image/fajar.jpg',
#             'static/Image/bhepa.jpg',
#             'static/Image/koko.jpg',
#             'static/Image/the bricks.jpg',
#             'static/Image/routebg.png',
#         ],
#     }

#     event_id = 1  # Set the event ID for all images

#     # Iterate through each category and its images
#     for detail_name, image_files in image_categories.items():
#         for image_file in image_files:
#             with open(image_file, 'rb') as file:
#                 # Convert image to binary
#                 binary_data = file.read()

#                 # Insert into the database
#                 sql = """
#                     INSERT INTO EventDetails (eventID, detailName, detailPicture)
#                     VALUES (%s, %s, %s)
#                 """
#                 db.execute(sql, (event_id, detail_name, binary_data))
    
#     # Commit the changes and close the connection
#     db.connection.commit()
#     db.close()

#     return "Images uploaded successfully!"

@app.route('/upload_images')
def upload_images():
    db = mysql.connection.cursor()

    image_files = [
        'static/Image/profile pic.png'
    ]

    event_id = 1
    detail_name = 'Organiser Profile'
    
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

    return "Images uploaded successfully!"

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

    if selected_option in index:
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
        transportation = request.form.get('transportation')
        
        user_description = {
            "matricNumber": matric_number,
            "package": package,
            "tShirtSize": t_shirt_size,
            "campus": campus,
            "school": school,
            "transport": transportation
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
    db = mysql.connection.cursor()
    db.execute("""
        SELECT detailPicture AS picture, 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name1')) AS name1,
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name2')) AS name2
        FROM EventDetails
        WHERE detailName = 'Organiser Profile'
    """)
    profile_data = db.fetchall()
    profile = None

    if profile_data:
        profile = {
            'picture': base64.b64encode(profile_data[0][0]).decode('utf-8') if profile_data[0][0] else None,
            'name1': profile_data[1][1],     
            'name2': profile_data[1][2]      
        }

    db.execute("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName1')) AS linkName1,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName2')) AS linkName2,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName3')) AS linkName3,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName4')) AS linkName4,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName5')) AS linkName5
        FROM EventDetails
        WHERE detailName = 'Social Link'
    """)
    social_data = db.fetchall()
    social = None

    if social_data:
        social = {
            'linkName1': social_data[0][0],
            'linkName2': social_data[0][1],
            'linkName3': social_data[0][2],
            'linkName4': social_data[0][3],
            'linkName5': social_data[0][4]
        }
    
    db.execute("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName1')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink1')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName2')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink2')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName3')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink3')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName4')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink4')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName5')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink5')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName6')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink6')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName7')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink7')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName8')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink8')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName9')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink9')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName10')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink10')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName11')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink11')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName12')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink12')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName13')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink13')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName14')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink14')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName15')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink15')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName16')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink16')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName17')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink17')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName18')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink18')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName19')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink19')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName20')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink20')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName21')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink21')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName22')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink22')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName23')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink23')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName24')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink24'))
        FROM EventDetails
        WHERE detailName = 'Other Social Link'
    """)

    other_social_data = db.fetchall()
    event = None

    if other_social_data:
        event = {}
        for i in range(1, 25):
            event[f'eventName{i}'] = other_social_data[0][2 * (i - 1)]  
            event[f'eventLink{i}'] = other_social_data[0][2 * (i - 1) + 1] 

    db.close()
    return render_template('Public/about_us.html', profile=profile, social=social, event=event)

@app.route('/Public/contact_us')
def contact_us():
    return render_template('Public/contact_us.html')

@app.route('/Organiser/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       email = request.form['email']
       password = request.form['password']
       
       if email == '123@gmail.com' and password == '123':
          return redirect(url_for('o_homepage')) 
       else:
          flash('Invalid email or password.', 'error')
          return redirect(url_for('login'))
    return render_template('Organiser/login.html')

@app.route('/Organiser/homepage', methods=['GET', 'POST'])
def o_homepage():
    db = mysql.connection.cursor()
    
    for i in range(1, 6): 
        img_file = request.files.get(f'upload-image-{i}')

        if img_file:
            img_data = img_file.read()
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailPicture = %s
                WHERE eventDetailId = %s
                """,
                (img_data, i)
            )

            mysql.connection.commit()
            flash('Your changes have been saved!', 'success')

    db.execute("""
        SELECT eventDetailID, detailPicture 
        FROM EventDetails 
        WHERE eventDetailID BETWEEN 1 AND 5 AND detailName = 'Past Event Images';
    """)
    past_event_images = db.fetchall()

    db.close()

    images = {}
    for image in past_event_images:
        images[image[0]] = {
            "picture": base64.b64encode(image[1]).decode('utf-8') if image[1] else None,
        }

    return render_template('Organiser/homepage.html', images=images)

@app.route('/Organiser/student_participant_list', methods=['GET'])
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
            T.fileName,
            JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.transport')) AS transport
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
            'fileName': student[11],
            'transport': student[12]
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

@app.route('/Organiser/info_list', methods=['GET', 'POST'])
def info_list():
    db = mysql.connection.cursor()

    if request.method == 'POST':
        try:
            for i in range(6, 15): 
                img_name = request.form.get(f'point-{i}')
                img_file = request.files.get(f'upload-image-{i}')

                if img_file:
                    img_data = img_file.read()
                    db.execute(
                        """
                        UPDATE EventDetails
                        SET 
                            detailPicture = %s,
                            detailDescription = CASE
                                WHEN JSON_CONTAINS_PATH(detailDescription, 'one', '$.imgName') THEN
                                    JSON_SET(detailDescription, '$.imgName', %s)
                                ELSE
                                    JSON_SET(detailDescription, '$.imgName', %s)  
                            END
                        WHERE eventDetailId = %s
                        """,
                        (img_data, img_name, img_name, i)
                    )
                else:
                    db.execute(
                        """
                        UPDATE EventDetails
                        SET detailDescription = CASE
                            WHEN JSON_CONTAINS_PATH(detailDescription, 'one', '$.imgName') THEN
                                JSON_SET(detailDescription, '$.imgName', %s)
                            ELSE
                                JSON_SET(detailDescription, '$.imgName', %s)  
                        END
                        WHERE eventDetailId = %s
                        """,
                        (img_name, img_name, i)
                    )

            mysql.connection.commit()
            flash('Your changes have been saved!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash('Failed to save changes. Please try again.', 'error')

    db.execute("""
        SELECT eventDetailId, detailPicture, JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.imgName')) AS detailDescription
        FROM EventDetails
        WHERE eventDetailId BETWEEN 6 AND 14 AND detailName = 'Route Images'
    """)
    event_details = db.fetchall()

    db.close()

    locations = {}
    for detail in event_details:
        locations[detail[0]] = {
            "picture": base64.b64encode(detail[1]).decode('utf-8') if detail[1] else None,
            "img_name": detail[2]
        }

    return render_template('Organiser/info_list.html',
                            location_6=locations.get(6),
                            location_7=locations.get(7),
                            location_8=locations.get(8),
                            location_9=locations.get(9),
                            location_10=locations.get(10),
                            location_11=locations.get(11),
                            location_12=locations.get(12),
                            location_13=locations.get(13),
                            location_14=locations.get(14)
                        )

@app.route('/Organiser/response')
def response():
    return render_template('Organiser/response.html')

@app.route('/Organiser/about_us', methods=['GET', 'POST'])
def o_about_us():
    db = mysql.connection.cursor()

    if request.method == 'POST':
        profile_name1 = request.form.get('name1')  
        profile_name2 = request.form.get('name2')  
        profile_file = request.files.get('profile') 

        if profile_file:
            img_data = profile_file.read()
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailPicture = %s,
                    detailDescription = JSON_SET(detailDescription, '$.name1', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name2', %s)
                WHERE detailName = 'Organiser Profile'
                """,
                (img_data, profile_name1, profile_name2)
            )
        else:
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailDescription = JSON_SET(detailDescription, '$.name1', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name2', %s)
                WHERE detailName = 'Organiser Profile'
                """,
                (profile_name1, profile_name2)
            )

        mysql.connection.commit()

        sociallink1 = request.form.get('link1')
        sociallink2 = request.form.get('link2')
        sociallink3 = request.form.get('link3')
        sociallink4 = request.form.get('link4')
        sociallink5 = request.form.get('link5')

        db.execute(
            """
            UPDATE EventDetails
            SET 
                detailDescription = JSON_SET(detailDescription, '$.linkName1', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName2', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName3', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName4', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName5', %s)
            WHERE detailName = 'Social Link'
            """,
            (sociallink1, sociallink2, sociallink3, sociallink4, sociallink5)
        )

        mysql.connection.commit()

        eventname1 = request.form.get('text1')
        eventlink1 = request.form.get('text2')

        eventname2 = request.form.get('text3')
        eventlink2 = request.form.get('text4')

        eventname3 = request.form.get('text5')
        eventlink3 = request.form.get('text6')

        eventname4 = request.form.get('text7')
        eventlink4 = request.form.get('text8')

        eventname5 = request.form.get('text9')
        eventlink5 = request.form.get('text10')

        eventname6 = request.form.get('text11')
        eventlink6 = request.form.get('text12')

        eventname7 = request.form.get('text13')
        eventlink7 = request.form.get('text14')

        eventname8 = request.form.get('text15')
        eventlink8 = request.form.get('text16')

        eventname9 = request.form.get('text17')
        eventlink9 = request.form.get('text18')

        eventname10 = request.form.get('text19')
        eventlink10 = request.form.get('text20')

        eventname11 = request.form.get('text21')
        eventlink11 = request.form.get('text22')

        eventname12 = request.form.get('text23')
        eventlink12 = request.form.get('text24')

        db.execute(
            """
            UPDATE EventDetails
            SET 
                detailDescription = JSON_SET(detailDescription, '$.eventName1', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName1', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName2', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName2', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName3', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName3', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName4', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName4', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName5', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName5', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName6', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName6', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName7', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName7', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName8', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName8', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName9', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName9', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName10', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName10', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName11', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName11', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName12', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName12', %s)
            WHERE detailName = 'Other Social Link'
            """,
            (
                eventname1, eventlink1,
                eventname2, eventlink2,
                eventname3, eventlink3,
                eventname4, eventlink4,
                eventname5, eventlink5,
                eventname6, eventlink6,
                eventname7, eventlink7,
                eventname8, eventlink8,
                eventname9, eventlink9,
                eventname10, eventlink10,
                eventname11, eventlink11,
                eventname12, eventlink12
            )
        )

        mysql.connection.commit()
        flash('Your changes have been saved!', 'success')

    db.execute("""
        SELECT detailPicture AS picture, 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name1')) AS name1,
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name2')) AS name2
        FROM EventDetails
        WHERE detailName = 'Organiser Profile'
    """)
    profile_data = db.fetchall()
    profile = None

    if profile_data:
        profile = {
            'picture': base64.b64encode(profile_data[0][0]).decode('utf-8') if profile_data[0][0] else None,
            'name1': profile_data[1][1],     
            'name2': profile_data[1][2]      
        }

    db.execute("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName1')) AS linkName1,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName2')) AS linkName2,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName3')) AS linkName3,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName4')) AS linkName4,
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName5')) AS linkName5
        FROM EventDetails
        WHERE detailName = 'Social Link'
    """)
    social_data = db.fetchall()
    social = None

    if social_data:
        social = {
            'linkName1': social_data[0][0],
            'linkName2': social_data[0][1],
            'linkName3': social_data[0][2],
            'linkName4': social_data[0][3],
            'linkName5': social_data[0][4]
        }
    
    db.execute("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName1')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink1')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName2')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink2')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName3')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink3')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName4')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink4')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName5')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink5')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName6')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink6')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName7')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink7')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName8')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink8')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName9')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink9')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName10')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink10')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName11')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink11')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName12')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink12')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName13')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink13')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName14')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink14')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName15')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink15')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName16')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink16')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName17')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink17')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName18')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink18')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName19')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink19')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName20')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink20')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName21')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink21')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName22')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink22')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName23')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink23')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName24')),
            JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink24'))
        FROM EventDetails
        WHERE detailName = 'Other Social Link'
    """)

    other_social_data = db.fetchall()
    event = None

    if other_social_data:
        event = {}
        for i in range(1, 25):
            event[f'eventName{i}'] = other_social_data[0][2 * (i - 1)]  
            event[f'eventLink{i}'] = other_social_data[0][2 * (i - 1) + 1] 

    db.close()
    return render_template('Organiser/about_us.html', profile=profile, social=social, event=event)

@app.route('/Organiser/contact_us')
def o_contact_us():
    return render_template('Organiser/contact_us.html')

if __name__ == '__main__':
    app.run(debug=True)

