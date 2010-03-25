import copy
import pkg_resources

import rdflib

from cc.licenserdf.tools import jurisdiction


class MockOpts(object): pass

class PrinterCollector(object):
    def __init__(self):
        self.printed_strings = []

    def __call__(self, string):
        self.printed_strings.append(string)

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


def _unordered_ensure_printer_printed(printer, expected_output):
    """
    Do an unordered check 
    """
    printer_output = copy.copy(printer.printed_strings)
    for line in expected_output:
        assert line in printer_output
        printer_output.pop(printer_output.index(line))

    # make sure that we only printed what we expected
    assert len(printer_output) is 0


def test_info():
    opts = MockOpts()
    printer = PrinterCollector()
    opts.rdf_file = pkg_resources.resource_filename(
        'cc.licenserdf.tests', 'rdf/jurisdictions.rdf')
    opts.jurisdiction = ['us']

    jurisdiction.info(opts, printer=printer)
    _unordered_ensure_printer_printed(printer, EXPECTED_INFO_OUTPUT_US)


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
