from core.node import Node

class Router(Node):
    def __init__(self, name):
        super().__init__(name)
        self.routing_table = []
    
    def add_route(self, route):
        self.routing_table.append(route)