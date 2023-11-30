from flask import jsonify, request
from models import db, Appointment
import requests


def init_routes(app):
    @app.route('/submit', methods=['POST'])
    def submit_appointment():
        data = request.json
        new_appointment = Appointment(date=data['date'], time=data['time'], email=data['email'], is_notificated=False)
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({"message": "Appointment submitted successfully"}), 200

    @app.route('/api/branches')
    def get_branches():
        url = 'https://www.dmv.ca.gov/portal/wp-json/dmv/v1/field-offices'
        response = requests.get(url)
        if response.status_code == 200:
            branches = response.json()
            return branches
        else:
            return []
