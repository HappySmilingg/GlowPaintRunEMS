import os
import re
from io import BytesIO
import logging
logging.basicConfig(level=logging.DEBUG)
import base64
from datetime import datetime
from flask_migrate import Migrate
from MySQLdb.cursors import DictCursor
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, json
from flask import Response
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)

secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Example: 16 MB

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

# Create a Jinja2 environment with the 'enumerate' filter
env = Environment(loader=FileSystemLoader('.'))
env.filters['enumerate'] = enumerate

@app.route('/')
def homepage():
    db = mysql.connection.cursor()

    db.execute("""
        SELECT eventName, eventDate, eventStartTime, eventEndTime, eventLocation, routeDistance 
        FROM Event
    """)
    events = db.fetchall()

    db.execute("""
        SELECT JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.titleDesc')), 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark1')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark2')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark3')) 
        FROM eventDetails
        WHERE eventDetailId = 21 AND detailName = 'Event Info';
    """)
    sub_detail = db.fetchall()
    sub_details = None
    if sub_detail:
        sub_details = {
            'description': sub_detail[0][0] or '',
            'info1': sub_detail[0][1] or '',
            'info2': sub_detail[0][2] or '',
            'info3': sub_detail[0][3] or ''
    }

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
    return render_template('Public/homepage.html', events=events, event_date=event_date, sub_details=sub_details, past_images=past_images)

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
    db = mysql.connection.cursor()  
    db.execute("""
        SELECT sizeName, sizePrice
        FROM tshirt_size
        ORDER BY sizeID;
    """)
    sizes = db.fetchall()
    db.close()

    return render_template('Public/public_register.html', sizes=sizes)


@app.route('/Public/student_register')
def student_register():
    db = mysql.connection.cursor()  
    db.execute("""
        SELECT distinct packageName, price, hasTShirt
        FROM packages 
        WHERE packageStatus = 'active';
    """)
    packages = db.fetchall()

    db.execute("""
        SELECT sizeName, sizePrice
        FROM tshirt_size
        ORDER BY sizeID;
    """)
    sizes = db.fetchall()

    db.close()
    return render_template('Public/student_register.html', packages=packages, sizes=sizes)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        try:
            name = request.form.get('full-name')
            matric_number = request.form.get('matric-number')
            phone = request.form.get('phone-number')
            email = request.form.get('email')
            campus = request.form.get('campus')
            school = request.form.get('school')
            package = request.form.get('package-details')
            t_shirt_size = request.form.get('t-shirt-size')
            transportation = request.form.get('transportation', '')

            # User description in JSON
            user_description = {
                "matricNumber": matric_number,
                "package": package,
                "tShirtSize": t_shirt_size,
                "campus": campus,
                "school": school,
                "transport": transportation
            }

            # Use UTC timestamp
            now = datetime.now()

            # Database operation
            with mysql.connection.cursor() as db:
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
            return "An error occurred. Please try again.", 500
        
        return redirect(url_for('payment', type='student'))

    return render_template('Public/student_register.html')


@app.route('/submit-form2', methods=['POST'])
def submit_form2():
    if request.method == 'POST':
        try:
            name = request.form.get('full-name')
            ic_number = request.form.get('ic-passport-number')
            phone = request.form.get('phone-number')
            email = request.form.get('email')
            t_shirt_size = request.form.get('t-shirt-size')

            # Fixed package value
            package = 'Glow-Rious Pro'

            # User description in JSON
            user_description = {
                "ICNumber": ic_number,
                "package": package,
                "tShirtSize": t_shirt_size
            }

            # Use UTC timestamp
            now = datetime.now()

            # Database operation
            with mysql.connection.cursor() as db:
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
            return "An error occurred. Please try again.", 500
        
        return redirect(url_for('payment', type='public'))

    return render_template('Public/public_register.html')

