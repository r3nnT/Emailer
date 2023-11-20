import pika
import ssl, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# RabbitMQ configuration
rabbitmq_host = 'localhost'  # Change this to your RabbitMQ server's hostname or IP address
queue_name = 'hello'

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 465  # Change this to the appropriate port for your SMTP server
smtp_username = 'jjelway24@gmail.com'
smtp_password = 'ofze kube zxbr mmib'
sender_email = 'jjelway24@gmail.com'
recipient_email = 'tyler_renn@yahoo.com'


def send_email(subject, body):
    #  Set up the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()

    # Connect to the SMTP server and send the email
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, message.as_string())


def callback(ch, method, properties, body):
    message = body.decode('utf-8')
    print(f"Received message: {message}")

    if "send" in message:
        subject = input('SUBJECT: ')
        body = input("MESSAGE: ")

        send_email(subject, body)
        print("Email sent!")


# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=queue_name)

# Set up the callback function for handling messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Waiting for messages. To exit, press Ctrl+C")
channel.start_consuming()