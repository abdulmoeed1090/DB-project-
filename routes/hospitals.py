from flask import Blueprint, jsonify, request
from db import query, execute
from flask_jwt_extended import jwt_required

hospitals_bp = Blueprint('hospitals', __name__)

@hospitals_bp.route('/api/hospitals', methods=['GET'])
@jwt_required()
def get_hospitals():
    try:
        rows = query("""
            SELECT h.HospitalID, h.HospitalName, h.Location,
                   h.TotalBeds, h.AvailableBeds, h.ContactNumber,
                   COUNT(p.PatientID) AS ActivePatients,
                   SUM(CASE WHEN p.IsCritical=1 THEN 1 ELSE 0 END) AS CriticalPatients
            FROM Hospital h
            LEFT JOIN Patient p ON h.HospitalID = p.HospitalID
                AND p.Status NOT IN ('Discharged','Deceased')
            GROUP BY h.HospitalID, h.HospitalName, h.Location,
                     h.TotalBeds, h.AvailableBeds, h.ContactNumber
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hospitals_bp.route('/api/hospitals/patients', methods=['GET'])
@jwt_required()
def get_patients():
    try:
        rows = query("""
            SELECT p.PatientID, p.PatientName, p.AdmittedAt,
                   p.Status, p.IsCritical,
                   h.HospitalName
            FROM Patient p
            JOIN Hospital h ON p.HospitalID = h.HospitalID
            ORDER BY p.AdmittedAt DESC
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hospitals_bp.route('/api/hospitals/patients', methods=['POST'])
@jwt_required()
def admit_patient():
    try:
        data = request.json
        execute("""
            INSERT INTO Patient
            (PatientName, HospitalID, ReportID, Status, IsCritical)
            VALUES (?, ?, ?, 'Admitted', ?)
        """, (data['patient_name'], data['hospital_id'],
              data.get('report_id'), data.get('is_critical', 0)))
        return jsonify({"message": "Patient admitted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500