import sys
import time
import socket
import colorama
import datetime
import threading

def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M:%S")
    return formattedTime

def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

def send(sock):
    while True:
        try:
            message = input()
            deleteLastLine()
            sock.send(message.encode("utf8"))
        except:
            print("An error occured while trying to send a message!")
            break

def receive(sock, buffer = 1024):
    while True:
        try:
            message = sock.recv(buffer).decode()
            if message:
                print("[{}] {}".format(currentTime(), message))
            else:
                # When connection errors occur, messages are empty
                break
        except:
            print("An error occured while trying to reach the server!")
            break


# Colorama handles the ANSI escape codes to work on every platform
colorama.init()

host = "localhost"
port = 25000
bufferSize = 2048
socketFamily = socket.AF_INET
socketType = socket.SOCK_STREAM
clientSocket = socket.socket(socketFamily, socketType)
clientSocket.connect((host, port))
sendingThread = threading.Thread(target=send, args=(clientSocket,))
receivingThread = threading.Thread(target=receive, args=(clientSocket, bufferSize))
receivingThread.start()
sendingThread.start()
while receivingThread.is_alive() and sendingThread.is_alive():
    time.sleep(1)
clientSocket.close()
print("\nYou can now close the application.")