from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('Public/homepage.html')

@app.route('/Public/route')
def route():
    return render_template('Public/route.html')

if __name__ == '__main__':
    app.run(debug=True)

