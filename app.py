import os
import cv2
import numpy as np
import datetime
from flask import Flask, render_template, request, Response, jsonify
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from deepface import DeepFace
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Email Config
SENDER_EMAIL = "chantyanand23@gmail.com"
SENDER_PASSWORD = "iwwnhymabugyopat"  # Use Gmail App Password

def send_email_alert(recipient_email, person_name, matched_img_path):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = f"Match Found for {person_name}"

    body = f"Hello,\n\nA face match has been found for {person_name}. The matched face is attached."
    message.attach(MIMEText(body, "plain"))

    try:
        with open(matched_img_path, 'rb') as f:
            from email.mime.image import MIMEImage
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(matched_img_path))
            message.attach(img)
    except Exception as e:
        print(f"[ERROR] Failed to attach matched image: {e}")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        server.quit()
        print(f"[INFO] Email sent to {recipient_email}")
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")

def extract_frame(video_path, frame_number, save_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_number = min(frame_number, total_frames - 1)

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()

    if success:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, frame)
        print(f"[INFO] Extracted frame saved to {save_path}")
        return True
    else:
        print("[ERROR] Frame extraction failed.")
        return False

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/extract', methods=['POST'])
def extract():
    name = request.form['name']
    email = request.form['email']
    age = int(request.form['age'])

    video = request.files['video']
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.mp4')
    video.save(video_path)

    save_dir = os.path.join('dataset', name)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f'{name}.jpg')

    frame_number = min(max(age, 0), 50)
    success = extract_frame(video_path, frame_number, save_path)

    if success:
        image_path = os.path.join('/dataset', name, f'{name}.jpg')
        return render_template('home.html', image_path=image_path, name=name, email=email)
    else:
        return "Frame extraction failed"

@app.route('/match_face', methods=['POST'])
def match_face():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    name = data['name']
    email = data['email']

    matched_folder = os.path.join('matched', name)
    os.makedirs(matched_folder, exist_ok=True)

    img_bytes = base64.b64decode(image_data)
    temp_img_path = os.path.join('static', 'temp_capture.jpg')
    with open(temp_img_path, 'wb') as f:
        f.write(img_bytes)

    try:
        result = DeepFace.find(
            img_path=temp_img_path,
            db_path=os.path.join('dataset', name),
            enforce_detection=False,
            silent=True
        )

        if len(result) > 0 and len(result[0]) > 0:
            matched_img_path = os.path.join(matched_folder, f'{name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            os.rename(temp_img_path, matched_img_path)
            send_email_alert(email, name, matched_img_path)
            return "Match found. Email sent."
        else:
            return "No match found."
    except Exception as e:
        print(f"[ERROR] Matching failed: {e}")
        return "Error during matching"

if __name__ == '__main__':
    app.run(debug=True)
