from flask import Flask, render_template

# Create Flask app
app = Flask(__name__)

# Sample data
equipment_data = [
    {'name': 'Controller', 'available': True},
    {'name': 'PS4', 'available': False},
    {'name': 'Cue', 'available': True},
    {'name': 'Pool Table', 'available': False},
]

# Route for main menu
@app.route('/')
def main_menu():
    return render_template('main_menu.html')

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
    app.run(debug=True)
