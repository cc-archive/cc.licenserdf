import os
import optparse
import pkg_resources
from StringIO import StringIO

import rdfadict
from rdfadict.sink.graph import GraphSink

from rdflib import URIRef
from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib.syntax.serializers.PrettyXMLSerializer import PrettyXMLSerializer

def create_option_parser():
    """Return an optparse.OptionParser configured for the merge script."""

    parser = optparse.OptionParser()

    # input options
    parser.add_option('-i', '--input-file', dest='input_file',
                      default='cc/licenserdf/rdf/ns.html',
                      help='Input file containing HTML + RDFa.')

    # output options
    parser.add_option('-o', '--output-file', dest='output_file', 
                      default='cc/licenserdf/rdf/schema.rdf',
                      help='Output file for RDF schema.')

    return parser

def remove_assertions(store):
    """Remove assertions from the generated schema."""

    # remove any assertions about the source document (stylesheet, etc)
    store.remove((URIRef("http://creativecommons.org/ns"),None, None))

                  
def schemafy(html_file):
    """Extract RDF from RDFa-annotated [html_file]; return a L{Graph} 
    containing the RDF."""

    # create an empty graph and bind some namespaces
    store = Graph()
    store.bind("cc", "http://creativecommons.org/ns#")
    store.bind("dc", "http://purl.org/dc/elements/1.1/")
    store.bind("dcq","http://purl.org/dc/terms/")
    store.bind("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    store.bind("xsd","http://www.w3.org/2001/XMLSchema-datatypes#")
    store.bind("owl","http://www.w3.org/2002/07/owl#")
    store.bind("xhtml", "http://www.w3.org/1999/xhtml/vocab#")

    # parse the source document
    parser = rdfadict.RdfaParser()
    parser.parse_file(file(html_file), "http://creativecommons.org/ns",
                      sink=GraphSink(store))

    # remove undesirable assertions
    remove_assertions(store)

    return store

def cli():
    """Command line interface for make_schema:

    Take an RDFa annotated HTML document and generate schema.rdf from it."""

    # parser the command line options
    (options, args) = create_option_parser().parse_args()

    # determine the absolute output dir
    output_fn = os.path.abspath( os.path.join( 
            os.getcwd(), options.output_file)
                                  )

    # write the RDF/XML translation of the source file
    output_file = open(output_fn,"w")
    output_file.write(schemafy(options.input_file).serialize(max_depth=1))
    output_file.close()
