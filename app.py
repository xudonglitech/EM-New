from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO

app = Flask(__name__)

#________________________
# app.config['SQLALCHEMY_DATABASE_URI'] =(
# 'postgresql://equipmentlist_user:722hxcFW75kDE9jT90Runx9w2Yez1wFW'
 # '@dpg-ctfkb5bgbbvc73den670-a:5432/equipmentlist'
#)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

#________________________ database internally conncet with render , when using render server and storage use this

#________________________ database externally - for using pycharm

#app.config['SQLALCHEMY_DATABASE_URI'] = (
 #   'postgresql://equipmentlist_user:722hxcFW75kDE9jT90Runx9w2Yez1wFW'
 #   '@dpg-ctfkb5bgbbvc73den670-a.oregon-postgres.render.com:5432/equipmentlist'
#)


# 8 - 24 is the old database address

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql://equipmentlist_new_user:"
    "xpaYk8ye8aeznCoCxnxnUWVRymoNadz5"
    "@dpg-ctu6963tq21c73bgdsd0-a.oregon-postgres.render.com/equipmentlist_new"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)


# Equipment model
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(20), unique=True, nullable=False)
    last_maintenance = db.Column(db.String(20))
    max_flow = db.Column(db.String(10))
    project_number = db.Column(db.String(20))
    action = db.Column(db.String(50))
    comments = db.Column(db.String(100))

# Home route
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
    result = [
        {
            'id': equipment.id,
            'equipment_id': equipment.equipment_id,
            'last_maintenance': equipment.last_maintenance,
            'max_flow': equipment.max_flow,
            'project_number': equipment.project_number,
            'action': equipment.action,
            'comments': equipment.comments
        }
        for equipment in equipment_list
    ]
    return jsonify(result)

# Route to generate QR code
@app.route('/generate_qrcode/<equipment_id>')
def generate_qrcode(equipment_id):
    url = f"https://em-5qm1.onrender.com/equipment/{equipment_id}"
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")

# Route to view and edit equipment details
@app.route('/equipment/<equipment_id>', methods=['GET', 'POST'])
def equipment_details(equipment_id):
    equipment = Equipment.query.filter_by(equipment_id=equipment_id).first_or_404()

    if request.method == 'POST':
        # Update the equipment data
        equipment.project_number = request.form.get('project_number', equipment.project_number)
        equipment.last_maintenance = request.form.get('last_maintenance', equipment.last_maintenance)
        equipment.max_flow = request.form.get('max_flow', equipment.max_flow)
        equipment.comments = request.form.get('comments', equipment.comments)
        equipment.action = request.form.get('action', equipment.action)

        db.session.commit()
        return redirect(url_for('equipment_details', equipment_id=equipment_id))

    return render_template('equipment_detail.html', equipment=equipment)

# Initialize database
@app.before_request
def create_tables():
    db.create_all()

# Search Route - 20241220
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    if not query:
        return render_template('search_results.html', results=[], query=query)

    results = Equipment.query.filter(
        (Equipment.equipment_id.ilike(f'%{query}%')) |
        (Equipment.project_number.ilike(f'%{query}%')) |
        (Equipment.comments.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', results=results, query=query)


# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
