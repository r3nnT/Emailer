import pika
import json
import ssl, smtplib
from email.mime.text import MIMEText


def send_email(recipient, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  # Change this to the appropriate port for your SMTP server
    smtp_password = 'your_sender_password'
    sender_email = 'your_sender_email@example.com'

    #  Set up the MIME
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient

    # Attach the body to the email

    context = ssl.create_default_context()

    # Connect to the SMTP server and send the email
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, recipient, message.as_string())


def callback(ch, method, properties, body):
    # Step 2: Client receives games_data
    games_data_message = json.loads(body)
    print("Received games_data:", games_data_message)
    games_data = games_data_message.get("data", [])

    #  Parses game data to send to Manangers and Refs
    for game in games_data:
        home_team = game.get("HomeTeamName", "")
        away_team = game.get("AwayTeamName", "")
        home_manager_email = game.get("HomeTeamManagerEmail", "")
        away_manager_email = game.get("AwayTeamManagerEmail", "")
        referee_email = game.get("RefereeEmails", "")
        location = game.get("GameLocation", "")
        time = game.get("GameTime", "")
        date = game.get("GameDate", "")
        subject = "Upcoming Game Notification"

        # For Managers
        for email in [game["HomeTeamManagerEmail"],
                     game["AwayTeamManagerEmail"]]:

            body_player = f"You have an upcoming game:" \
                   f"\n\nDate: {date}" \
                   f"\nTime: {time}" \
                   f"\nLocation: {location}" \
                   f"\nHome: {home_team}\nAway: {away_team}"
            send_email(email, subject, body_player)

        #For Refs
        for email in game["RefereeEmails"]:
            body_ref = f"You are scheduled to officiate the following game:" \
                   f"\n\nDate: {date}" \
                   f"\nTime: {time}" \
                   f"\nLocation: {location}" \
                   f"\nHome: {home_team} vs. Away: {away_team}"
            send_email(email, subject, body_ref)

    # Clean up
    connection.close()


# Set up RabbitMQ connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

# Set up client queue
client_queue = "client_queue"
channel.queue_declare(queue=client_queue)

# Set up server queue
server_queue = "server_queue"
channel.queue_declare(queue=server_queue)

# Step 1: Client sends "Ready for Data"
channel.basic_publish(
    exchange="",
    routing_key=server_queue,
    body="Ready for Data",
    properties=pika.BasicProperties(
        reply_to=client_queue,  # Specify the client queue for responses
    ),
)

# Step 1.5: Client waits for a response on its specific queue
channel.basic_consume(queue=client_queue, on_message_callback=callback, auto_ack=True)

# Start consuming messages
channel.start_consuming()
