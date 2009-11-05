"""Support functions for license RDF tools."""

import os

from babel.messages import pofile
from rdflib.Graph import Graph
from rdflib import Namespace, RDF, URIRef, Literal

from cc.licenserdf import util
from cc.licenserdf import cc_org_i18n


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

def translate_graph(graph):
    """
    Look for title assertions with i18n as the lang, use their object
    as the msgid to find additionaly title translations

    Args:
      graph: rdflib processed graph for us to walk through
      i18n_dir: directory of PO files.  Default directory is that
        which is supplied with this package.
    """
    lang_dirs = os.listdir(os.path.abspath(cc_org_i18n.I18N_PATH))

    for subject, predicate, obj in graph.triples((
            None, None, None)):
        if not hasattr(obj, 'language') or obj.language != 'i18n':
            continue
        else:
            str_id = unicode(obj)
    
        if not str_id:
            return None

        for lang in lang_dirs:
            translated = util.inverse_translate(str_id, lang)
            graph.add((subject, predicate, Literal(translated, lang=lang)))
