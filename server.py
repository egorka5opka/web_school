from flask import render_template, Flask, redirect


app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Deskmate')

@app.route('/creators')
def creators():
    return render_template('creators.html', title='Deskmate')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')