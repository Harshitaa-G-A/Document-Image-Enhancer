from flask import Flask, render_template, request, send_from_directory,jsonify,send_file,session, redirect, url_for
import os
import subprocess
import datetime
from PIL import Image, ImageDraw, ImageFont
import pyrebase 
import requests
from firebase_admin import credentials,firestore,initialize_app,storage
import cv2
import pytesseract
from docx import Document
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText  # Add this import statement
from email import encoders

current_direct=os.path.dirname(os.path.abspath(__file__))
path_to_cred=os.path.join(current_direct,"serviceAccountKey.json")

app = Flask(__name__)
CERTIFICATE_TEMPLATE_PATH = 'certific.jpg'
cred=credentials.Certificate(path_to_cred)
initialize_app(cred)
firebaseConfig={
    'apiKey': "AIzaSyCmMhNroXfoai26mw5WN1uz9-P6q1TVppc",
    'authDomain': "document-image-enhancer.firebaseapp.com",
    'projectId': "document-image-enhancer",
    'storageBucket': "document-image-enhancer.appspot.com",
    'messagingSenderId': "515716475868",
    'appId': "1:515716475868:web:51b8560f3647f2fc30bd19",
    'measurementId': "G-N7H2WRD7SP",
    'databaseURL': ""
}
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()
db=firestore.client()
app.secret_key = 'secret'
@app.route('/')
def index():
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png')]
    converted_files=[f for f in os.listdir('./result') if f.endswith('.txt')]
    message = request.args.get('message')
    # Check if the user is logged in
    if 'user_id' in session:
        # User is logged in, render the home page with logged-in user information
        return render_template('index.html', extracted_files=extracted_files,converted_files=converted_files, enhanced_files=enhanced_files, message=message, logged_in=True)
    else:
        # User is not logged in, render the home page without logged-in user information
        return render_template('index.html', extracted_files=extracted_files,converted_files=converted_files, enhanced_files=enhanced_files, message=message, logged_in=False)
@app.route('/logout')
def logout():
    # Remove the user_id from the session if it exists
    session.pop('user_id', None)
    # Redirect to the home page with a logout message
    return redirect('/')
@app.route('/login', methods=['POST'])
def login():
    email = request.form['login-email']
    password = request.form['login-password']
    try:
        users = auth.sign_in_with_email_and_password(email, password)
        # Check the structure of the user object
        print(users)
        # Assuming user['idToken'] contains the user ID
        user_id = users.get('idToken')
        session['user_id'] = user_id
        return redirect('/')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['signup-email']
    password = request.form['signup-password']
    try:
        users = auth.create_user_with_email_and_password(email, password)
        # Check the structure of the user object
        print(users)
        # Assuming user['idToken'] contains the user ID
        user_id = users.get('idToken')
        session['user_id'] = user_id
        return redirect('/')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/overwrite-file', methods=['POST'])
def overwrite_file():
    # Assuming you want to do something with the decrypted text
    decrypted_text = request.json.get('decryptedText')
    # Process the decrypted text as needed
    # For now, let's just print it
    print("Decrypted Text:", decrypted_text)
    # Return a response
    return jsonify({'message': 'File overwritten successfully'})
