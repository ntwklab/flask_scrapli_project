from website import app
from flask import render_template

"""
Before first run...

will need to use this also...
export FLASK_APP=app.py #Mac
set FLASK_APP=app.py or $env:FLASK_APP = "app" #Windows
flask db init 
flask db migrate -m "new tables"
flask db upgrade
!!!Run this script, go to browser...!!!

"""

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
    