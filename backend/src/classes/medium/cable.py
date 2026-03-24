from collections import deque
class Cable:
    def __init__(self):
        self.dict={}
        self.dict[0]=None
        self.dict[1]=None
        self.free_ports=deque(range(2))
        self.transmitters=set()
    
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
    
    def transmit(self,senderPort,bit=None,flag=None,completion=None):
            for port in self.dict:
                if(port!=senderPort):
                    if completion:
                        self.dict[port].recieverSidePhysical.transfer()
                        pass
                    elif flag:
                       self.dict[port].recieverSidePhysical.recieve_bit(bit)
                    else:
                       self.dict[port].recieverSidePhysical.collision_detected()