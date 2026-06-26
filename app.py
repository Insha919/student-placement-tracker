
from flask import Flask, render_template, request, session, redirect, url_for
from flask import redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "placementtracker123"

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

        query = "SELECT * FROM students WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and user[3] == password:
            session['student_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Email or Password"
        
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))

  
    student_id = session['student_id']
    
    cursor.execute(
        "SELECT branch, cgpa FROM students WHERE student_id = %s", 
        (student_id,)
    )
    student = cursor.fetchone()
    branch = student[0]
    cgpa = student[1]

    cursor.execute(
        "SELECT COUNT(*) FROM companies"
    )
    total_companies = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE student_id = %s",
        (student_id,)
    )
    applied_companies = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM companies WHERE allowed_branch = %s AND minimum_cgpa <= %s",
        (branch, cgpa)
    )
    eligible_companies = cursor.fetchone()[0]


    if total_companies > 0:
       progress = int((applied_companies / total_companies) * 100)
    else:
       progress = 0

    return render_template(
        'dashboard.html',
        total_companies=total_companies,
        applied_companies=applied_companies,
        eligible_companies=eligible_companies,
        progress=progress
    )



@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        branch = request.form['branch']
        cgpa = request.form['cgpa']

       
        hashed_password = generate_password_hash(password)

        query = '''
        INSERT INTO students (name, email, password, branch, cgpa)
        VALUES (%s, %s, %s, %s, %s)
        '''

        
        values = (name, email, hashed_password, branch, cgpa)

      
        cursor.execute(query, values)
        db.commit()

        return "Registration Successful"

   
    return render_template('register.html')


@app.route('/companies')
def companies():

    cursor.execute("SELECT * FROM companies")

    company_list = cursor.fetchall()

    return render_template(
        'companies.html',
        companies=company_list
    )


@app.route('/eligible_companies')
def eligible_companies():

    student_id = session['student_id']

    query = '''

    SELECT branch, cgpa

    FROM students

    WHERE student_id=%s

    '''

    cursor.execute(query, (student_id,))

    student = cursor.fetchone()

    branch = student[0]

    cgpa = student[1]

    query2 = '''

    SELECT *

    FROM companies

    WHERE allowed_branch=%s

    AND minimum_cgpa<=%s

    '''

    cursor.execute(query2, (branch, cgpa))

    eligible = cursor.fetchall()

    return render_template(
        'eligible_companies.html',
        companies=eligible
    )

@app.route('/apply/<int:company_id>')
def apply(company_id):

    student_id = session['student_id']

    check_query = '''

    SELECT *

    FROM applications

    WHERE student_id=%s

    AND company_id=%s

    '''

    cursor.execute(
        check_query,
        (student_id, company_id)
    )

    existing = cursor.fetchone()

    if existing:

        return "You have already applied."

    query = '''

    INSERT INTO applications

    (student_id, company_id, status)

    VALUES(%s,%s,%s)

    '''

    values = (
        student_id,
        company_id,
        "Applied"
    )

    cursor.execute(query, values)

    db.commit()

    return "Application Submitted Successfully"

@app.route('/my_applications')
def my_applications():

    student_id = session['student_id']

    query = '''

    SELECT companies.company_name,
           companies.package,
           applications.status

    FROM applications

    JOIN companies

    ON applications.company_id = companies.company_id

    WHERE applications.student_id = %s

    '''

    cursor.execute(query, (student_id,))

    applications = cursor.fetchall()

    return render_template(
        'my_applications.html',
        applications=applications
    )

@app.route('/logout')
def logout():

    session.clear()

    return render_template('login.html')


@app.route('/admin', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        query = '''

        SELECT *

        FROM admin

        WHERE username=%s

        AND password=%s

        '''

        cursor.execute(
            query,
            (username,password)
        )

        admin = cursor.fetchone()

        if admin:

            return render_template(
                'admin_dashboard.html'
            )

        else:

            return "Invalid Admin Credentials"

    return render_template(
        'admin_login.html'
    )


@app.route('/all_applications')
def all_applications():

    query = '''

    SELECT students.name,
       companies.company_name,
       applications.status,
       applications.application_id

    FROM applications

    JOIN students

    ON applications.student_id =
       students.student_id

    JOIN companies

    ON applications.company_id =
       companies.company_id

    '''

    cursor.execute(query)

    applications = cursor.fetchall()

    return render_template(
        'all_applications.html',
        applications=applications
    )

@app.route('/select/<int:application_id>')
def select_application(application_id):

    query = '''

    UPDATE applications

    SET status='Selected'

    WHERE application_id=%s

    '''

    cursor.execute(query,(application_id,))

    db.commit()

    return "Application Selected"

@app.route('/reject/<int:application_id>')
def reject_application(application_id):

    query = '''

    UPDATE applications

    SET status='Rejected'

    WHERE application_id=%s

    '''

    cursor.execute(query,(application_id,))

    db.commit()

    return "Application Rejected"


@app.route('/profile')
def profile():

    student_id = session['student_id']

    query = '''

    SELECT *

    FROM students

    WHERE student_id=%s

    '''

    cursor.execute(query,(student_id,))

    student = cursor.fetchone()

    return render_template(
        'profile.html',
        student=student
    )

@app.route('/company/<int:company_id>')
def company_details(company_id):

    cursor.execute(
        "SELECT * FROM companies WHERE company_id=%s",
        (company_id,)
    )

    company = cursor.fetchone()

    return render_template(
        'company_details.html',
        company=company
    )



if __name__ == '__main__':
    app.run(debug=True)