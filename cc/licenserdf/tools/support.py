"""Support functions for license RDF tools."""

import os
import pkg_resources

from babel.messages import pofile
from rdflib.Graph import Graph
from rdflib import Namespace, RDF, URIRef, Literal

NS_DC = Namespace("http://purl.org/dc/elements/1.1/")
NS_DCQ = Namespace("http://purl.org/dc/terms/")
NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
NS_XSD = Namespace("http://www.w3.org/2001/XMLSchema-datatypes#")

NS_CC = Namespace("http://creativecommons.org/ns#")
NS_CC_JURISDICTION = Namespace("http://creativecommons.org/international/")

I18N_DIR = pkg_resources.resource_filename('cc.licenserdf', 'i18n/i18n/')


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

def translate_graph(graph, i18n_dir=I18N_DIR):
    """
    Look for title assertions with i18n as the lang, use their object
    as the msgid to find additionaly title translations
    """
    for subject, predicate, obj in graph.triples((
            None, NS_DC['title'], None)):
        if obj.language != 'i18n':
            continue
        else:
            str_id = unicode(obj)
    
        if not str_id:
            return None

        for lang in os.listdir(os.path.abspath(i18n_dir)):
            po_path = os.path.join(i18n_dir, lang, 'cc_org.po')
            if not os.path.exists(po_path):
                continue

            catalog = pofile.read_po(file(po_path))

            if str_id not in catalog:
                continue

            translated = catalog[str_id].string
            graph.add((subject, predicate, Literal(translated, lang=lang)))
