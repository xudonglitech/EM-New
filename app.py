from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import qrcode
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://equipmentlist_user:722hxcFW7kDE9J90Runx9w2Yez1wFW@dpg-ctfkb5bgbbvc73den670-a/equipmentlist'
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

# Route to fetch all data
@app.route('/all_data', methods=['GET'])
def get_all_data():
    equipment_list = Equipment.query.all()
    data = [{
        'id': eq.id,
        'equipment_id': eq.equipment_id,
        'project_number': eq.project_number,
        'last_maintenance': eq.last_maintenance,
        'max_flow': eq.max_flow,
        'comments': eq.comments,
        'action': eq.action
    } for eq in equipment_list]
    return jsonify(data)

# Route to generate QR code for an equipment
@app.route('/generate_qrcode/<equipment_id>', methods=['GET'])
def generate_qrcode(equipment_id):
    try:
        # Generate a URL pointing to the equipment details page
        equipment_url = f"https://em-5qm1.onrender.com/equipment/{equipment_id}"
        qr_img = qrcode.make(equipment_url)
        
        # Save QR code to an in-memory buffer
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(buffer, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display equipment details dynamically
@app.route('/equipment/<equipment_id>', methods=['GET'])
def equipment_details(equipment_id):
    try:
        # Query for equipment by ID
        equipment = Equipment.query.filter_by(equipment_id=equipment_id).first()
        if not equipment:
            return "<h1>404 - Equipment Not Found</h1>", 404

        # Display equipment details as HTML
        details = f"""
        <h1>Equipment Details</h1>
        <ul>
            <li><strong>Equipment ID:</strong> {equipment.equipment_id}</li>
            <li><strong>Project Number:</strong> {equipment.project_number}</li>
            <li><strong>Last Maintenance:</strong> {equipment.last_maintenance}</li>
            <li><strong>Max Flow:</strong> {equipment.max_flow}</li>
            <li><strong>Comments:</strong> {equipment.comments}</li>
            <li><strong>Action:</strong> {equipment.action}</li>
        </ul>
        """
        return details
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

if __name__ == '__main__':
    app.run(debug=True)
