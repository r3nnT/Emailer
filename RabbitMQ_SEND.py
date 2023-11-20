import pika


def send():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Queue to which the message will be delivered
    channel.queue_declare(queue='hello')

    # Exchange in where the queue flows to
    message_send = input("Input 'SEND' to send an email: ")
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=message_send.lower())

    print('sent message!')
    connection.close()


send()
