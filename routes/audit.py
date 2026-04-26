from flask import Blueprint, jsonify
from db import query
from flask_jwt_extended import jwt_required

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/audit', methods=['GET'])
@jwt_required()
def get_audit():
    try:
        rows = query("""
            SELECT TOP 100 * FROM vw_AuditTrailSummary
            ORDER BY LogTimestamp DESC
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500