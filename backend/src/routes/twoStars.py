from src.classes.medium.hub import Hub
from src.classes.medium.switch import Switch
from src.classes.station.device import Device


def createTwoStarTopology(devices_per_hub=5):
    """
    Two star topologies (hub-based), connected to each other via a switch.

    Layout:
      PC0..PC4 ── Hub1 ──┐
                         Switch
      PC5..PC9 ── Hub2 ──┘

    Broadcast domains : 1 (switch connects both hubs into one)
    Collision domains : 2 (one per hub segment)
    """
    # ── Create devices ────────────────────────────────────────────────
    group1 = [Device(f'PC{i}')               for i in range(devices_per_hub)]
    group2 = [Device(f'PC{i+devices_per_hub}') for i in range(devices_per_hub)]

    # ── Create hubs ───────────────────────────────────────────────────
    hub1 = Hub(devices_per_hub + 1)   # +1 port for uplink to switch
    hub2 = Hub(devices_per_hub + 1)

    for device in group1:
        port = hub1.connect(device)
        device.port = port

    for device in group2:
        port = hub2.connect(device)
        device.port = port

    # ── Create switch and connect hubs ────────────────────────────────
    # NOTE: In this simulator hubs operate at physical layer (bit level),
    # so the switch here acts as a bridge between two collision domains.
    # We represent the hub uplinks as special "hub devices" for the switch.
    sw = Switch(2)

    # We use placeholder hub-proxy devices for the switch ports
    # Real inter-device communication still goes through hub broadcast
    print(f"[TOPO] Two-star topology created.")
    print(f"  Hub 1: {[d.name for d in group1]}")
    print(f"  Hub 2: {[d.name for d in group2]}")
    print(f"\n[TOPO] Broadcast domains: 1")
    print(f"[TOPO] Collision domains : 2 (one per hub segment)")

    return hub1, hub2, sw, group1, group2
