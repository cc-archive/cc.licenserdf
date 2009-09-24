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

_MODULE_CATALOG_CACHE = {}

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

def translate_graph(graph, i18n_dir=I18N_DIR, use_module_catalog_cache=True):
    """
    Look for title assertions with i18n as the lang, use their object
    as the msgid to find additionaly title translations

    Args:
      graph: rdflib processed graph for us to walk through
      i18n_dir: directory of PO files.  Default directory is that
        which is supplied with this package.
      use_module_catalog_cache: Use a module-level cache of these
        objects.  Possibly not recommended for long-running processes or
        something where memory issue is a concern.
    """
    lang_dirs = os.listdir(os.path.abspath(i18n_dir))

    if use_module_catalog_cache:
        catalog_cache = _MODULE_CATALOG_CACHE
    else:
        catalog_cache = {}

    for subject, predicate, obj in graph.triples((
            None, NS_DC['title'], None)):
        if obj.language != 'i18n':
            continue
        else:
            str_id = unicode(obj)
    
        if not str_id:
            return None

        for lang in lang_dirs:
            po_path = os.path.join(i18n_dir, lang, 'cc_org.po')
            if not os.path.exists(po_path):
                continue

            if catalog_cache.has_key(po_path):
                catalog = catalog_cache[po_path]
            else:
                catalog = pofile.read_po(file(po_path))
                catalog_cache[po_path] = catalog

            if str_id not in catalog:
                continue

            translated = catalog[str_id].string
            graph.add((subject, predicate, Literal(translated, lang=lang)))
