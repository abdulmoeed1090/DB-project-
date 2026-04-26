from flask import Blueprint, jsonify, request
from db import query, call_sp
from flask_jwt_extended import jwt_required

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/api/teams', methods=['GET'])
@jwt_required()
def get_teams():
    rows = query("SELECT * FROM vw_RescueTeamStatus")
    return jsonify(rows)

# Calls sp_AssignTeamToReport directly
@teams_bp.route('/api/teams/assign', methods=['POST'])
@jwt_required()
def assign_team():
    data = request.json
    call_sp("sp_AssignTeamToReport", (data['team_id'], data['report_id']))
    return jsonify({"message": "Team assigned successfully"})