@app.route('/generate-certificate', methods=['POST'])
def generate_certificate():
    name = request.form['name'].upper()  # Capitalize the entire name
    year = request.form['year']
    department = request.form['department']
    place = request.form['place']
    incharge = request.form['incharge']
    college = request.form['college']
    event_name = request.form['event_name']
    
    # Load the certificate template image
    certificate_template_path = 'Certificate.png'  # Adjust the path to your certificate template image
    certificate_template = Image.open(certificate_template_path)
    
    # Define the font and size for the text
    title_font = ImageFont.truetype("arial.ttf", 70)
    text_font = ImageFont.truetype("arial.ttf", 54)
    small_text_font = ImageFont.truetype("arial.ttf", 40)  # Define font for smaller text
    
    # Create a drawing context
    draw = ImageDraw.Draw(certificate_template)
    
    # Define text content
    certificate_title = f"{name}"
    certificate_content_1 = f"of {college}, {year} {department},"
    certificate_content_2 = f"for winning the {place} place in {event_name}"
    certificate_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Calculate text size and position for title
    title_width, title_height = draw.textsize(certificate_title, font=title_font)
    title_x = (certificate_template.width - title_width) // 2
    title_y = 600
    
    # Calculate text size and position for content 1
    content1_width, content1_height = draw.textsize(certificate_content_1, font=text_font)
    content1_x = (certificate_template.width - content1_width) // 2
    content1_y = title_y + title_height + 50  # Increase the gap between title and content1
    
    # Calculate text size and position for content 2
    content2_width, content2_height = draw.textsize(certificate_content_2, font=text_font)
    content2_x = (certificate_template.width - content2_width) // 2
    content2_y = content1_y + content1_height + 20  # Increase the gap between content1 and content2
    incharge_width, incharge_height = draw.textsize(incharge, font=small_text_font)  # Use small font for incharge
    incharge_x = certificate_template.width - incharge_width - 1400  # Right end of the certificate
    incharge_y = 1000# Below the date
    
    # Calculate text size and position for date
    date_width, date_height = draw.textsize(certificate_date, font=small_text_font)  # Use small font for date
    date_x = certificate_template.width - date_width - 550  # Right end of the certificate
    date_y =  1000   # Adjust vertically
    
    # Calculate text size and position for incharge
    
    # Add text to the certificate
    draw.text((title_x, title_y), certificate_title, fill=(0, 0, 0), font=title_font)
    draw.text((content1_x, content1_y), certificate_content_1, fill=(0, 0, 0), font=text_font)
    draw.text((content2_x, content2_y), certificate_content_2, fill=(0, 0, 0), font=text_font)
    draw.text((incharge_x, incharge_y), f"{incharge}", fill=(0, 0, 0), font=small_text_font)
    draw.text((date_x, date_y), f"{certificate_date}", fill=(0, 0, 0), font=small_text_font)
    
    # Save the generated certificate
    output_directory = './templates'
    certificate_filename = f'{name.replace(" ", "_")}_{event_name.replace(" ", "_")}_certificate.png'
    certificate_path = os.path.join(output_directory, certificate_filename)
    certificate_template.save(certificate_path)
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png') or f.endswith('.docx')]
    # Return the saved certificate image
    return send_file(certificate_path, mimetype='image/png')

@app.route('/binarize', methods=['POST'])
def binarize():
    image_file = request.files['image']
    image_filename = image_file.filename
    image_path = os.path.join('./images', image_filename)
    image_file.save(image_path)
    output_directory = './results'
    subprocess.run(['python', 'enhance.py', 'binarize', image_path, output_directory])    
    # Get the resulting image filename
    result_image_filename = os.path.splitext(image_filename)[0] + '.png'
    result_image_path = os.path.join(output_directory, result_image_filename)
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png')]
    converted_files=[f for f in os.listdir('./result') if f.endswith('.txt')]
    if 'user_id' in session:
        # User is logged in
        return render_template('index.html', result_image=result_image_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=True)
    else:
        # User is not logged in
        return render_template('index.html', result_image=result_image_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=False)


@app.route('/deblur', methods=['POST'])
def deblur():
    image_file = request.files['image']
    image_filename = image_file.filename
    image_path = os.path.join('./images', image_filename)
    image_file.save(image_path)
    output_directory = './results'
    subprocess.run(['python', 'enhance.py', 'deblur', image_path, output_directory])
    
    # Get the resulting image filename
    result_image_filename = os.path.splitext(image_filename)[0] + '.png'
    result_image_path = os.path.join(output_directory, result_image_filename)
    
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png')]
    converted_files=[f for f in os.listdir('./result') if f.endswith('.txt')]
    if 'user_id' in session:
        # User is logged in
        return render_template('index.html', result_image=result_image_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=True)
    else:
        # User is not logged in
        return render_template('index.html', result_image=result_image_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=False)



