from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///equipment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(50), nullable=False, unique=True)  # Unique constraint for Equipment ID
    project_number = db.Column(db.String(50), nullable=True)
    last_maintenance = db.Column(db.String(50), nullable=False)
    max_flow = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(200), nullable=False)
    action = db.Column(db.String(50), nullable=False)

# Ensure database is created within the application context
with app.app_context():
    db.create_all()
    print(f"Database location: {os.path.abspath('equipment.db')}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_equipment', methods=['GET'])
def get_equipment():
    equipment = Equipment.query.all()
    return jsonify([{
        'equipmentID': eq.equipment_id,
        'projectNumber': eq.project_number,
        'lastMaintenance': eq.last_maintenance,
        'maxFlow': eq.max_flow,
        'comments': eq.comments,
        'action': eq.action
    } for eq in equipment])

@app.route('/add_equipment', methods=['POST'])
def add_equipment():
    data = request.json
    try:
        new_equipment = Equipment(
            equipment_id=data['equipmentID'],
            project_number=data.get('projectNumber', ''),
            last_maintenance=data['lastMaintenance'],
            max_flow=data['maxFlow'],
            comments=data['comments'],
            action=data['action']
        )
        db.session.add(new_equipment)
        db.session.commit()
        return jsonify({'message': 'Equipment added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': f'Equipment ID "{data["equipmentID"]}" already exists.'}), 400
        return jsonify({'error': 'Failed to add equipment'}), 500

@app.route('/update_equipment', methods=['PUT'])
def update_equipment():
    data = request.get_json()
    try:
        equipment = Equipment.query.filter_by(equipment_id=data['equipmentID']).first()
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404

        equipment.project_number = data.get('projectNumber', equipment.project_number)
        equipment.last_maintenance = data.get('lastMaintenance', equipment.last_maintenance)
        equipment.max_flow = data.get('maxFlow', equipment.max_flow)
        equipment.comments = data.get('comments', equipment.comments)
        equipment.action = data.get('action', equipment.action)

        db.session.commit()
        return jsonify({'message': 'Equipment updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update equipment'}), 500

@app.route('/delete_equipment/<equipmentID>', methods=['DELETE'])
def delete_equipment(equipmentID):
    try:
        equipment = Equipment.query.filter_by(equipment_id=equipmentID).first()
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404

        db.session.delete(equipment)
        db.session.commit()
        return jsonify({'message': 'Equipment deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete equipment'}), 500

if __name__ == '__main__':
    app.run(debug=True)
