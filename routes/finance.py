from flask import Blueprint, jsonify, request
from db import query, execute
from flask_jwt_extended import jwt_required

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/api/finance/summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    try:
        rows = query("""
            SELECT 
                de.EventID,
                de.EventName,
                de.DisasterType,
                ISNULL((SELECT SUM(d.Amount) FROM Donation d 
                        WHERE d.EventID = de.EventID), 0) AS TotalDonationsReceived,
                ISNULL((SELECT SUM(e.Amount) FROM Expense e 
                        WHERE e.EventID = de.EventID), 0) AS TotalExpensesIncurred,
                ISNULL((SELECT SUM(d.Amount) FROM Donation d 
                        WHERE d.EventID = de.EventID), 0) -
                ISNULL((SELECT SUM(e.Amount) FROM Expense e 
                        WHERE e.EventID = de.EventID), 0) AS NetBudgetBalance
            FROM DisasterEvent de
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@finance_bp.route('/api/finance/donations', methods=['GET'])
@jwt_required()
def get_donations():
    try:
        rows = query("""
            SELECT d.DonationID, dn.DonorName, dn.DonorType,
                   d.Amount, d.DonatedAt, de.EventName
            FROM Donation d
            JOIN Donor dn ON d.DonorID = dn.DonorID
            JOIN DisasterEvent de ON d.EventID = de.EventID
            ORDER BY d.DonatedAt DESC
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@finance_bp.route('/api/finance/donors/top', methods=['GET'])
@jwt_required()
def get_top_donors():
    try:
        rows = query("""
            SELECT dn.DonorID, dn.DonorName, dn.DonorType,
                   COUNT(d.DonationID)  AS NumberOfDonations,
                   SUM(d.Amount)        AS TotalContributed
            FROM Donor dn
            JOIN Donation d ON dn.DonorID = d.DonorID
            GROUP BY dn.DonorID, dn.DonorName, dn.DonorType
            ORDER BY TotalContributed DESC
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@finance_bp.route('/api/finance/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    try:
        rows = query("""
            SELECT e.ExpenseID, e.Description, e.Amount,
                   e.Category, e.ExpenseDate, de.EventName
            FROM Expense e
            JOIN DisasterEvent de ON e.EventID = de.EventID
            ORDER BY e.ExpenseDate DESC
        """)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@finance_bp.route('/api/finance/donations', methods=['POST'])
@jwt_required()
def add_donation():
    try:
        data = request.json
        execute("""
            INSERT INTO Donation (DonorID, Amount, EventID, RecordedByUserID)
            VALUES (?, ?, ?, ?)
        """, (data['donor_id'], data['amount'],
              data['event_id'], data['recorded_by']))
        return jsonify({"message": "Donation recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@finance_bp.route('/api/finance/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    try:
        data = request.json
        execute("""
            INSERT INTO Expense
            (Description, Amount, Category, ExpenseDate, EventID, RecordedByUserID)
            VALUES (?, ?, ?, GETDATE(), ?, ?)
        """, (data['description'], data['amount'],
              data['category'], data['event_id'], data['recorded_by']))
        return jsonify({"message": "Expense recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500