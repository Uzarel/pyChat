import atexit
import socket
import threading

def connectionThread(sock):
    # Accepts a connection request and stores both a socket object and its IP address
    while True:
        try:
            client, address = sock.accept()
        except:
            print("Something went wrong while accepting incoming connections!")
            break
        print("{} has connected.".format(address[0]))
        addresses[client] = address
        threading.Thread(target=clientThread, args=(client,)).start()

def clientThread(client):
    # Handles the client
    address = addresses[client][0]
    try:
        user = getNickname(client)
    except:
        print("Something went wrong while setting the nickname for {}!".format(address))
        del addresses[client]
        client.close()
        return
    print("{} set its nickname to {}!".format(address, user))
    users[client] = user
    try:
        client.send("Hi {}! You are now connected to pyChat. Type \"/help\" for a list of available commands!".format(user).encode("utf8"))
    except:
        print("Communication error with {} ({}).".format(address, user))
        del addresses[client]
        del users[client]
        client.close()
        return
    broadcast("{} has joined the chat room!".format(user))

    # Handles specific messages in a different way (user commands)
    while True:
        try:
            message = client.recv(2048).decode("utf8")
            if message == "/quit":
                client.send("You left the chat!".encode("utf8"))
                del addresses[client]
                del users[client]
                client.close()
                print("{} ({}) has left.".format(address, user))
                broadcast("{} has left the chat.".format(user))
                break
            elif message == "/online":
                onlineUsers = ', '.join([user for user in sorted(users.values())])
                client.send("Users online are: {}".format(onlineUsers).encode("utf8"))
            elif message == "/help":
                client.send("Available commands are /help, /online and /quit".encode("utf8"))
            else:
                print("{} ({}): {}".format(address, user, message))
                broadcast(message, user)
        except:
            print("{} ({}) has left.".format(address, user))
            del addresses[client]
            del users[client]
            client.close()
            broadcast("{} has left the chat.".format(user))
            break

def getNickname(client):
    # Gets a nickname for a client (if it is not already taken)
    client.send("Welcome to pyChat! Please type your nickname:".encode("utf8"))
    nickname = client.recv(2048).decode("utf8")
    alreadyTaken = False
    if nickname in users.values():
        alreadyTaken = True
        while alreadyTaken:
            client.send("This nickname has already been taken. Please choose a different one:".encode("utf8"))
            nickname = client.recv(2048).decode("utf8")
            if nickname not in users.values():
                alreadyTaken = False
    return nickname

def broadcast(message, sentBy = ""):
    # Broadcasts a message to all users connected
    try:
        if sentBy == "":
            for user in users:
                user.send(message.encode("utf8"))
        else:
            for user in users:
                user.send("{}: {}".format(sentBy, message).encode("utf8"))
    except:
        print("Something went wrong while broadcasting a message!")

def cleanup():
    # Closes all socket object connections
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
    print("Cleanup done.")

def main():
    # Register cleanup() as the function to be executed at termination
    atexit.register(cleanup)
    # The host and port for the chat service
    host = ""
    port = 25000
    # Creates the socket for a TCP application
    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    serverSocket = socket.socket(socketFamily, socketType)
    # Binds the serverSocket at the specified port number
    serverSocket.bind((host, port))
    # Enables accepting connections
    serverSocket.listen()
    # Welcome message to the server owner
    print("pyChat server is up and running!")
    print("Listening for new connections on port {}.".format(port))

    # Creates a thread for accepting incoming connections
    connThread = threading.Thread(target=connectionThread, args=(serverSocket,))
    connThread.start()
    # Waits for it to end
    connThread.join()
    # Performs socket connections cleanup
    cleanup()
    # Closes the server socket object connection
    serverSocket.close()
    print("Server has shut down.")

# Dictionaries of nicknames and addresses with socket object as key
users = {}
addresses = {}

if __name__ == "__main__":
    main()
    pass