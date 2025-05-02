from flask import Flask
from routes.routes import main
import os

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROCESSED_FOLDER = os.path.join('static', 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Register blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
