Before first run...

will need to use this also...
export FLASK_APP=app.py #Mac
set FLASK_APP=app.py or $env:FLASK_APP = "app" #Windows
flask db init 
flask db migrate -m "new tables"
flask db upgrade
!!!Run this script, go to browser...!!!
