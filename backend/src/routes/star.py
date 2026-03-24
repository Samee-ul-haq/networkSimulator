from src.classes.device import Device
from src.classes.hub import Hub
def createStarTopology():
    devicesList=[]
    for i in range(0,5):
        device=Device('A'+i)
        devicesList.append(device)
    hub=Hub(5)
    
    for device in devicesList:
        port=hub.connect(device)
        device.port=port
        
    print(f"[TOPO] Star topology created: {num_devices} devices connected to hub.")
    for d in devicesList:
        print(f"  {d.name}: mac={d.macAddress}, port={d.port}")

    return hub,devicesList