import pkg_resources

import rdflib

from cc.licenserdf.tests.util import (
    PrinterCollector, unordered_ensure_printer_printed)
from cc.licenserdf.tools import jurisdiction


class MockOpts(object): pass

class MockSaveGraph(object):
    def __init__(self):
        self.graph = None
        self.save_path = None

    def __call__(self, graph, save_path):
        self.graph = graph
        self.save_path = save_path


EXPECTED_INFO_OUTPUT_US = [
    'http://purl.org/dc/elements/1.1/title Etats-Unis',
    'http://purl.org/dc/elements/1.1/title United States',
    'http://purl.org/dc/elements/1.1/title United States',
    'http://creativecommons.org/ns#launched true',
    'http://purl.org/dc/elements/1.1/language en-us',
    'http://creativecommons.org/ns#jurisdictionSite http://creativecommons.org/worldwide/us/',
    'http://creativecommons.org/ns#defaultLanguage en-us',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type http://creativecommons.org/ns#Jurisdiction',
    ]


def test_info():
    opts = MockOpts()
    printer = PrinterCollector()
    opts.rdf_file = pkg_resources.resource_filename(
        'cc.licenserdf.tests', 'rdf/jurisdictions.rdf')
    opts.jurisdiction = ['us']

    jurisdiction.info(opts, printer=printer)
    unordered_ensure_printer_printed(printer, EXPECTED_INFO_OUTPUT_US)


def test_launch():
    opts = MockOpts()
    opts.rdf_file = pkg_resources.resource_filename(
        'cc.licenserdf.tests', 'rdf/jurisdictions.rdf')
    opts.jurisdiction = ['pl']

    graph_saver = MockSaveGraph()

    jurisdiction.launch(opts, save_graph=graph_saver)

    # assert that we got one result, launch is True
    result = graph_saver.graph.value(
        subject=rdflib.URIRef('http://creativecommons.org/international/pl/'),
        predicate=rdflib.URIRef('http://creativecommons.org/ns#launched'))
    expected_result = rdflib.Literal(
        u'true',
        datatype=rdflib.URIRef(
            'http://www.w3.org/2001/XMLSchema-datatypes#boolean'))
    assert result == expected_result

    # make sure that we got the right save path
    assert graph_saver.save_path == opts.rdf_file


def test_add():
    opts = MockOpts()
    opts.rdf_file = pkg_resources.resource_filename(
        'cc.licenserdf.tests', 'rdf/jurisdictions.rdf')
    opts.jurisdiction = ['it']
    opts.i18n_dir = pkg_resources.resource_filename(
        'cc.i18n', 'i18n/')
    opts.juris_uri = "http://www.creativecommons.it"
    opts.langs = 'en_US,sr_LATN'

    graph_saver = MockSaveGraph()

    jurisdiction.add(opts, __save_graph=graph_saver)

    # make sure that we got the right save path
    assert graph_saver.save_path == opts.rdf_file

    # ensure the jurisdiction exists in the output
    ## using a list comprehension here because the generators rdflib
    ## has seem to work weird and aren't list()'able?
    assert rdflib.URIRef('http://creativecommons.org/international/it/') \
        in [i for i in graph_saver.graph.subjects()]

    # ensure that launched is set to False
    result = graph_saver.graph.value(
        subject=rdflib.URIRef('http://creativecommons.org/international/it/'),
        predicate=rdflib.URIRef('http://creativecommons.org/ns#launched'))
    expected_result = rdflib.Literal(
        u'false',
        datatype=rdflib.URIRef(
            'http://www.w3.org/2001/XMLSchema-datatypes#boolean'))
    assert result == expected_result

    # ensure that jurisdictionSite == opts.juris_uri
    result = graph_saver.graph.value(
        subject=rdflib.URIRef('http://creativecommons.org/international/it/'),
        predicate=rdflib.URIRef(
            'http://creativecommons.org/ns#jurisdictionSite'))
    expected_result = rdflib.URIRef('http://www.creativecommons.it')
    assert result == expected_result

    # get all (hopefully translated) titles
    result = graph_saver.graph.triples(
        (rdflib.URIRef('http://creativecommons.org/international/it/'),
         rdflib.URIRef('http://purl.org/dc/elements/1.1/title'),
         None))

    titles = {}
    for subj, pred, obj in result:
        titles[obj.language] = unicode(obj)

    # ensure we have the generated i18n string
    assert titles['i18n'] == u'${Italy}'

    # ensure that the translations were run
    # (just checking a few should be fine)
    assert titles['en'] == u'Italy'
    assert titles['it'] == u'Italia'
