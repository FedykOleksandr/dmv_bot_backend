from flask import Flask
from flask_migrate import Migrate
from models import db, Appointment
from routes import init_routes
from flask_cors import CORS
from flask_apscheduler import APScheduler
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os

app = Flask(__name__)
app.run(port=5000)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:reallyStrongPwd123@localhost/dmvbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# scheduler = APScheduler()
# scheduler.init_app(app)

migrate = Migrate(app, db)
init_routes(app)
CORS(app)


def get_dmv_branches():
    url = 'https://www.dmv.ca.gov/portal/wp-json/dmv/v1/field-offices'
    response = requests.get(url)
    if response.status_code == 200:
        branches = response.json()
        return branches
    else:
        return []



def gmail_authenticate():
    creds = None
    token_file = 'token.json'
    credentials_file = 'credentials.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, 'https://www.googleapis.com/auth/gmail.send')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file,
                                                             'https://www.googleapis.com/auth/gmail.send')
            creds = flow.run_local_server(port=5000)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def send_email(service, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['from'] = 'fedyk.common@gmail.com'
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}
    service.users().messages().send(userId='me', body=message_body).execute()


def get_available_dates(branch_id):
    url = f"https://www.dmv.ca.gov/portal/wp-json/dmv/v1/appointment/branches/{branch_id}/dates?services[]=DT!1857a62125c4425a24d85aceac6726cb8df3687d47b03b692e27bd8d17814&numberOfCustomers=1&ver=650499006111.7792"
    response = requests.get(url)
    if response.status_code == 200:
        dates = response.json()
        print("Available dates for branch_id" + branch_id)
        print(dates)
        return [date.split('T')[0] for date in dates]
    else:
        return []


gmail_service = gmail_authenticate()


def scheduled_task():
    with app.app_context():
        unique_branch_ids = {appointment.branch_id for appointment in Appointment.query.filter_by(is_notificated=False).all()}

        dates_by_branch = {}
        for branch_id in unique_branch_ids:
            dates_by_branch[branch_id] = get_available_dates(branch_id)

        for appointment in Appointment.query.filter_by(is_notificated=False).all():
            if str(appointment.date) in dates_by_branch.get(appointment.branch_id, []):
                send_email(gmail_service, appointment.email, "Доступна нова дата для запису", f"Доступні дати: {appointment.date}")
                appointment.is_notificated = True
                db.session.commit()


# scheduler.add_job(id='CheckAppointments', func=scheduled_task, trigger='interval', minutes=0.5)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # scheduler.start()
    app.run()
