from flask import Blueprint, jsonify, request
from db import query, execute
from flask_jwt_extended import jwt_required, get_jwt_identity

approvals_bp = Blueprint('approvals', __name__)

@approvals_bp.route('/api/approvals/pending', methods=['GET'])
@jwt_required()
def get_pending():
    try:
        rows = query("SELECT * FROM vw_PendingApprovals")
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@approvals_bp.route('/api/approvals', methods=['GET'])
@jwt_required()
def get_all():
    try:
        rows = query("""
            SELECT ap.ApprovalID, ap.RequestType, ap.ReferenceID,
                   ap.Status, ap.RequestedAt, ap.ReviewedAt, ap.Remarks,
                   u1.Name AS RequestedByName,
                   u2.Name AS ReviewedByName
            FROM ApprovalRequest ap
            JOIN Users u1 ON ap.RequestedByUserID = u1.UserID
            LEFT JOIN Users u2 ON ap.ReviewedByUserID = u2.UserID
            ORDER BY ap.RequestedAt DESC
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@approvals_bp.route('/api/approvals/<int:approval_id>/approve', methods=['PATCH'])
@jwt_required()
def approve(approval_id):
    try:
        user_id = int(get_jwt_identity())
        execute("""
            UPDATE ApprovalRequest
            SET Status = 'Approved',
                ReviewedByUserID = ?,
                ReviewedAt = GETDATE()
            WHERE ApprovalID = ?
        """, (user_id, approval_id))
        return jsonify({"message": "Approved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@approvals_bp.route('/api/approvals/<int:approval_id>/reject', methods=['PATCH'])
@jwt_required()
def reject(approval_id):
    try:
        user_id = int(get_jwt_identity())
        execute("""
            UPDATE ApprovalRequest
            SET Status = 'Rejected',
                ReviewedByUserID = ?,
                ReviewedAt = GETDATE()
            WHERE ApprovalID = ?
        """, (user_id, approval_id))
        return jsonify({"message": "Rejected successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    