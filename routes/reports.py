from flask import Blueprint, jsonify, request
from db import query, execute
from flask_jwt_extended import jwt_required

reports_bp = Blueprint('reports', __name__)

# GET all active emergency reports (uses your existing view)
@reports_bp.route('/api/reports', methods=['GET'])
@jwt_required()
def get_reports():
    rows = query("SELECT * FROM vw_ActiveEmergencyReports")
    return jsonify(rows)

# GET single report
@reports_bp.route('/api/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    rows = query("SELECT * FROM EmergencyReport WHERE ReportID = ?", (report_id,))
    return jsonify(rows[0] if rows else {})

# POST create new report
@reports_bp.route('/api/reports', methods=['POST'])
@jwt_required()
def create_report():
    data = request.json
    execute("""
        INSERT INTO EmergencyReport 
        (Location, DisasterType, SeverityLevel, CitizenName, CitizenContact, EventID)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data['location'], data['disaster_type'], data['severity'],
          data.get('citizen_name'), data.get('citizen_contact'), data.get('event_id')))
    return jsonify({"message": "Report created"}), 201

# PATCH update report status
@reports_bp.route('/api/reports/<int:report_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(report_id):
    status = request.json.get('status')
    execute("UPDATE EmergencyReport SET Status = ? WHERE ReportID = ?", (status, report_id))
    return jsonify({"message": "Status updated"})