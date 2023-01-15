import threading
import socket
import json
import pickle
import ssl

host = '127.0.0.1' # localhost
port = 55558

# Create a context using default settings
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load the self-signed CA and private key
context.load_cert_chain("cert.pem", "cert.pem")

# Create standard TCP socket and bind it to localhost on port 55558
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
emails = []

# Getting all the clients and sending message
def broadcast(message):
    for client in clients:
        client.send(message)

# Broadcast Handler
# Each client will have its own thread running and executing the handle function
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode('ascii') == 'LIST':
                index = clients.index(client)
                email = emails[index]
                # De-serializing the data from the client, loop through and check
                # if any of the client's contacts are in the online emails list

                # Function is currently ONE-WAY, meaning if the other contact does
                # not have the client added, it will still list them as a contact on
                # client's end
                data = pickle.loads(client.recv(1024))
                client.send(bytes(f'The following contacts are online: \n'.encode('ascii')))
                for i in data:
                    online_contacts = i["email"]
                    name = i['name']
                    if online_contacts in emails:
                        client.send(bytes(f'* {name}  <{online_contacts}> \n'.encode('ascii')))
                    else:
                        continue
                client.send('stop'.encode('ascii'))
                

            elif message.decode('ascii') == 'EXIT':
                index = clients.index(client) # Remove client from list and terminate connection
                clients.remove(client)
                #client.close()
                email = emails[index]
                #client.send(f'{email} has exited Secure Drop!'.encode('ascii'))
                print(f'User {email} has disconnected from SecureDrop.')
                emails.remove(email)
                print(f'Active connections: {emails}')
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            email = emails[index]
            print(f'User {email} has disconnected from SecureDrop.')
            emails.remove(email)
            break


def receive():

    # Start accepting incoming connections
    while True:
        conn, address = server.accept()
        # Wrap the standard socket with the context, it is now a secure socket connection
        ssl_client = context.wrap_socket(conn, server_side=True)
        print(f'Connection established from {str(address)}')

        ssl_client.send('CONTACT'.encode('ascii'))
        email = ssl_client.recv(1024).decode('ascii')
        emails.append(email)
        clients.append(ssl_client)

        print(f'Username: {email} has securely connected to SecureDrop.')
        print(f'Active connections: {emails}')

        #broadcast(f'{email} has joined Secure Drop!'.encode('ascii'))
        #client.send('Connected to the server'.encode('ascii'))
        #emails_list = print(*emails, sep ="\n")

        # Define and run separate thread for each
        # connection, need to handle them at the same time. 
        thread = threading.Thread(target=handle, args=(ssl_client,))
        thread.start()

print("SecureDrop server running and listening...")
receive()
