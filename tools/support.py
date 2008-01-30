"""Support functions for license RDF tools."""

from rdflib.Graph import Graph
from rdflib import Namespace, RDF, URIRef, Literal

NS_DC = Namespace("http://purl.org/dc/elements/1.1/")
NS_DCQ = Namespace("http://purl.org/dc/terms/")
NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
NS_XSD = Namespace("http://www.w3.org/2001/XMLSchema-datatypes#")

NS_CC = Namespace("http://creativecommons.org/ns#")
NS_CC_JURISDICTION = Namespace("http://creativecommons.org/international/")

def graph():
    """Return an empty graph with common namespaces defined."""

    store = Graph()
    store.bind("cc", "http://creativecommons.org/ns#")
    store.bind("dc", "http://purl.org/dc/elements/1.1/")
    store.bind("dcq","http://purl.org/dc/terms/")
    store.bind("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    return store

def load_graph(filename):
    """Load the specified filename; return a graph."""

    store = graph()
    store.load(filename)

    return store

def save_graph(graph, filename):
    """Save the graph to the specified filename."""

    output_file = open(filename,"w")
    output_file.write(
        graph.serialize(format="pretty-xml", max_depth=1)
        )
    output_file.close()
