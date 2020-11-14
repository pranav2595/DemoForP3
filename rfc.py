class RFCNode:
    def __init__(self, rfcNumber, rfcTitle, peerHostname):
        self.rfcNumber = rfcNumber
        self.rfcTitle = rfcTitle
        self.peerHostname = peerHostname
        self.next = None


class RFCList:
    def __init__(self):
        self.head = None

    def isPresentInList(self, rfcNumber, rfcTitle, peerHostname):
        temp = self.head
        while temp:
            if temp.rfcNumber == rfcNumber and temp.rfcTitle == rfcTitle and temp.peerHostname == peerHostname:
                return True
            temp = temp.next
        return False

    def addRFC(self, rfcNumber, rfcTitle, peerHostname):
        if self.isPresentInList(rfcNumber, rfcTitle, peerHostname):
            print("Duplicate RFC Entry")
            return False
        newRFC = RFCNode(rfcNumber, rfcTitle, peerHostname)
        newRFC.next = self.head
        self.head = newRFC
        return True

    def listAll(self):
        temp = self.head
        res = []
        while temp:
            res.append({"rfcNumber": str(temp.rfcNumber), "rfcTitle": temp.rfcTitle, "peerHostname": temp.peerHostname})
            temp = temp.next
        return res

    def deleteRFC(self, peerHostname):
        if self.head is None:
            print("RFC list is empty.")
            return

        temp = self.head
        if temp.peerHostname == peerHostname:
            self.head = temp.next
            return True

        prev = None
        while temp and temp.peerHostname != peerHostname:
            prev = temp
            temp = temp.next

        if temp is None:
            return False

        prev.next = temp.next
        return True

    def lookup(self, rfc_number):
        if self.head is None:
            print("RFC list is empty.")
            return []

        res = []
        temp = self.head
        while temp:
            if temp.rfcNumber == rfc_number:
                res.append({'rfcNumber': temp.rfcNumber, 'rfcTitle': temp.rfcTitle, 'peerHostname': temp.peerHostname})
            temp = temp.next
        return res