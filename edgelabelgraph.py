import networkx as nx
import copy

class EdgeLabelGraph(nx.DiGraph):
    def __init__(self):
        super().__init__()
        self.edge_labels = dict()
        self.edges_with_vertex = dict()
        self.all_labels = set()

    def add_edge_with_labels(self, edge, labels=set()):
        edge = tuple(sorted(edge))
        if edge in self.edge_labels:
            self.edge_labels[edge] |= labels
        else:
            self.add_edge(*edge)
            self.edge_labels[edge] = labels
            for v in edge:
                if not v in self.edges_with_vertex:
                    self.edges_with_vertex[v] = set()
                self.edges_with_vertex[v].add(edge)
        for label in labels:
            self.all_labels.add(label)

    def density(self):
        n = nx.number_of_nodes(self)
        m = nx.number_of_edges(self)
        if n > 0:
            return m/n
        return 0

    def delete_edge(self, edge):
        """Delete an edge from the graph.
        Does not update the all_labels set even if the last edge with a certain label is deleted."""
        del self.edge_labels[edge]
        for v in edge:
            self.edges_with_vertex[v].remove(edge)
            if len(self.edges_with_vertex[v]) == 0:
                self.remove_node(v)
        if edge in self.edges():
            self.remove_edge(*edge)

    def update_label_set(self):
        self.all_labels = set()
        for edge in self.edges:
            for label in self.edge_labels[edge]:
                self.all_labels.add(label)

    def create_copy(self):
        G = self.copy()
        G.edge_labels = copy.deepcopy(self.edge_labels)
        G.all_labels = self.all_labels.copy()
        G.edges_with_vertex = copy.deepcopy(self.edges_with_vertex)
        return G