@app.route('/remove-watermark', methods=['POST'])
def remove_watermark():
    image_file = request.files['image']
    image_filename = image_file.filename
    image_path = os.path.join('./images', image_filename)
    image_file.save(image_path)
    output_directory = './results'
    subprocess.run(['python', 'enhance.py', 'unwatermark', image_path, output_directory])
    
    # Get the resulting image filename
    result_image_filename = os.path.splitext(image_filename)[0] + '.png'
    result_image_path = os.path.join(output_directory, result_image_filename)
    
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png')]
    converted_files=[f for f in os.listdir('./result') if f.endswith('.txt')]
    if 'user_id' in session:
        # User is logged in
        return render_template('index.html', result_image=result_image_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=True)
    else:
        # User is not logged in
        return render_template('index.html', result_image=result_image_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=False)

 
    
@app.route('/extracttext', methods=['POST'])
def extract_text():
    image_file = request.files['image']
    image_filename = image_file.filename
    image_path = os.path.join('./images', image_filename)
    image_file.save(image_path)
    output_directory = './results'
    subprocess.run(['python', 'enhance.py', 'extracttext', image_path, output_directory])
    
    # Get the resulting text file filename
    result_text_filename = os.path.splitext(image_filename)[0] + '.txt'
    result_text_path = os.path.join(output_directory, result_text_filename)
    
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png')]
    converted_files=[f for f in os.listdir('./result') if f.endswith('.txt')]
    if 'user_id' in session:
        # User is logged in
        return render_template('index.html', result_image=result_text_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=True)
    else:
        # User is not logged in
        return render_template('index.html', result_image=result_text_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=False)

@app.route('/handwritten', methods=['POST'])
def handwritten():
    # Get the input image file
    image_file = request.files['image']
    image_filename = image_file.filename
    image_path = os.path.join('./images', image_filename)
    image_file.save(image_path)
    
    # Recognize handwriting and save the text to a text file
    recognized_text = recognize_handwriting(image_path)
    text_filename = os.path.splitext(image_filename)[0] + '.txt'
    text_path = os.path.join('./result', text_filename)
    with open(text_path, 'w') as text_file:
        text_file.write(recognized_text)
    
    # Convert the text file to a Word document
    docx_filename = os.path.splitext(image_filename)[0] + '.docx'
    docx_path = os.path.join('./results', docx_filename)
    convert_to_docx(text_path, docx_path)
    extracted_files = [f for f in os.listdir('./results') if f.endswith('.txt')]
    enhanced_files = [f for f in os.listdir('./results') if f.endswith('.png')]
    converted_files=[f for f in os.listdir('./result') if f.endswith('.txt')]
    if 'user_id' in session:
        # User is logged in
        return render_template('index.html', result_image=docx_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=True)
    else:
        # User is not logged in
        return render_template('index.html', result_image=docx_filename,converted_files=converted_files, extracted_files=extracted_files, enhanced_files=enhanced_files, logged_in=False)

def convert_to_docx(input_text_path, output_docx_path):
    # Open the text file and read its content
    with open(input_text_path, 'r') as file:
        text_content = file.read()

    # Create a new Word document
    doc = Document()
    
    # Add the content of the text file to the Word document
    doc.add_paragraph(text_content)
    
    # Save the Word document
    doc.save(output_docx_path)

    print("Conversion complete.")

# Preprocess the handwritten document image
def preprocess_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding or other preprocessing techniques as needed
    # Example:
    # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return gray

# Perform handwriting recognition
def recognize_handwriting(image_path):
    # Preprocess the image
    processed_image = preprocess_image(image_path)
    
    # Perform OCR using Tesseract
    recognized_text = pytesseract.image_to_string(processed_image)
    
    return recognized_text
@app.route('/send_email', methods=['POST'])
def send_email():
    sender_email = 'idkwhattokeep000@gmail.com'  # Your email address
    sender_password = 'gcqg tmhz soxd pati'  # Your email password

    receiver_email = request.form['receiverEmail']
    subject = request.form['subject']
    message = request.form['message']
    file = request.files['file']

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add message body
    msg.attach(MIMEText(message, 'plain'))

    # Attach file
    attachment = file.read()
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(file.filename))
    msg.attach(part)

    # Connect to SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send email
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

    return redirect('/')
@app.route('/results/<filename>')
def uploaded_file(filename):
    return send_from_directory('./results', filename)
@app.route('/result/<filename>')
def uploaded_file2(filename):
    return send_from_directory('./result', filename)
if __name__ == '__main__':
    app.run(debug=True)