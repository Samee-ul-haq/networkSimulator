"""
Network Layer — RIP v1 (Routing Information Protocol, RFC 1058).

Algorithm : Distance-Vector (Bellman-Ford).
Metric     : Hop count (1–15 reachable; 16 = infinity / unreachable).
Operation  : Each router advertises its routing table to its directly
             connected neighbours.  Neighbours update their tables if
             the new path has a lower metric.  Repeated until stable.
"""

from network.routing_table import Route


INFINITY = 16


class RIP:
    def __init__(self, router):
        self.router    = router
        self.neighbors = []   # list of dicts: {router, interface, next_hop_ip}

    # ── Neighbour management ──────────────────────────────────────────── #

    def add_neighbor(self, neighbor_router, local_interface: str, next_hop_ip: str):
        """
        Register a directly connected neighbouring router.
          local_interface : name of the interface on THIS router facing the neighbour
          next_hop_ip     : IP of the neighbour's interface on the shared link
        """
        self.neighbors.append({
            "router"    : neighbor_router,
            "interface" : local_interface,
            "next_hop"  : next_hop_ip,
        })
        print(f"[RIP] {self.router.name}: neighbour {neighbor_router.name} "
              f"via {local_interface} (next-hop {next_hop_ip})")

    # ── Advertisement ─────────────────────────────────────────────────── #

    def advertise(self) -> list:
        """Return this router's routes as a list of Route objects."""
        return list(self.router.routing_table.routes)

    # ── Update processing (Bellman-Ford) ──────────────────────────────── #

    def process_update(self, advertisements: list, neighbor_info: dict) -> bool:
        updated      = False
        next_hop_ip  = neighbor_info["next_hop"]
        out_iface    = neighbor_info["interface"]

        for adv in advertisements:
            new_metric = adv.metric + 1
            if new_metric >= INFINITY:
                continue

            existing = None
            for r in self.router.routing_table.routes:
                if r.network == adv.network and r.mask == adv.mask:
                    existing = r
                    break

            if existing is None:
                print(f"[RIP] {self.router.name}: NEW route "
                      f"{adv.network}/{adv.mask} via {next_hop_ip} "
                      f"metric {new_metric}")
                self.router.routing_table.add_route(Route(
                    network   = adv.network,
                    mask      = adv.mask,
                    next_hop  = next_hop_ip,
                    interface = out_iface,
                    metric    = new_metric,
                ))
                updated = True

            elif new_metric < existing.metric:
                print(f"[RIP] {self.router.name}: BETTER route "
                      f"{adv.network}/{adv.mask} via {next_hop_ip} "
                      f"metric {new_metric} (was {existing.metric})")
                self.router.routing_table.add_route(Route(
                    network   = adv.network,
                    mask      = adv.mask,
                    next_hop  = next_hop_ip,
                    interface = out_iface,
                    metric    = new_metric,
                ))
                updated = True

        return updated

    # ── One update cycle ──────────────────────────────────────────────── #

    def run_cycle(self) -> bool:
        changed = False
        for nbr in self.neighbors:
            ads = nbr["router"].rip.advertise()
            if self.process_update(ads, nbr):
                changed = True
        return changed

    # ── Convergence ───────────────────────────────────────────────────── #

    @staticmethod
    def converge(routers: list, max_iterations: int = 15):
        """
        Run RIP update cycles until no routing table changes occur
        (convergence) or max_iterations is reached.
        """
        print("\n" + "=" * 56)
        print("[RIP] Starting convergence …")
        print("=" * 56)

        for iteration in range(1, max_iterations + 1):
            print(f"\n[RIP] ── Iteration {iteration} ──────────────────────")
            any_changed = False
            for router in routers:
                if hasattr(router, "rip") and router.rip.run_cycle():
                    any_changed = True

            if not any_changed:
                print(f"\n[RIP] ✓ Converged after {iteration} iteration(s)")
                break
        else:
            print(f"\n[RIP] ⚠ Did not fully converge in {max_iterations} iterations")

        print("\n[RIP] Final routing tables:")
        for router in routers:
            router.routing_table.show()
