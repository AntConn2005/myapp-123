import networkx as nx
from typing import Dict, List, Tuple

class RoutingOptimizer:
    """
    Handles Multi-Objective Routing Optimization.
    Balances Cost, Time, and Risk dynamically using Dijkstra's algorithm 
    with custom composite weights.
    """
    def __init__(self, network_manager):
        self.network_manager = network_manager

    def _composite_weight(self, u, v, data, weights: Dict[str, float]) -> float:
        """
        Normalizes and combines attributes into a single cost metric.
        If a route is closed (0 capacity), returns infinity to avoid it entirely.
        """
        if data['current_capacity'] <= 0:
            return float('inf')

        # Rough normalization constants to make sliders balanced
        # Assume max realistic cost ~$3000, time ~24h, risk ~100
        norm_cost = data['current_cost'] / 3000.0
        norm_time = data['current_time'] / 24.0
        norm_risk = data['current_risk'] / 100.0

        score = (weights['cost'] * norm_cost) + \
                (weights['time'] * norm_time) + \
                (weights['risk'] * norm_risk)
        return score

    def find_optimal_route(self, source: str, target: str, weights: Dict[str, float]) -> List[str]:
        """Finds the optimal path based on user-defined priority weights."""
        G = self.network_manager.current_graph
        
        # Check if start/end are fundamentally isolated
        if source not in G or target not in G:
            return []

        def weight_func(u, v, data):
            return self._composite_weight(u, v, data, weights)

        try:
            path = nx.shortest_path(G, source=source, target=target, weight=weight_func)
            return path
        except nx.NetworkXNoPath:
            return []

    def evaluate_route(self, route: List[str]) -> Dict[str, float]:
        """Calculates total absolute metrics for a given route sequence."""
        G = self.network_manager.current_graph
        metrics = {'cost': 0.0, 'time': 0.0, 'risk': 0.0, 'bottleneck_capacity': float('inf')}
        
        if not route or len(route) < 2:
            return metrics

        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            edge = G[u][v]
            metrics['cost'] += edge['current_cost']
            metrics['time'] += edge['current_time']
            metrics['risk'] += edge['current_risk']
            metrics['bottleneck_capacity'] = min(metrics['bottleneck_capacity'], edge['current_capacity'])
        
        # Average risk instead of additive, as risk is typically non-additive probabilistic
        metrics['risk'] = metrics['risk'] / (len(route) - 1)
        return metrics

    def get_alternative_routes(self, source: str, target: str, weights: Dict[str, float], top_k: int = 3):
        """Finds suboptimal but viable alternative paths for fallback."""
        G = self.network_manager.current_graph.copy()
        
        # Remove absolutely closed edges to allow simple path generation
        closed_edges = [(u, v) for u, v, d in G.edges(data=True) if d['current_capacity'] <= 0]
        G.remove_edges_from(closed_edges)

        try:
            # Generate all simple paths, evaluate them, sort by composite score
            paths = list(nx.shortest_simple_paths(G, source, target, weight=None))
            
            evaluated_paths = []
            for p in paths[:15]: # Limit search space for performance
                score = 0
                for i in range(len(p)-1):
                    score += self._composite_weight(p[i], p[i+1], G[p[i]][p[i+1]], weights)
                evaluated_paths.append((score, p))
            
            evaluated_paths.sort(key=lambda x: x[0])
            return [p for score, p in evaluated_paths[1:top_k+1]] # Exclude the absolute best one
        except (nx.NetworkXNoPath, nx.NetworkXError):
            return []