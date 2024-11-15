from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        package = request.form['package-details']
        t_shirt_size = request.form['t-shirt-size']

        return redirect(url_for('payment', package=package, t_shirt_size=t_shirt_size))
    return render_template('Public/student_register.html')

@app.route('/submit-form2', methods=['POST'])
def submit_form2():
    if request.method == 'POST':
        package = 'Glowrious Pro'
        t_shirt_size = request.form['t-shirt-size']

        return redirect(url_for('payment', package=package, t_shirt_size=t_shirt_size))
    return render_template('Public/student_register.html')

@app.route('/Public/payment')
def payment():
    package = request.args.get('package')
    t_shirt_size = request.args.get('t_shirt_size')

    package_price = {
        'Glowrious Pro': 50,
        'Glowrious Lite': 35,
        'Glowrious Starter': 15
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

if __name__ == '__main__':
    app.run(debug=True)

