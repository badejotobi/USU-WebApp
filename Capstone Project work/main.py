# import flast module
from flask import Flask, render_template

# instance of flask application
app = Flask(__name__)

# home route that returns below text when root url is accessed
@app.route("/")
def home():
    return render_template('index.html')

if __name__ == '__main__':  
   app.run()  