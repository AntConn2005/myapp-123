class DisruptionSimulator:
    """
    Simulates real-world logistics disruptions by dynamically altering graph weights.
    """
    def __init__(self, network_manager):
        self.network_manager = network_manager

    def apply_scenario(self, scenario_name: str):
        """Applies a specific disruption scenario to the network graph."""
        self.network_manager.reset_to_base()
        G = self.network_manager.current_graph

        if scenario_name == "Normal Operations":
            return # Base state

        elif scenario_name == "Northeast Blizzard":
            # Severe weather hits JFK and ORD. High time delays, higher risk, reduced capacity.
            for u, v, data in G.edges(data=True):
                if u in ['JFK', 'ORD'] or v in ['JFK', 'ORD']:
                    data['current_time'] *= 3.0      # 3x time delay
                    data['current_risk'] = min(100, data['current_risk'] + 60) # High risk
                    data['current_capacity'] *= 0.3  # 70% drop in capacity
                    data['status'] = 'Disrupted (Weather)'
                    G.nodes[u]['status'] = 'Impacted'
                    G.nodes[v]['status'] = 'Impacted'

        elif scenario_name == "LAX Labor Strike":
            # Ground crew strike at LAX. Extremely high cost to operate, massive time delays.
            for u, v, data in G.edges(data=True):
                if u == 'LAX' or v == 'LAX':
                    data['current_cost'] *= 4.0      # 4x cost due to premium labor
                    data['current_time'] *= 5.0      # Massive backlog
                    data['current_capacity'] *= 0.1  # Operating at 10% capacity
                    data['status'] = 'Disrupted (Strike)'
            G.nodes['LAX']['status'] = 'Severe Disruption'

        elif scenario_name == "MEM Super-Hub Failure":
            # Core routing hub goes offline (e.g., severe power grid failure).
            # Edges into/out of MEM drop to 0 capacity.
            for u, v, data in G.edges(data=True):
                if u == 'MEM' or v == 'MEM':
                    data['current_capacity'] = 0     # Closed
                    data['status'] = 'Closed'
            G.nodes['MEM']['status'] = 'Offline'