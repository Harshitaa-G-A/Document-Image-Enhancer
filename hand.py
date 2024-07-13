import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText  # Add this import statement
from email import encoders


def send_email(sender_email, sender_password, receiver_email, subject, message, file_paths):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add message body
    msg.attach(MIMEText(message, 'plain'))

    # Attach files
    for file_path in file_paths:
        attachment = open(file_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= {}".format(file_path))
        msg.attach(part)

    # Connect to SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send email
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

# Example usage
sender_email = '21z116@psgitech.ac.in'
sender_password = 'h@rshu1411'
receiver_email = 'harshitaa1103@gmail.com'
subject = 'Files for you'
message = 'Please find attached files.'
file_paths = ['C:/Users/91944/Downloads/typed_document.docx']

send_email(sender_email, sender_password, receiver_email, subject, message, file_paths)
