from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('Public/homepage.html')

@app.route('/Public/route')
def route():
    return render_template('Public/route.html')

@app.route('/Public/public_register')
def route():
    return render_template('Public/public_register.html')

@app.route('/Public/student_register')
def route():
    return render_template('Public/student_register.html')

@app.route('/Public/packages')
def route():
    return render_template('Public/packages.html')

@app.route('/Public/about_us')
def route():
    return render_template('Public/about_us.html')

if __name__ == '__main__':
    app.run(debug=True)

