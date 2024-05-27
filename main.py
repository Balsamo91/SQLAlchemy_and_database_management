from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# request is used for html form to get teh IDs and do somnehting with it

app = Flask(__name__)
# Configuration for our database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# Creation of SQLAlchemy object. We are passing the Flask 'app' object here
db = SQLAlchemy(app)

# Creating a table the db.Model have always to be there ******
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.String(10), nullable=False)

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', list_students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Getting data from form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthdate = request.form['birthdate']

        # Adding data to database

        # Creating new Row before sending it to database, inside Student() the first parameter is called from db.Model above and next is the same in the request method under add_student
        new_student = Student(first_name=first_name, last_name=last_name, birthdate=birthdate)

        # Adding new_student to session
        db.session.add(new_student)

        # Submitting the sesstion to database (Saving to db)
        db.session.commit()

        # redirecting
        return redirect(url_for('index'))


    return render_template('add_student.html')



# If database file does not exist it will create it 
with app.app_context():
    db.create_all()

app.run(debug=True)