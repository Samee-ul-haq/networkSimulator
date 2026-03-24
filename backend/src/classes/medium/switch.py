from collections import deque
class Switch:
    def __init__(self,ports):
        self.dict={}
        self.macTable={}
        self.free_ports=deque(range(ports))
        self.transmitters=set()

        for port in range(0,ports):
            self.dict[port]=None

    def connect(self,device):
        if not self.free_ports:
            return None
        else:
            free_port=self.free_ports.popleft()
            self.dict[free_port]=device
            return free_port

    def disconnect(self,port):
        if(port!=None):
            self.free_ports.append(port)
            self.dict[port]=None
    
    def is_busy(self):
        return len(self.transmitters)>0

    def collision(self):
        return len(self.transmitters)>1
    
    # def transmit(self,senderPort,frame):
    #     reciever=frame["dest_mac"]
    #     if(self.macTable[reciever]!=None):
    #         flag=False
    #         while(not(flag)):
    #             flag=self.macTable[reciever].recieve(frame)
    #     else:
    #         flag=False
    #         while(not(flag)):
    #             for port in self.dict:
    #                 if(port!=senderPort):
    #                     flag=self.dict[port].recieve(frame)
    #                     if(flag):
    #                         self.macTable[reciever]=self.dict[port]
    #                         break
