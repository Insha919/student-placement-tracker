from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="alina",
    database="placement_tracker"
)

cursor = db.cursor()

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        query = '''

        SELECT * FROM students

        WHERE email=%s AND password=%s

        '''

        values = (email,password)

        cursor.execute(query, values)

        user = cursor.fetchone()

        if user:

            return "Login Successful"

        else:

            return "Invalid Email or Password"
        
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        branch = request.form['branch']
        cgpa = request.form['cgpa']

        query = '''
        INSERT INTO students
        (name,email,password,branch,cgpa)

        VALUES(%s,%s,%s,%s,%s)
        '''

        values = (name, email, password, branch, cgpa)

        cursor.execute(query, values)

        db.commit()

        return "Registration Successful"

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)