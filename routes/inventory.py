from flask import Blueprint, jsonify, request
from db import query, execute
from flask_jwt_extended import jwt_required

inventory_bp = Blueprint('inventory', __name__)

# GET all warehouse stock summary
@inventory_bp.route('/api/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    rows = query("SELECT * FROM vw_WarehouseStockSummary")
    return jsonify(rows)

# GET low stock alerts only
@inventory_bp.route('/api/inventory/alerts', methods=['GET'])
@jwt_required()
def get_low_stock():
    rows = query("""
        SELECT * FROM vw_WarehouseStockSummary
        WHERE StockStatus != 'Sufficient'
    """)
    return jsonify(rows)

# GET inventory for a specific warehouse
@inventory_bp.route('/api/inventory/<int:warehouse_id>', methods=['GET'])
@jwt_required()
def get_warehouse_inventory(warehouse_id):
    rows = query("""
        SELECT * FROM vw_WarehouseStockSummary
        WHERE WarehouseLocation = (
            SELECT Location FROM Warehouse WHERE WarehouseID = ?
        )
    """, (warehouse_id,))
    return jsonify(rows)

# PATCH update stock quantity
@inventory_bp.route('/api/inventory/<int:inventory_id>', methods=['PATCH'])
@jwt_required()
def update_stock(inventory_id):
    data = request.json
    execute("""
        UPDATE WarehouseInventory
        SET Quantity = ?, LastUpdated = GETDATE()
        WHERE InventoryID = ?
    """, (data['quantity'], inventory_id))
    return jsonify({"message": "Stock updated successfully"})