class PeerNode:
    def __init__(self, hostName, portNumber):
        self.hostName = hostName
        self.portNumber = portNumber
        self.next = None


class PeerList:
    def __init__(self):
        self.head = None

    def isPresentInList(self, hostName, portNumber):
        temp = self.head
        while temp is not None:
            if temp.hostName == hostName and temp.portNumber == portNumber:
                return True
            temp = temp.next
        return False

    def addPeer(self, hostName, portNumber):
        if self.isPresentInList(hostName, portNumber):
            print("Duplicate Peer Entry")
            return False
        newPeer = PeerNode(hostName, portNumber)
        newPeer.next = self.head
        self.head = newPeer
        return True

    def printList(self):
        cur = self.head
        res = []
        while cur is not None:
            res.append({'hostName': cur.hostName, 'portNumber': str(cur.portNumber)})
            cur = cur.next
        print(res)

    def deletePeer(self, hostName, portNumber):
        if self.head is None:
            print("Peer list is empty.")
            return

        temp = self.head
        if temp.hostName == hostName and temp.portNumber == portNumber:
            self.head = temp.next
            return

        prev = None
        while temp and (temp.hostName != hostName or temp.portNumber != portNumber):
            prev = temp
            temp = temp.next

        if temp is None:
            return

        prev.next = temp.next

    def getPeer(self, hostName, portNumber):
        temp = self.head
        while temp:
            if temp.hostName == hostName and temp.portNumber == portNumber:
                return temp
            temp = temp.next
        print("Peer not found")
        return None

    def getPortNumber(self, hostName):
        temp = self.head
        while temp:
            if temp.hostName == hostName:
                return temp.portNumber
            temp = temp.next
        print("Peer not found with hostname", hostName)
        return None