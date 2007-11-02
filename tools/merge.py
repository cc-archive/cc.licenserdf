import os
import optparse

from rdflib.Graph import Graph
from rdflib import Namespace, RDF, URIRef, Literal

def create_option_parser():
    """Return an optparse.OptionParser configured for the merge script."""

    parser = optparse.OptionParser()

    # output options
    parser.add_option('-o', '--output-file', dest='output_file', 
                      default='licenses/index.rdf',
                      help='Output file for merged RDF.')

    return parser


def merge(input_files):
    """Return a single rdflib Graph containing the contents of input_files.
    input_files should be a sequence of filenames to load."""

    store = Graph()
    store.bind("cc", "http://creativecommons.org/ns#")
    store.bind("dc", "http://purl.org/dc/elements/1.1/")
    store.bind("dcq","http://purl.org/dc/terms/")
    store.bind("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    for filename in input_files:
        print 'reading %s...' % filename
        store.load(filename)

    return store


def cli():
    """Primary command line interface for the merge tool."""


    # parser the command line options
    (options, input_files) = create_option_parser().parse_args()

    # determine the absolute output dir
    output_fn = os.path.abspath( os.path.join( 
            os.getcwd(), options.output_file)
                                  )

    output_file = open(output_fn,"w")
    output_file.write(
        merge(input_files).serialize(format="pretty-xml")
        )
    output_file.close()

    print 'wrote %s' % output_fn

if __name__ == '__main__':
    cli()
