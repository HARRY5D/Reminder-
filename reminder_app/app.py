from flask import Flask, request, render_template, redirect, flash, get_flashed_messages
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT')

@app.route('/')
def index():
    # Read mail history
    mail_history = []
    if os.path.exists(MAIL_HISTORY_FILE):
        with open(MAIL_HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    mail_history.append({
                        'email': parts[0],
                        'message': parts[1],
                        'datetime': parts[2]
                    })
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', mail_history=mail_history, messages=messages)

@app.route('/remind', methods=['POST'])
def remind():
    email = request.form.get('email')
    message = request.form.get('message')
    datetime_val = request.form.get('datetime')

    if not email or not message or not datetime_val:
        flash('All fields are required!', 'error')
        return redirect('/')

    # Compose the email
    subject = f'Reminder for {datetime_val}'
    body = f"Hello,\n\nYou have set a reminder for {datetime_val}:\n\n{message}\n\n--\nReminder App"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
        flash('Reminder email sent successfully!', 'success')
        # Save to mail history
        with open(MAIL_HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}|{message}|{datetime_val}\n")
    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'error')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True) 
