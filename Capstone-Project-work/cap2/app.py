import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from equipment import load_equipment_data, save_equipment_data, initial_data

app = Flask(__name__)
app.secret_key = '!@#$%^&*(jhdshgsd'  # Required for flash messages

'''
HOSTNAME = os.environ.get('HOSTNAME')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
'''
mydb= mysql.connector.connect(
    host="127.0.0.1",
    database="user",  # Use your database name
    user="root",                 # Use your database username
    password='',
    port=3306
    )


def table_check(fname, lname, studentid, equip, status):
    try:
        # Establishing a database connection
        cursor = mydb.cursor()

        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS accounts (
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            student_id INT(11) NOT NULL,
            equipment VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (student_id)
        );
        """
        cursor.execute(create_table_query)
        mydb.commit()

         # Check if the student already has a record with the given status
        select_query = """
        SELECT status FROM accounts WHERE student_id = %s;
        """
        cursor.execute(select_query, (studentid,))
        result = cursor.fetchone()  # Fetch one result

        if result:
            current_status = result[0]

            # If the current status is 'check-out', update to 'check-in'
            if current_status == 'check-out':
                update_query = """
                UPDATE accounts SET status = 'check-in' , timestamp = CURRENT_TIMESTAMP WHERE student_id = %s;
                """
                cursor.execute(update_query, (studentid,))
                mydb.commit()
                print("Status updated to check-in successfully!")
            #if the current status is 'check-in', insert into the table new record of user to checkout new equipment
            elif current_status == 'check-in':
                update_query = """
                UPDATE accounts 
                SET status = 'check-out', equipment = %s, timestamp = CURRENT_TIMESTAMP 
                WHERE student_id = %s;
                """
                cursor.execute(update_query, (equip, studentid))
                mydb.commit()
                print("Data inserted successfully!")

        else:
            # Insert data from the form if no existing record is found
            insert_query = """
            INSERT INTO accounts (first_name, last_name, student_id, equipment, status)
            VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (fname, lname, studentid, equip, status))
            mydb.commit()
            print("Data inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()





def validate_login(username, password):
    try:
        # Establishing a database connection
        cursor = mydb.cursor()
        # Example query to validate login (modify as needed)
        cursor.execute("SELECT * FROM Employees WHERE username = %s AND password = %s", (username, password))
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

@app.route('/equipment')
def equipment():
    try:
        # Create the cursor object
        page = int(request.args.get('page', 1))  # Get current page number from query parameters
        per_page = 20
        conn = mydb.cursor()

        # Define the query
        total_query = 'SELECT COUNT(*) FROM accounts'
        #query = 'SELECT first_name, last_name, student_id, equipment, status, timestamp FROM accounts'
        
        # Execute the query
        #conn.execute(query)
        conn.execute(total_query)
        total_rows = conn.fetchone()[0]
        
        # Fetch all rows from the executed query
        #rows = conn.fetchall()  
        start = (page - 1) * per_page
        end = start + per_page
        total_pages = (total_rows + per_page - 1) // per_page

        query = 'SELECT first_name, last_name, student_id, equipment, status, timestamp FROM accounts LIMIT %s OFFSET %s'
        conn.execute(query, (per_page, start))
        rows = conn.fetchall()


    # Pass the result to the template


    except mysql.connector.Error as err:
        # Log the error and show an error page or message
        print(f"Database error: {err}")
    finally:
        # Always close the cursor/connection if it was opened
        if conn:
            conn.close()

    # Pass the result to the template
    #return render_template('equipment.html', rows=rows)

    return render_template('equipment.html', rows=rows, page=page, total_pages=total_pages)



@app.route('/equipments')
def equipments():
    # Load initial equipment data
    equipment_data = load_equipment_data()

    # If no data is loaded (e.g., file not found), initialize with initial_data
    if not equipment_data:
        equipment_data = initial_data
        save_equipment_data(equipment_data)
    return render_template('equipments.html', equipment_data=equipment_data)

@app.route('/update_availability', methods=['POST'])
def update_availability():
    item_id = int(request.form['item_id'])
    availability = request.form['availability']

    # Load existing data
    equipment_data = load_equipment_data()

    # Update the item's availability
    for item in equipment_data:
        if item['id'] == item_id:
            if availability == "available":
                item['available'] = True
            else:  
                item['available'] = False
            break
    # Save the updated data
    save_equipment_data(equipment_data)

    return redirect(url_for('equipments'))



@app.route('/checkinout', methods=['GET', 'POST'])
def checkinout():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        studentid = request.form['studentid']
        equipment = request.form['equipment']
        status = request.form['status']

        table_check(fname, lname, studentid, equipment, status)
    
    return render_template('checkinout.html')


# Route for Tournament Schedule page
@app.route('/tournament')
def tournament():
    return render_template('tournament.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8082",debug=True)
