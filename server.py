import socket
from peer import PeerList
from rfc import RFCList
import _thread
import traceback


def addRFC(req, clientHostname, client_port_no):
    rfcNumber = req[0].strip().split()[2].strip()
    rfcTitle = req[3].strip().split(':')[1].strip()
    rfcList.addRFC(rfcNumber, rfcTitle, clientHostname)
    response = ['P2P-CI/1.0 200 OK', rfcNumber + ' ' + rfcTitle + ' ' + clientHostname + ' ' + client_port_no]
    return "\n".join(response)


def lookupRFC(req):
    rfcNumber = req[0].strip().split()[2].strip()
    peersWithRFC = rfcList.lookup(rfcNumber)

    if len(peersWithRFC) == 0:
        return "P2P-CI/1.0 404 Not Found"
    response = ['P2P-CI/1.0 200 OK']
    for peer in peersWithRFC:
        peerPortNumber = peerList.getPortNumber(peer['peerHostname'])
        response.append(rfcNumber + ' ' + peer['rfcTitle'] + ' ' + peer['peerHostname'] + ' ' + str(peerPortNumber))
    return "\n".join(response)


def listAllRFC():
    allRfcs = rfcList.listAll()
    if len(allRfcs) == 0:
        return "P2P-CI/1.0 404 Not Found"
    response = ['P2P-CI/1.0 200 OK']
    for rfc in allRfcs:
        peerPortNumber = peerList.getPortNumber(rfc['peerHostname'])
        if peerPortNumber:
            response.append(
                rfc['rfcNumber'] + ' ' + rfc['rfcTitle'] + ' ' + rfc['peerHostname'] + ' ' + str(peerPortNumber))
    return "\n".join(response)


def spawnedThread(c):
    c.send("P2P-CI/1.0 200 OK".encode())
    while True:
        req = c.recv(4096).decode()
        try:
            req = req.split('\n')
            method = req[0].strip().split()[0].strip()

            if method == 'LIST':
                version = req[0].strip().split()[2].strip()
            else:
                version = req[0].strip().split()[3].strip()
        except:
            c.send("P2P-CI/1.0 400 Bad Request".encode())
            traceback.print_exc()
            continue

        if version != 'P2P-CI/1.0':
            c.send("505 P2P-CI Version Not Supported".encode())
            continue

        try:
            hostName = req[1].strip().split(':')[1].strip()
            portNumber = req[2].strip().split(':')[1].strip()
        except:
            c.send("P2P-CI/1.0 400 Bad Request".encode())
            continue

        if method == 'ADD':
            try:
                response = addRFC(req, hostName, portNumber)
                c.send(response.encode())
            except:
                c.send("P2P-CI/1.0 400 Bad Request".encode())
        elif method == 'LOOKUP':
            try:
                response = lookupRFC(req)
                c.send(response.encode())
            except:
                c.send("P2P-CI/1.0 400 Bad Request".encode())
        elif method == 'LIST':
            try:
                response = listAllRFC()
                c.send(response.encode())
            except:
                c.send("P2P-CI/1.0 400 Bad Request".encode())
        elif method == 'EXIT':
            peerList.deletePeer(hostName, portNumber)
            while rfcList.deleteRFC(hostName):
                continue
            c.send("P2P-CI/1.0 200 OK".encode())
            c.close()
            print('**********Client thread terminated**********')
            break


if __name__ == '__main__':
    s = socket.socket()
    port = 7734
    s.bind(('', port))
    s.listen(5)
    print("Server started, waiting for connections from Peers!")
    peerList = PeerList()
    rfcList = RFCList()
    while True:
        client, addr = s.accept()
        print('Got connection from', addr)
        _request = client.recv(4096).decode().split('\n')
        client_host_name, client_port_no = _request[0].split(':')[1].strip(), _request[1].split(':')[1].strip()
        peerList.addPeer(client_host_name, client_port_no)
        _thread.start_new_thread(spawnedThread, (client,))
