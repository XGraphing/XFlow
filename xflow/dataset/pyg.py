import networkx as nx
import numpy as np
import torch_geometric.datasets as ds
import random
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc

from torch_geometric.datasets import Planetoid

def convert_to_graph(dataset):
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    return G

def add_edge_weights(G, min_weight, max_weight):
    config = mc.Configuration()
    for a, b in G.edges():
        weight = random.uniform(min_weight, max_weight)
        weight = round(weight, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        G[a][b]['weight'] = weight
    return G, config
    
def CiteSeer():
    dataset = Planetoid(root='./Planetoid', name='CiteSeer')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def PubMed():
    dataset = Planetoid(root='./Planetoid', name='PubMed')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def Cora():
    dataset = Planetoid(root='./Planetoid', name='Cora')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def photo():
    dataset = ds.Amazon(root='./geo', name = 'Photo')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    g = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(5,20)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def coms():
    dataset = ds.Amazon(root='./geo', name = 'Computers')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    g = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(5,20)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def bitcoin_otc():
    dataset = SNAPDataset(root='./SNAP', name='BitcoinOTC')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def email_eu_core():
    dataset = SNAPDataset(root='./SNAP', name='email-Eu-core')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def hydro_net():
    dataset = ds.SuiteSparseMatrixCollection(root='./SuiteSparse', name='HydroNet')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def gdelt():
    dataset = SNAPDataset(root='./SNAP', name='GDELT')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def icews18():
    dataset = SNAPDataset(root='./SNAP', name='ICEWS18')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def pol_blogs():
    dataset = SNAPDataset(root='./SNAP', name='polBlogs')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def reddit():
    dataset = JODIEDataset(root='./JODIE', name='Reddit')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def last_fm():
    dataset = JODIEDataset(root='./JODIE', name='LastFM')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def myket():
    dataset = SNAPDataset(root='./SNAP', name='Myket')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config