@app.route('/Public/payment', methods=['GET'])
def payment():
    user_type = request.args.get('type')
    db = mysql.connection.cursor()

    # Retrieve active student data
    db.execute("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.matricNumber')) AS matricNumber,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
            userEmail AS email
        FROM users
        WHERE userType = 'student' AND userStatus = 'registered';
    """)
    student = db.fetchall()

    # Retrieve active public user data
    db.execute("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.ICNumber')) AS ICNumber,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
            JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
            userEmail AS email
        FROM users
        WHERE userType = 'public' AND userStatus = 'registered';
    """)
    public = db.fetchall()

    # Initialize variables
    number = None
    email = None
    package = None
    t_shirt_size = None
    package_price = 0
    size_price = 0

    # Process student or public data based on 'type' parameter
    if user_type == 'public' and public:
        number = public[0][0]
        package = student[0][1]
        t_shirt_size = public[0][2]
        email = public[0][3]
    elif user_type == 'student' and student:
        number = student[0][0]
        package = student[0][1]
        t_shirt_size = student[0][2]
        email = student[0][3]

    
    if number:
        first_six_digits = number[:6] if len(number) >= 6 else number
    else:
        first_six_digits = '000000'  # Default value if 'number' is None

    # Combine with current date in ddmmyy format
    current_date = datetime.now().strftime('%d%m%y')
    order_number = f"{first_six_digits}{current_date}"

    # Retrieve package details
    db.execute("""
        SELECT packageName, price
        FROM packages
        WHERE packageStatus = 'active';
    """)
    package_details = db.fetchall()

    # Retrieve t-shirt size details
    db.execute("""
        SELECT sizeName, sizePrice
        FROM tshirt_size
        ORDER BY sizeID;
    """)
    size_details = db.fetchall()

    # Calculate the total amount (assuming you get the right package and size prices)
    if package_details and size_details:
        package_price = int(package_details[0][1]) if package_details else 0
        size_price = int(size_details[0][1]) if size_details else 0
        total_amount = package_price + size_price
    else:
        total_amount = 0

    return render_template('Public/payment.html', package=package, t_shirt_size=t_shirt_size, 
                           package_price=package_price, additional_price=size_price, total_amount=total_amount, 
                           number=number, email=email, order_number=order_number)

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
        order_number = request.form.get('order_number')

        subject = "Order Confirmation - Glow Paint Run 3KPP"
        message_body = f"""
        <html>
            <body>
                <p>Dear Participant,</p>

                <p>Thank you for your payment of <strong>RM {total_amount}</strong>!</p>

                <p>Here are the details of your order:</p>

                <p><strong>&nbsp;&nbsp;&nbsp;&nbsp;Order Number:</strong> {order_number}</p>
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
                    INSERT INTO payment (orderNumber, userNumber, totalAmount, fileUploaded, fileName)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute(query, (order_number, number, total_amount, file_content, file_name))
                mysql.connection.commit()
                db.close()

                return jsonify({"success": True}), 200

            except Exception as e:
                 return jsonify({"success": False, "error": str(e)}), 500

        else:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

@app.route('/download_file/<string:number>')
def download_file(number):
    db = mysql.connection.cursor()
    query = '''
        SELECT T.fileUploaded, T.fileName 
        FROM payment T
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
    db = mysql.connection.cursor(DictCursor)  # Use DictCursor to fetch rows as dictionaries
    db.execute("""
        SELECT P.packageName, P.price, I.itemName
        FROM packages P
        LEFT JOIN items I ON I.itemID = P.itemID
        WHERE P.packageStatus = 'active';
    """)
    results = db.fetchall()
    db.close()

    # Group items by package
    packages = {}
    for row in results:
        package_name = row['packageName']
        price = row['price']
        item_name = row['itemName']
        if package_name not in packages:
            packages[package_name] = {
                'price': price,
                'items': []
            }
        packages[package_name]['items'].append(item_name)

    # Add a note for specific packages (example: "Only for USM Student")
    for package in packages:
        if package.lower().endswith('lite') or package.lower().endswith('starter'):
            packages[package]['note'] = '#Only for USM Student'
        else:
            packages[package]['note'] = '#Available for USM Student & Public Participant'

    return render_template('Public/packages.html', packages=packages)

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
    db = mysql.connection.cursor()

    db.execute("""
        SELECT detailPicture, 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.message')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
        FROM EventDetails
        WHERE eventDetailId = 19 AND detailName = 'Contact Us'
    """)
    contact_data = db.fetchall()

    db.execute("""
        SELECT detailPicture, 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
        FROM EventDetails
        WHERE eventDetailId = 20 AND detailName = 'Contact Us'
    """)
    contact_data2 = db.fetchall()

    contact = None
    contact2 = None

    if contact_data:
       contact = {
            'profile': base64.b64encode(contact_data[0][0]).decode('utf-8') if contact_data[0][0] else None,
            'message': contact_data[0][1],
            'title': contact_data[0][2],
            'position': contact_data[0][3],
            'name': contact_data[0][4],
            'contact': contact_data[0][5],
        }

    if contact_data2:
       contact2 = {
            'profile': base64.b64encode(contact_data2[0][0]).decode('utf-8') if contact_data2[0][0] else None,
            'title': contact_data2[0][1],
            'position': contact_data2[0][2],
            'name': contact_data2[0][3],
            'contact': contact_data2[0][4],
        }

    db.close()

    return render_template('Public/contact_us.html', contact=contact, contact2=contact2)

@app.route('/Organiser/login', methods=['GET', 'POST'])
def login():
    db = mysql.connection.cursor(DictCursor)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db.execute("SELECT userEmail, userPassword FROM users WHERE userType = 'admin' AND userEmail = %s", (email,))
        user = db.fetchone()

        if user and user['userPassword'] == password:
            return redirect(url_for('o_homepage'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    return render_template('Organiser/login.html')

@app.route('/Organiser/homepage', methods=['GET', 'POST'])
def o_homepage():
    db = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form.get('text-title')
        description = request.form.get('text-desc')
        date = request.form.get('text-date')
        time1 = request.form.get('text-time1')
        time2 = request.form.get('text-time2')
        venue = request.form.get('text-venue')
        distance = request.form.get('text-distance')
        remark1 = request.form.get('text-info1')
        remark2 = request.form.get('text-info2')
        remark3 = request.form.get('text-info3')
        print("sub_details:", title)

    
        try:
            if description or remark1 or remark2 or remark3:
                db.execute(
                    """
                    UPDATE EventDetails
                    SET detailDescription = JSON_SET(
                        detailDescription, 
                        '$.titleDesc', COALESCE(%s, ''),
                        '$.remark1', COALESCE(%s, ''),
                        '$.remark2', COALESCE(%s, ''),
                        '$.remark3', COALESCE(%s, '')
                    )
                    WHERE eventDetailId = 21 AND detailName = 'Event Info';
                    """,
                    (description, remark1, remark2, remark3)
                )
                print("sub_details:", description, remark1, remark2, remark3)
                mysql.connection.commit()

            if title or date or time1 or time2 or venue or distance:
                time_start = f"{date} {time1}" 
                time_end = f"{date} {time2}"

                db.execute(
                    """
                    UPDATE Event
                    SET eventName = %s,
                        eventDate = %s, 
                        eventStartTime = %s, 
                        eventEndTime = %s,
                        eventLocation = %s,
                        routeDistance = %s;
                    """,
                    (title, date, time_start, time_end, venue, distance)
                )
                mysql.connection.commit()
                
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
        except Exception as e:
            mysql.connection.rollback()
            flash('Failed to save changes. Please try again.', 'error')

    db.execute("""
        SELECT eventName, 
               DATE(eventDate),
               TIME(eventStartTime),
               TIME(eventEndTime), 
               eventLocation, 
               routeDistance 
        FROM Event;
    """)
    mains = None
    main = db.fetchall()
    if main:
       mains = {
            'name': main[0][0],
            'date': main[0][1],
            'time1': main[0][2],
            'time2': main[0][3],
            'venue': main[0][4],
            'distance': main[0][5]
        }
    
    mains['time1'] = datetime.strptime(str(mains['time1']), "%H:%M:%S").strftime("%H:%M")
    mains['time2'] = datetime.strptime(str(mains['time2']), "%H:%M:%S").strftime("%H:%M")

    db.execute("""
        SELECT JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.titleDesc')), 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark1')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark2')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark3')) 
        FROM eventDetails
        WHERE eventDetailId = 21 AND detailName = 'Event Info';
    """)
    sub_detail = db.fetchall()
    sub_details = None
    if sub_detail:
        sub_details = {
            'description': sub_detail[0][0] or '',
            'info1': sub_detail[0][1] or '',
            'info2': sub_detail[0][2] or '',
            'info3': sub_detail[0][3] or ''
        }

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

    return render_template('Organiser/homepage.html', mains=mains, sub_details=sub_details, images=images)

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
        LEFT JOIN payment T ON T.userNumber = JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.matricNumber'))
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
        LEFT JOIN payment T ON T.userNumber = JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.ICNumber'))
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

@app.route('/Organiser/packages', methods=['GET', 'POST'])
def or_packages():
    db = mysql.connection.cursor(DictCursor)
    if request.method == 'POST':
        print(request.form)
        # Handle updates for T-shirt sizes
        tshirt_sizes = []
        for key in request.form:
            if key.startswith('sizes['):
                # Check if it's a new size or existing size
                if '[new]' in key:
                    # Handle new sizes
                    field_name = key.split('[')[3].split(']')[0]
                    index = key.split('[')[2].split(']')[0]

                    # Ensure tshirt_sizes list has enough entries for new sizes
                    while len(tshirt_sizes) <= int(index):
                        tshirt_sizes.append({"is_new": True})

                    tshirt_sizes[int(index)][field_name] = request.form[key]
                else:
                    # Handle existing sizes
                    size_id = key.split('[')[1].split(']')[0]
                    field_name = key.split('[')[2].split(']')[0]

                    # Ensure tshirt_sizes list has enough entries for existing sizes
                    while len(tshirt_sizes) <= int(size_id):
                        tshirt_sizes.append({"sizeID": size_id})

                    tshirt_sizes[int(size_id)][field_name] = request.form[key]

        # Process T-shirt sizes
        for size in tshirt_sizes:
            size_id = size.get('sizeID')
            size_name = size.get('sizeName')
            size_price = size.get('sizePrice')
            delete_flag = size.get('delete', '0')
            if delete_flag == '1' and size_id:
                db.execute("DELETE FROM Tshirt_size WHERE sizeID = %s", (size_id,))
                continue
            if size_id:
                db.execute(
                    "UPDATE Tshirt_size SET sizeName = %s, sizePrice = %s WHERE sizeID = %s",
                    (size_name, size_price, size_id)
                )
            elif size.get("is_new"):
                db.execute(
                    "INSERT INTO Tshirt_size (sizeName, sizePrice) VALUES (%s, %s)",
                    (size_name, size_price)
                )

        # Handle updates for Items
        items = []
        for key in request.form:
            if key.startswith('items['):
                # Check if this is a new item
                if '[new]' in key:
                    # Extract the field name and index for the new item
                    field_name = key.split('[')[3].split(']')[0]
                    index = key.split('[')[2].split(']')[0]

                    # Ensure the items list is large enough to accommodate the new item
                    while len(items) <= int(index):
                        items.append({"is_new": True})

                    # Assign the value to the respective field in the new item
                    items[int(index)][field_name] = request.form[key]
                else:
                    # Extract item_id and field_name for existing items
                    item_id = key.split('[')[1].split(']')[0]
                    field_name = key.split('[')[2].split(']')[0]

                    # Ensure the items list is large enough to accommodate the existing item
                    while len(items) <= int(item_id):
                        items.append({"itemID": item_id})

                    # Assign the value to the respective field in the existing item
                    items[int(item_id)][field_name] = request.form[key]

        # Loop through each item to handle updates or inserts
        for item in items:
            item_id = item.get('itemID')
            item_name = item.get('itemName')
            delete_flag = item.get('delete')

            # Handle item deletion
            if delete_flag == '1' and item_id:
                db.execute("UPDATE Items SET itemStatus = 'deleted' WHERE itemID = %s", (item_id,))
                continue
            if item_id:
                # Update existing item
                db.execute("UPDATE Items SET itemName = %s WHERE itemID = %s", (item_name, item_id))
            elif item.get("is_new"):
                # Insert new item if it's not marked for deletion and has a name
                db.execute("INSERT INTO Items (itemName, itemStatus) VALUES (%s, 'active')", (item_name,))
        
        packages = []

        # Loop through the form data
        for key in request.form:
            if key.startswith('packages['):  # We are dealing with packages
                if '[new]' in key:  # This is a new package
                    index = key.split('[')[2].split(']')[0]

                    # Ensure the packages list is large enough to accommodate the new package
                    while len(packages) <= int(index):
                        packages.append({"is_new": True, "items": []})

                    # Determine if this is a package-level field or an item
                    if '[items]' in key:  # Handle package items
                        item_id = key.split('[')[4].split(']')[0]  # Extract itemID
                        item_name = request.form[key]  # Extract itemName
                        packages[int(index)]["items"].append({"itemID": item_id, "itemName": item_name})
                    else:  # Handle package-level fields
                        field_name = key.split('[')[3].split(']')[0]  # Extract field name (e.g., packageName, price)
                        packages[int(index)][field_name] = request.form[key]

                else:  # This is an existing package
                    # Get the submitted package ids
                    submitted_package_ids = list(set([str(int(key.split('[')[1].split(']')[0]) + 1)]))
                    # Delete all packages whose packageID is NOT in the submitted list
                    if submitted_package_ids:
                        query = f"DELETE FROM Packages WHERE packageID NOT IN ({', '.join(submitted_package_ids)})"
                        db.execute(query)

                    package_id = key.split('[')[1].split(']')[0]  # Extract package index

                    # Initialize package if not already done
                    if len(packages) <= int(package_id):
                        packages.append({
                            "packageID": request.form.get(f"packages[{package_id}][packageID]"),
                            "packageName": request.form.get(f"packages[{package_id}][packageName]"),
                            "price": request.form.get(f"packages[{package_id}][price]"),
                            "items": []
                        })

                    # If the key contains 'items', process the item data
                    if 'items' in key:
                        # Extract the index of the item (e.g., [1], [2], etc.)
                        item_index = int(key.split('[')[3].split(']')[0])

                        # Get the item name
                        item_name = request.form[key]

                        # Add the item directly if it exists
                        if item_name:
                            packages[int(package_id)]["items"].append({
                                "itemID": item_index,
                                "itemName": item_name
                            })

        # Print the result for debugging
        print(f"packages: {packages}")

        # Handle updates for Packages
        for package in packages:
            package_id = package.get('packageID')
            package_name = package.get('packageName')
            price = package.get('price')
            items_in_package = package.get('items', [])  
            has_tshirt = any(item['itemName'].lower() == "t-shirt" for item in items_in_package)

            print("status:", has_tshirt)
            if package_id:
                # Update an existing package
                db.execute(
                    "UPDATE Packages SET packageName = %s, price = %s WHERE packageID = %s",
                    (package_name, price, package_id)
                )
                print("packageID:", package_id)
                # Get a list of current item IDs for the package from the database
                db.execute("SELECT itemID FROM Packages WHERE packageID = %s", (package_id,))
                current_items = {row['itemID'] for row in db.fetchall()}

                print("Items in package:", items_in_package)
                print("Current items:", current_items)

                # Determine which items to delete
                items_to_delete = current_items - {item['itemID'] for item in items_in_package}
                print("Deleted items:", items_to_delete)
                # Delete items no longer part of the package
                for item_id in items_to_delete:
                    db.execute(
                        "DELETE FROM Packages WHERE packageID = %s AND itemID = %s",
                        (package_id, item_id)
                    )

                # Determine which items to add
                items_to_add = {item['itemID'] for item in items_in_package} - current_items
                print("Items to add:", items_to_add)
                
                # Add new items to the package
                for item_id in items_to_add:
                    db.execute(
                        "INSERT INTO Packages (packageID, packageName, price, hasTShirt, itemID) VALUES (%s, %s, %s, %s, %s)",
                        (package_id, package_name, price, has_tshirt, item_id)
                    )
            elif package.get("is_new"):
                # Insert the new package and get the new package ID
                db.execute("SELECT MAX(packageID) + 1 AS new_package_id FROM Packages")
                new_package_id = db.fetchone()["new_package_id"]

                # Insert a row for each item in the new package
                for item in package["items"]:
                    db.execute(
                        "INSERT INTO Packages (packageID, packageName, price, hasTShirt, itemID) VALUES (%s, %s, %s, %s, %s)",
                        (new_package_id, package["packageName"], package["price"], has_tshirt, item["itemID"])
                    )

        mysql.connection.commit()
        flash('Your changes have been saved!', 'success')
    else:
        flash('Failed to save changes. Please try again.', 'error')

    # Fetch data for display
    db.execute("SELECT sizeID, sizeName, sizePrice FROM Tshirt_size ORDER BY sizeID")
    tshirt_sizes = db.fetchall()

    db.execute("SELECT itemID, itemName FROM Items WHERE itemStatus = 'active' ORDER BY itemID")
    items = db.fetchall()

    db.execute("SELECT itemID, itemName FROM Items WHERE itemStatus = 'active' ORDER BY itemID")

    # Query to fetch packages and their items
    db.execute("""
        SELECT p.packageID, p.packageName, p.price, i.itemID, i.itemName
        FROM Packages p
        LEFT JOIN Items i ON i.itemID = p.itemID
        WHERE p.packageStatus = 'active' AND i.itemStatus = 'active'
        ORDER BY p.packageID, p.itemID;
    """)
    raw_packages = db.fetchall()

    # Organize the data for display
    packages = {}
    for row in raw_packages:
        package_id = row['packageID']
        if package_id not in packages:
            # Add new package entry
            packages[package_id] = {
                'packageID': package_id,
                'packageName': row['packageName'],
                'price': row['price'],
                'items': []
            }
        if row['itemID']:
            # Append item to the package's item list
            packages[package_id]['items'].append({
                'itemID': row['itemID'],
                'itemName': row['itemName']
            })

    return render_template('Organiser/packages.html', tshirt_sizes=tshirt_sizes, items=items, packages=list(packages.values()), enumerate=enumerate)

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

@app.route('/Organiser/contact_us', methods=['GET', 'POST'])
def o_contact_us():
    db = mysql.connection.cursor()

    if request.method == 'POST':
        try:
            message = request.form.get('desc')
            title = request.form.get('desc2')
            position = request.form.get('desc3')
            name = request.form.get('desc4')
            contact = request.form.get('desc5')
            img_file = request.files.get('profile')

            if img_file:
                img_data = img_file.read()
                db.execute(
                    """
                    UPDATE EventDetails
                    SET 
                        detailPicture = %s,
                        detailDescription = JSON_SET(detailDescription, '$.message', %s),
                        detailDescription = JSON_SET(detailDescription, '$.title', %s),
                        detailDescription = JSON_SET(detailDescription, '$.position', %s),
                        detailDescription = JSON_SET(detailDescription, '$.name', %s),
                        detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                    WHERE eventDetailId = 19
                    """,
                    (img_data, message, title, position, name, contact)
                )
            else:
                db.execute(
                    """
                    UPDATE EventDetails
                    SET detailDescription = JSON_SET(detailDescription, '$.message', %s),
                        detailDescription = JSON_SET(detailDescription, '$.title', %s),
                        detailDescription = JSON_SET(detailDescription, '$.position', %s),
                        detailDescription = JSON_SET(detailDescription, '$.name', %s),
                        detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                    WHERE eventDetailId = 19
                    """,
                    (message, title, position, name, contact)
                )

            mysql.connection.commit()

            title2 = request.form.get('desc6')
            position2 = request.form.get('desc7')
            name2 = request.form.get('desc8')
            contact2 = request.form.get('desc9')
            img_file2 = request.files.get('profile2')

            if img_file2:
                img_data = img_file2.read()
                db.execute(
                    """
                    UPDATE EventDetails
                    SET 
                        detailPicture = %s,
                        detailDescription = JSON_SET(detailDescription, '$.title', %s),
                        detailDescription = JSON_SET(detailDescription, '$.position', %s),
                        detailDescription = JSON_SET(detailDescription, '$.name', %s),
                        detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                    WHERE eventDetailId = 20
                    """,
                    (img_data, title2, position2, name2, contact2)
                )
            else:
                db.execute(
                    """
                    UPDATE EventDetails
                    SET detailDescription = JSON_SET(detailDescription, '$.title', %s),
                        detailDescription = JSON_SET(detailDescription, '$.position', %s),
                        detailDescription = JSON_SET(detailDescription, '$.name', %s),
                        detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                    WHERE eventDetailId = 20
                    """,
                    (title2, position2, name2, contact2)
                )

            mysql.connection.commit()
            flash('Your changes have been saved!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash('Failed to save changes. Please try again.', 'error')

    db.execute("""
        SELECT detailPicture, 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.message')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
        FROM EventDetails
        WHERE eventDetailId = 19 AND detailName = 'Contact Us'
    """)
    contact_data = db.fetchall()

    db.execute("""
        SELECT detailPicture, 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
        FROM EventDetails
        WHERE eventDetailId = 20 AND detailName = 'Contact Us'
    """)
    contact_data2 = db.fetchall()

    contact = None
    contact2 = None

    if contact_data:
       contact = {
            'profile': base64.b64encode(contact_data[0][0]).decode('utf-8') if contact_data[0][0] else None,
            'message': contact_data[0][1],
            'title': contact_data[0][2],
            'position': contact_data[0][3],
            'name': contact_data[0][4],
            'contact': contact_data[0][5],
        }

    if contact_data2:
       contact2 = {
            'profile': base64.b64encode(contact_data2[0][0]).decode('utf-8') if contact_data2[0][0] else None,
            'title': contact_data2[0][1],
            'position': contact_data2[0][2],
            'name': contact_data2[0][3],
            'contact': contact_data2[0][4],
        }
    db.close()
    
    return render_template('Organiser/contact_us.html', contact=contact, contact2=contact2)

if __name__ == '__main__':
    app.run(debug=True)

