import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = '!@#$%^&*(jhdshgsd'  # Required for flash messages

mydb= mysql.connector.connect(
    host='localhost',
    database='user',  # Use your database name
    user='root',                 # Use your database username
    password='',
    port=3306
    )


# Sample data
equipment_data = [
    {'name': 'Controller', 'available': True},
    {'name': 'PS4', 'available': False},
    {'name': 'Cue', 'available': True},
    {'name': 'Pool Table', 'available': False},
]


def validate_login(username, password):
    try:
        # Establishing a database connection
        cursor = mydb.cursor()
        # Example query to validate login (modify as needed)
        cursor.execute("SELECT * FROM employees WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate credentials
        if validate_login(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('mainmenu'))  # Redirect to a welcome page or dashboard
        else:
            flash('INVALID USERNAME OR PASSWORD', 'danger')

    return render_template('hello.html')  # Render the HTML template

# Route for main menu
@app.route('/mainmenu')
def mainmenu():
    return render_template('main-menu.html')

# Route for Check In/Out page
@app.route('/checkinout')
def checkinout():
    return render_template('checkinout.html')

# Route for Tournament Schedule page
@app.route('/tournament')
def tournament():
    return render_template('tournament.html')

# Route for Equipment List page
@app.route('/equipment')
def equipment():
    return render_template('equipment.html', equipment_data=equipment_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8081",debug=True)
