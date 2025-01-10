from flask import request, redirect, url_for, render_template, make_response, jsonify, flash
from datetime import datetime
from app import mail  
from flask_mail import Message
from models.register_model import UserModel, PaymentModel

class RegisterController:
    def __init__(self, db):
        self.db = db
        self.user_model = UserModel(db)
        self.payment_model = PaymentModel(db)

    def public_register(self):
        self.db.execute("""
            SELECT sizeName, sizePrice
            FROM tshirt_size
            ORDER BY sizeID;
        """)
        sizes = self.db.fetchall()
        self.db.close()
        return render_template('Public/public_register.html', sizes=sizes)

    def student_register(self):
        self.db.execute("""
            SELECT distinct packageName, price, hasTShirt
            FROM packages 
            WHERE packageStatus = 'active';
        """)
        packages = self.db.fetchall()

        self.db.execute("""
            SELECT sizeName, sizePrice
            FROM tshirt_size
            ORDER BY sizeID;
        """)
        sizes = self.db.fetchall()

        self.db.close()
        return render_template('Public/student_register.html', packages=packages, sizes=sizes)

    def submit_form(self):
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

                user_description = {
                    "matricNumber": matric_number,
                    "package": package,
                    "tShirtSize": t_shirt_size,
                    "campus": campus,
                    "school": school,
                    "transport": transportation
                }

                now = datetime.now()

                user_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'userType': 'student',
                    'userDescription': user_description,
                    'now': now
                }

                if self.user_model.insert_user(user_data):
                    resp = make_response(redirect(url_for('register.payment')))
                    resp.set_cookie('matric_number', matric_number)
                    resp.set_cookie('user_type', 'student')
                    return resp
                else:
                    flash('User registration failed. Please try again.', 'error')
                    return redirect(url_for('register.student_register'))

            except Exception as e:
                print(f"Error in user registration: {e}")
                return "An error occurred. Please try again.", 500

    def submit_form2(self):
        if request.method == 'POST':
            try:
                name = request.form.get('full-name')
                ic_number = request.form.get('ic-passport-number')
                phone = request.form.get('phone-number')
                email = request.form.get('email')
                t_shirt_size = request.form.get('t-shirt-size')

                package = 'Glow-Rious Pro'

                user_description = {
                    "ICNumber": ic_number,
                    "package": package,
                    "tShirtSize": t_shirt_size
                }

                now = datetime.now()

                user_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'userType': 'public',
                    'userDescription': user_description,
                    'now': now
                }

                if self.user_model.insert_user(user_data):
                    resp = make_response(redirect(url_for('register.payment')))
                    resp.set_cookie('ic_number', ic_number)
                    resp.set_cookie('user_type', 'public')
                    return resp

            except Exception as e:
                print(f"Error in user registration: {e}")
                return "An error occurred. Please try again.", 500

    def payment(self):
        try:
            user_type = request.cookies.get('user_type')
            matric = request.cookies.get('matric_number')
            IC = request.cookies.get('ic_number')

            # Retrieve active student and public data
            student_data = self.payment_model.get_active_students(matric)
            public_data = self.payment_model.get_active_public_users(IC)

            # Determine user type and extract data
            number, email, package, t_shirt_size = None, None, None, None
            if user_type == 'public' and public_data:
                number = public_data[0][0]
                package = public_data[0][1]
                t_shirt_size = public_data[0][2]
                email = public_data[0][3]
            elif user_type == 'student' and student_data:
                number = student_data[0][0]
                package = student_data[0][1]
                t_shirt_size = student_data[0][2]
                email = student_data[0][3]

            # Generate order number
            first_six_digits = number[:6] if number and len(number) >= 6 else '000000'
            current_date = datetime.now().strftime('%d%m%y')
            order_number = f"{first_six_digits}{current_date}"

            # Retrieve package and size details
            package_details = self.payment_model.get_package_details(package)
            size_details = self.payment_model.get_tshirt_sizes(t_shirt_size)

            # Calculate total amount
            package_price = int(package_details[0][1]) if package_details else 0
            size_price = int(size_details[0][1]) if size_details else 0
            total_amount = package_price + size_price
        
        except Exception as e:
            print(f"Error in payment processing: {e}")
            flash("An error occurred during payment processing. Please try again.", "error")
            return render_template('Public/homepage.html')

        return render_template('Public/payment.html', package=package, t_shirt_size=t_shirt_size, 
                               package_price=package_price, additional_price=size_price, total_amount=total_amount, 
                               number=number, email=email, order_number=order_number)
    
    def submit_payment(self):
        if request.method == 'POST':
            # Extract data from the request
            number = request.form.get('number')
            total_amount = request.form.get('total_amount')
            uploaded_file = request.files.get('receipt_upload')
            email = request.form.get('email')
            package = request.form.get('package')
            t_shirt_size = request.form.get('t_shirt_size')
            package_price = request.form.get('package_price')
            additional_price = request.form.get('additional_price')
            order_number = request.form.get('order_number')

            # Prepare the email content
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

            # Send email confirmation
            try:
                msg = Message(subject, sender='tankaixin02@gmail.com', recipients=[email])
                msg.html = message_body
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email: {e}")
                return redirect(request.url)

            # Save payment information to the database
            if uploaded_file and uploaded_file.filename:
                try:
                    # Read the file content and filename
                    file_content = uploaded_file.read()
                    file_name = uploaded_file.filename

                    # Save payment to the database using the model function
                    self.payment_model.save_payment(order_number, number, total_amount, file_content, file_name)

                    return jsonify({"success": True}), 200
                except Exception as e:
                    print(f"Error saving payment: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500
            else:
                return jsonify({"success": False, "error": "No file uploaded"}), 400
        