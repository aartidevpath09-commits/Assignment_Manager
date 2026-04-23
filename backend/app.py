from flask import Flask
from flask_cors import CORS

from models import create_tables
from auth import auth_bp
from assignment import assignment_bp
from user import user_bp

import threading
from notifier import start_scheduler

app = Flask(__name__)
CORS(app)

# create tables
create_tables()

# register routes
app.register_blueprint(auth_bp)
app.register_blueprint(assignment_bp)
app.register_blueprint(user_bp)

# start notification thread
threading.Thread(target=start_scheduler, daemon=True).start()

@app.route("/")
def home():
    return {"message": "Backend Running"}

if __name__ == "__main__":
    app.run(debug=True)