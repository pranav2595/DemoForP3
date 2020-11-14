import socket
import _thread
import os
from datetime import datetime
from pytz.reference import LocalTimezone
from platform import platform
from random import randint


class Client:
    def __init__(self):
        self.serverIP = socket.gethostbyname('G7')
        self.serverPort = 7734
        self.clientSocket = socket.socket()
        self.uploadServerPort = 1024 + randint(1, 48000)
        self.clientHostName = socket.gethostname() + "@" + str(randint(1, 1000))
        self.uploadServerSocket = socket.socket()
        self.uploadServerSocket.bind(('', self.uploadServerPort))
        self.isConnected = False

    def startConnectionToServer(self):
        self.clientSocket.connect((self.serverIP, self.serverPort))
        _request = "Host: " + self.clientHostName + \
                   "\nPort: " + str(self.uploadServerPort)
        self.clientSocket.send(_request.encode())
        response = self.clientSocket.recv(4096).decode()
        return response

    def getP2P(self, req):
        res = self.sendRequest(req)
        print('\033[91m' + res + '\033[0m')
        data = res.split('\n')
        if not res or len(data) <= 1:
            return
        rfc = [x.strip() for x in data[1].split()]
        rfcNumber = rfc[0]
        rfcTitle = rfc[1]
        peerHostname = rfc[2].split('@')[0].strip()
        peerPortNumber = int(rfc[3])
        receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        receiveSocket.connect((peerHostname, peerPortNumber))
        receiveSocket.send(rfcTitle.encode())
        metaData = receiveSocket.recv(4096).decode()
        if metaData in  ['P2P-CI/1.0 404 Not Found', 'P2P-CI/1.0 400 Bad Request']:
            print(metaData)
            return

        f = open(rfcTitle + ".txt", 'w')
        receivedData = receiveSocket.recv(4096).decode()
        while receivedData:
            f.write(receivedData)
            receivedData = receiveSocket.recv(4096).decode()
        f.close()
        print('RFC downloaded')
        addRequest = ['ADD RFC ' + rfcNumber + ' P2P-CI/1.0', 'Host: ' + self.clientHostName,
                      'Port: ' + str(self.uploadServerPort), 'Title: ' + rfcTitle]
        addRequest = "\n".join(addRequest)
        response = self.sendRequest(addRequest)
        print('\033[91m' + response + '\033[0m')
        receiveSocket.close()

    def uploadServerProcess(self):
        self.uploadServerSocket.listen(5)
        while True:
            c, address = self.uploadServerSocket.accept()
            rfcTitle = c.recv(4096).decode().strip()
            if rfcTitle:
                try:
                    stats = os.stat(rfcTitle + '.txt')
                    lastModified = datetime.fromtimestamp(stats.st_mtime).strftime('%a, %d %b %Y %H:%M:%S %Z')
                    reply = ["P2P-CI/1.0 200 OK"]
                    reply.append(
                        "Date:" + datetime.now().strftime('%a,%d %b %Y %H:%M:%S') + " " + LocalTimezone().tzname(
                            datetime.now()))
                    reply.append("OS:" + platform())
                    reply.append("Last-Modified:" + lastModified + " " + LocalTimezone().tzname(datetime.now()))
                    reply.append("Content-Length:" + str(stats.st_size))
                    reply.append("Content-Type:text/text")
                    c.send("\n".join(reply).encode())

                    with open(rfcTitle + ".txt") as file:
                        for line in file:
                            c.send(line.encode())
                    c.close()
                except:
                    return "P2P-CI/1.0 400 Bad Request"

    def sendRequest(self, _request):
        self.clientSocket.send(_request.encode())
        response = self.clientSocket.recv(4096).decode()
        return response


if __name__ == '__main__':
    client = Client()
    while True:
        response = ''
        if not client.isConnected:
            option = input('Connect to Server, (y/n)? ')
            if option == 'y' and not client.isConnected:
                _thread.start_new_thread(client.uploadServerProcess, ())
                response = client.startConnectionToServer()
                client.isConnected = True
        else:
            option = input(
                "Hello, You are now connected to the server.\n" +
                "List of methods available:\n" +
                "1. ADD: Add an RFC in the peer to peer network\n" +
                "2. LOOKUP: Find peers that have a specified RFC.\n" +
                "3. LIST: List all RFCs available in the network.\n" +
                "4. GET: Download an RFC from a peer in network.\n" +
                "5. EXIT: End peer connection\n" +
                "Select option - 1, 2, 3, 4 or 5\n")

            option = int(option)
            _request = []
            if option == 1:
                rfc_no, rfc_title = input("Enter RFC number: "), input("Enter RFC title: ")
                _request = ['ADD RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + client.clientHostName,
                            'Port: ' + str(client.uploadServerPort), 'Title: ' + rfc_title]
            elif option == 2:
                rfc_no, rfc_title = input("Enter RFC number: "), input("Enter RFC title: ")
                _request = ['LOOKUP RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + client.clientHostName,
                            'Port: ' + str(client.uploadServerPort), 'Title: ' + rfc_title]
            elif option == 3:
                _request = ['LIST ALL P2P-CI/1.0', 'Host: ' + client.clientHostName,
                            'Port: ' + str(client.uploadServerPort)]
            elif option == 4:
                rfc_no = input("Enter RFC number: ")
                _request = ['LOOKUP RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + client.clientHostName,
                            'OS: ' + platform()]
                _thread.start_new_thread(client.getP2P, ("\n".join(_request),))
            elif option == 5:
                _request = ['EXIT RFC 123 P2P-CI/1.0', 'Host: ' + client.clientHostName,
                            'Port: ' + str(client.uploadServerPort)]

            if len(_request) > 0 and option != 4:
                response = client.sendRequest("\n".join(_request))
            if option == 5:
                print('\033[91m' + response + '\033[0m')
                client.clientSocket.close()
                break
        print('\033[91m' + response + '\033[0m')
