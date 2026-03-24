import networkx as nx
import copy
from typing import Dict, Any

class LogisticsNetwork:
    """
    Represents the core logistics network graph.
    Models Warehouses, Hubs, and Airports as nodes, and shipping routes as edges.
    """
    def __init__(self):
        self.base_graph = nx.DiGraph()
        self._build_network()
        self.current_graph = copy.deepcopy(self.base_graph)

    def _build_network(self):
        """Constructs a realistic US-based hub-and-spoke + point-to-point network."""
        # Define nodes with approximate Longitude (X) and Latitude (Y) for visualization
        nodes = {
            'SEA': {'name': 'Seattle', 'type': 'Airport', 'pos': (-122.3, 47.6)},
            'LAX': {'name': 'Los Angeles', 'type': 'Hub', 'pos': (-118.2, 34.0)},
            'DEN': {'name': 'Denver', 'type': 'Airport', 'pos': (-104.9, 39.7)},
            'DFW': {'name': 'Dallas', 'type': 'Hub', 'pos': (-96.7, 32.7)},
            'ORD': {'name': 'Chicago', 'type': 'Airport', 'pos': (-87.6, 41.8)},
            'MEM': {'name': 'Memphis', 'type': 'SuperHub', 'pos': (-90.0, 35.1)},
            'ATL': {'name': 'Atlanta', 'type': 'Hub', 'pos': (-84.4, 33.6)},
            'JFK': {'name': 'New York', 'type': 'Airport', 'pos': (-73.7, 40.6)},
            'MIA': {'name': 'Miami', 'type': 'Airport', 'pos': (-80.2, 25.7)}
        }
        
        for node_id, attrs in nodes.items():
            self.base_graph.add_node(node_id, **attrs)

        # Define edges (routes) with [Cost ($), Time (Hours), Risk (0-100), Capacity]
        # Realistic network: most things flow through Hubs (MEM, DFW, ATL, LAX)
        edges = [
            # West Coast / Mountain
            ('SEA', 'LAX', 800, 4.0, 10, 1000), ('LAX', 'SEA', 800, 4.0, 10, 1000),
            ('SEA', 'DEN', 900, 3.5, 15, 800), ('DEN', 'SEA', 900, 3.5, 15, 800),
            ('LAX', 'DEN', 700, 3.0, 5, 1200), ('DEN', 'LAX', 700, 3.0, 5, 1200),
            
            # Connections to Central Hubs
            ('LAX', 'DFW', 1200, 4.5, 10, 2000), ('DFW', 'LAX', 1200, 4.5, 10, 2000),
            ('DEN', 'DFW', 600, 2.5, 10, 1500), ('DFW', 'DEN', 600, 2.5, 10, 1500),
            ('LAX', 'MEM', 1500, 5.0, 12, 3000), ('MEM', 'LAX', 1500, 5.0, 12, 3000),
            ('SEA', 'ORD', 1600, 5.5, 20, 1000), ('ORD', 'SEA', 1600, 5.5, 20, 1000),
            
            # Central / Super Hub Network
            ('DFW', 'MEM', 400, 1.5, 5, 5000), ('MEM', 'DFW', 400, 1.5, 5, 5000),
            ('ORD', 'MEM', 500, 2.0, 15, 4000), ('MEM', 'ORD', 500, 2.0, 15, 4000),
            ('ATL', 'MEM', 350, 1.2, 5, 4500), ('MEM', 'ATL', 350, 1.2, 5, 4500),
            ('DFW', 'ATL', 700, 2.5, 8, 3000), ('ATL', 'DFW', 700, 2.5, 8, 3000),
            ('ORD', 'ATL', 650, 2.2, 10, 2500), ('ATL', 'ORD', 650, 2.2, 10, 2500),
            
            # East Coast
            ('ORD', 'JFK', 800, 3.0, 15, 3000), ('JFK', 'ORD', 800, 3.0, 15, 3000),
            ('MEM', 'JFK', 1100, 3.5, 10, 3500), ('JFK', 'MEM', 1100, 3.5, 10, 3500),
            ('ATL', 'JFK', 750, 2.5, 10, 4000), ('JFK', 'ATL', 750, 2.5, 10, 4000),
            ('ATL', 'MIA', 550, 2.0, 25, 2000), ('MIA', 'ATL', 550, 2.0, 25, 2000),
            ('MEM', 'MIA', 900, 3.0, 20, 1500), ('MIA', 'MEM', 900, 3.0, 20, 1500),
            ('JFK', 'MIA', 1000, 3.5, 20, 2500), ('MIA', 'JFK', 1000, 3.5, 20, 2500)
        ]

        for u, v, cost, time, risk, cap in edges:
            self.base_graph.add_edge(u, v, 
                                     base_cost=cost, current_cost=cost,
                                     base_time=time, current_time=time,
                                     base_risk=risk, current_risk=risk,
                                     base_capacity=cap, current_capacity=cap,
                                     status='Active')

    def reset_to_base(self):
        """Restores the network to its clean, undisrupted state."""
        self.current_graph = copy.deepcopy(self.base_graph)