Before first run...

Create the database tables
export FLASK_APP=app.py #Mac
set FLASK_APP=app.py or $env:FLASK_APP = "app" #Windows
flask db init 
flask db migrate -m "new tables"
flask db upgrade
!!!Run this script, go to browser...!!!
