from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

from routes.auth      import auth_bp
from routes.reports   import reports_bp
from routes.teams     import teams_bp
from routes.inventory import inventory_bp
from routes.finance   import finance_bp
from routes.hospitals import hospitals_bp
from routes.approvals import approvals_bp
from routes.audit     import audit_bp

load_dotenv()

app = Flask(__name__, static_folder='static')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

CORS(app)
JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(finance_bp)
app.register_blueprint(hospitals_bp)
app.register_blueprint(approvals_bp)
app.register_blueprint(audit_bp)

with app.app_context():
    from db import get_connection, release_connection
    for _ in range(3):
        try:
            conn = get_connection()
            release_connection(conn)
            print("DB connection pool warmed up.")
        except Exception as e:
            print(f"Pool warm-up failed: {e}")

@app.route('/')
def home():
    return send_from_directory('static', 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/test/finance')
def test_finance():
    from db import query
    try:
        rows = query("SELECT TOP 5 * FROM Donation")
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)