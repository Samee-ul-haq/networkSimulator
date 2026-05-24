class ARPTable:

    def __init__(self):
        self.table = {}

    def add_entry(self, ip, mac):
        self.table[ip] = mac

    def resolve(self, ip):
        return self.table.get(ip)

    def show_table(self):
        print("\nARP Table")
        
        for ip, mac in self.table.items():
            print(f"{ip} -> {mac}")