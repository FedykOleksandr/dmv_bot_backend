from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os

# Функція для входу та отримання сервісу Gmail
def gmail_authenticate():
    creds = None
    # Шлях до файлу токену
    token_file = 'token.json'
    # Шлях до файлу з обліковими даними
    credentials_file = 'credentials.json'

    # Завантаження існуючого токену
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # Якщо немає існуючого токену або він недійсний, авторизуйтеся
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Збереження токену для наступного використання
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


# Функція для створення та відправлення листа
def send_message(service, sender, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    try:
        message = (service.users().messages().send(userId="me", body=body).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print(f'An error occurred: {error}')


SCOPES = ['https://www.googleapis.com/auth/gmail.send']
service = gmail_authenticate()
send_message(service, "fedyk.common@gmail.com", "mrmudik@gmail.com", "Test mail from Python project",
             "Body of the email")
