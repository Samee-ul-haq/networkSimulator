from core.interface import Interface

class Node:
    def __init__(self, name):
        self.name = name
        self.interfaces = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def show_interfaces(self):
        for i in self.interfaces:
            print(f"{i.name} | IP={i.ip} | MAC={i.mac}")