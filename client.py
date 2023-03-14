import os
from socket import *
import pickle
import sys
from hashlib import sha256
import struct
import base64

# Set up server address and port#

multicastGroup = ("235.1.1.1", 55555)

# Create a UDP socket

clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)

# set a timeout wait time for 5 seconds

clientSocket.settimeout(5)

# Set a ttl so that it can't leave the network/computer

ttl = struct.pack('b', 32)

clientSocket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)

requestNumber = 0


def takePicture(destination, nameID, requestNumber, portNumber):

    # increase the request number

    requestNumber += 1
            # saves the image as a jpg file

            #encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

            #result, imgencode = cv2.imencode('.jpg', frame, encode_param)

    data = array(imgencode)

    # Send request to server

    pictureSocket = socket()

    pictureSocket.connect(('localhost', portNumber))

    stringData = base64.b64encode(data)

    length = str(len(stringData))

    pictureSocket.sendall(length.encode('utf-8').ljust(64))

    pictureSocket.sendall(stringData)

    pictureSocket.close()

    try:

        lookingForMessage = True

        while lookingForMessage:

            # Obtain the return message

            response, server = clientSocket.recvfrom(2048)

            # convert the message to a useable format

            response = pickle.loads(response)

            # Check if it is for the most recent request

            if str(response[0]) == str(requestNumber):

                # get rid of the request number as it does not need to be printed

                response.pop(0)

                # Stop looking for correct message, stops while loop from going through another cycle

                lookingForMessage = False

                if str(response[0]) == "picture failed":

                    #print("Face not detected, try again")

                    takePicture(server, nameID, requestNumber, response[-1])

                else:

                    # Say what server provided the information

                    print("From Server: " + str(response[-1]))

    except socket.timeout:

        # notify there was a failure

        print(" Request time out\n")


def handleRequest(request, nameID, requestNumber):

    nameID = sha256(str(nameID).lower().encode('utf-8')).hexdigest()

    # increase the request number

    requestNumber += 1

    sendingMessage = [str(requestNumber), request, nameID]

    # Send request to server

    sent = clientSocket.sendto(pickle.dumps(sendingMessage), multicastGroup)

    try:

        lookingForMessage = True

        while lookingForMessage:

            # Obtain the return message

            returnMessage, server = clientSocket.recvfrom(2048)

            # convert the message to a useable format

            response = pickle.loads(returnMessage)

            # Check if it is for the most recent request

            if response[0] == str(requestNumber):

                # get rid of the request number as it does not need to be printed

                response.pop(0)

                # Stop looking for correct message, stops while loop from going through another cycle

                lookingForMessage = False

                if str(response[-2]) == "picture":

                    takePicture(server, nameID, requestNumber, response[-1])

                else:

                    # Say what server said

                    print("From Server: " + str(response[-1]))

    except socket.timeout:

        # notify there was a failure

        print(" Request time out\n")