from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://equipmentlist_user:722hxcFW75kDE9jT90Runx9w2Yez1wFW'
    '@dpg-ctfkb5bgbbvc73den670-a:5432/equipmentlist'
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
def home():
    return "Welcome to Equipment Management System"

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
@app.before_first_request
def create_tables():
    db.create_all()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
