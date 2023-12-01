import pika
import json
import time


# Assume game data is stored in a list for simplicity
def send_games_data(channel, client_queue):
    games_data = [
        {
            "HomeTeamName": "Team A",
            "AwayTeamName": "Team B",
            "HomeTeamManagerEmail": "managerA@example.com",
            "AwayTeamManagerEmail": "managerB@example.com",
            "RefereeEmails": ["referee1@example.com", "referee2@example.com"],
            "GameLocation": "Stadium X",
            "GameTime": "14:00",
            "GameDate": "12/25/2023"
        },
        {
            "HomeTeamName": "Team C",
            "AwayTeamName": "Team D",
            "HomeTeamManagerEmail": "managerC@example.com",
            "AwayTeamManagerEmail": "managerD@example.com",
            "RefereeEmails": ["referee3@example.com", "referee4@example.com"],
            "GameLocation": "Stadium Y",
            "GameTime": "19:00",
            "GameDate": "12/25/2023"
        }
        # Add more game data as needed
    ]
    data_msg = {"type": "games_data", "data": games_data}
    channel.basic_publish(
        exchange="", routing_key=client_queue, body=json.dumps(data_msg)
    )
    print("Sent games_data to client.")


def callback(ch, method, properties, body):
    client_queue = properties.reply_to
    try:
        ready_message = body.decode()
        if ready_message == "Ready for Data":
            send_games_data(ch, client_queue)

    except Exception as e:
        print("Error:", e)


# Set up RabbitMQ connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

# Set up server queue
server_queue = "server_queue"
channel.queue_declare(queue=server_queue)

# Set up server to consume messages
channel.basic_consume(queue=server_queue, on_message_callback=callback, auto_ack=True)

print("Server waiting for messages...")

# Start consuming messages
channel.start_consuming()
