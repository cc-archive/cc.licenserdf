"""Support functions for license RDF tools."""

import os
import pkg_resources
from distutils.version import StrictVersion

from babel.messages import pofile
from rdflib.Graph import Graph
from rdflib import Namespace, RDF, URIRef, Literal

from cc.i18n import mappers
from cc.i18n.util import locale_to_lower_lower

from cc.licenserdf import util


NS_DC = Namespace("http://purl.org/dc/elements/1.1/")
NS_DCQ = Namespace("http://purl.org/dc/terms/")
NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
NS_XSD = Namespace("http://www.w3.org/2001/XMLSchema-datatypes#")
NS_FOAF = Namespace("http://xmlns.com/foaf/0.1/")

NS_CC = Namespace("http://creativecommons.org/ns#")
NS_CC_JURISDICTION = Namespace("http://creativecommons.org/international/")


def graph():
    """Return an empty graph with common namespaces defined."""

    store = Graph()
    store.bind("cc", "http://creativecommons.org/ns#")
    store.bind("dc", "http://purl.org/dc/elements/1.1/")
    store.bind("dcq", "http://purl.org/dc/terms/")
    store.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    store.bind("foaf", "http://xmlns.com/foaf/0.1/")

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


def gen_license_i18n_title(license_code, license_version, license_jurisdiction):
    if license_code == 'devnations':
        i18n_str = '${Developing Nations} License'
    elif 'sampling' in license_code:
        i18n_str = '${%s} %s' % (
            mappers.LICENSE_NAME_MAP[license_code],
            license_version)
    elif license_code in ('MIT', 'BSD'):
        i18n_str = license_code
    elif license_code == 'LGPL':
        i18n_str = '${GNU Lesser General Public License}'
    elif license_code == 'GPL':
        i18n_str = '${GNU General Public License}'
    elif license_code == 'publicdomain':
        i18n_str = '${Public Domain}'
    elif license_code == 'cc0':
        i18n_str = 'CC0 %s ${Universal}' % (
            license_version)
    else:
        # 'standard' license
        if license_jurisdiction:
            i18n_str = '${%s} %s ${%s}' % (
                mappers.LICENSE_NAME_MAP[license_code],
                license_version,
                mappers.COUNTRY_MAP[license_jurisdiction])
        else:
            if StrictVersion(license_version) >= StrictVersion('3.0'):
                i18n_str = '${%s} %s ${Unported}' % (
                    mappers.LICENSE_NAME_MAP[license_code],
                    license_version)
            else:
                i18n_str = '${%s} %s ${Generic}' % (
                    mappers.LICENSE_NAME_MAP[license_code],
                    license_version)

    return i18n_str


def translate_graph(graph):
    """
    Look for title assertions with i18n as the lang, use their object
    as the msgid to find additionaly title translations

    Args:
      graph: rdflib processed graph for us to walk through
      i18n_dir: directory of PO files.  Default directory is that
        which is supplied with this package.
    """
    lang_dirs = os.listdir(
        os.path.abspath(
            pkg_resources.resource_filename('cc.i18n', 'i18n')))

    for subject, predicate, obj in graph.triples((
            None, None, None)):
        if not hasattr(obj, 'language') or obj.language != 'i18n':
            continue
        else:
            str_id = unicode(obj)
    
        if not str_id:
            return None

        old_objects = {}

        # remove any previous instane of this language's
        # translations.
        for s, p, old_obj in graph.triples((subject, predicate, None)):
            if lang_dirs.count(old_obj.language):
                old_objects[old_obj.language] = old_obj

        for lang in lang_dirs:
            rdf_lang = locale_to_lower_lower(lang)

            if old_objects.has_key(rdf_lang):
                graph.remove((subject, predicate, old_objects[rdf_lang]))

            translated = util.inverse_translate(str_id, lang)
            graph.add((subject, predicate, Literal(translated, lang=rdf_lang)))
