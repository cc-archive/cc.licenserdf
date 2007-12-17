"""
jurisdiction.py

Maintenance script for manipulating jurisidiction information representated
as RDF.

Based on a script developed by Will Frank, updated by Nathan R. Yergler to 
manipulate RDF files.

(c) 2005-2007, Creative Commons, Will Frank, Nathan R. Yergler
licensed to the public under the GNU GPL version 2.
"""

import sys
import os
from optparse import OptionParser

from rdflib.Graph import Graph
from rdflib import Namespace, RDF, URIRef, Literal

NS_DC = Namespace("http://purl.org/dc/elements/1.1/")
NS_DCQ = Namespace("http://purl.org/dc/terms/")
NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
NS_XSD = Namespace("http://www.w3.org/2001/XMLSchema-datatypes#")

NS_CC = Namespace("http://creativecommons.org/ns#")
NS_CC_JURISDICTION = Namespace("http://creativecommons.org/international/")

# *******************************************************************
# * command line option support

INFO = 'info'
ADD = 'add'
LAUNCH = 'launch'

def makeOpts():
    """Define an option parser and return it."""
    
    usage = "usage: %prog <action> <jurisdiction> [options]"
    parser = OptionParser(usage)

    # source options
    parser.add_option( '-f', '--file', dest='rdf_file', action='store',
                       help='Location of the jurisdictions RDF file; '
                       'defaults to ./rdf/jurisdictions.rdf')

    # jurisdiction actions
    parser.add_option( '--info', dest='action',
                       action="store_const", const=INFO,
                       help="Display jurisdiction information.",
                       )
    parser.add_option( '--launch', dest='action',
                       action="store_const", const=LAUNCH,
                       help="Mark the jurisdiction as launched.",
                       )
    parser.add_option( '--add', dest='action',
                       action="store_const", const=ADD,
                       help="Add the jurisdiction.",
                       )

    # jurisdiction information options
    parser.add_option( '--lang', dest='langs',
                       help="Comma delimited list of languages for the "
                       "specified jurisdiction",
                       )
    parser.add_option( '--uri', dest='juris_uri',
                       help="The URI of the jurisdiction specific web page.",
                       )
    parser.set_defaults(licenses="by-nc,by,by-nc-nd,by-nc-sa,by-sa,by-nd",
                        action=INFO,
                        langs=[],
                        rdf_file='./rdf/jurisdictions.rdf')
    
    return parser

# * 
# *******************************************************************

def load_jurisdictions(filename):
    """Load the specified filename; return a graph."""

    store = Graph()
    store.bind("cc", "http://creativecommons.org/ns#")
    store.bind("dc", "http://purl.org/dc/elements/1.1/")
    store.bind("dcq","http://purl.org/dc/terms/")
    store.bind("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    store.load(filename)

    return store

def save_jurisdictions(graph, filename):
    """Save the graph to the specified filename."""

    output_file = open(filename,"w")
    output_file.write(
        graph.serialize(max_depth=1)
        )
    output_file.close()

def info(opts, args):
    """Print information for the jurisdiction."""

    j_graph = load_jurisdictions(opts.rdf_file)
    if args[0][-1] != '/':
        args[0] += '/'
    j_ref = NS_CC_JURISDICTION[args[0]]
    
    if ((j_ref, NS_RDF.type, NS_CC.Jurisdiction)
        not in j_graph):

        raise KeyError("Unknown jurisdiction: %s" % args[0])


    # print the info for this jurisdiction
    for p, o in j_graph.predicate_objects(j_ref):
        # XXX This could be improved greatly
        print str(p), str(o)

def launch(opts, args):
    """Mark the jurisdiction as launched."""

    # load the RDF graph
    j_graph = load_jurisdictions(opts.rdf_file)
    if args[0][-1] != '/':
        args[0] += '/'
    j_ref = NS_CC_JURISDICTION[args[0]]
    
    if ((j_ref, NS_RDF.type, NS_CC.Jurisdiction)
        not in j_graph):

        raise KeyError("Unknown jurisdiction: %s" % args[0])

    # find the specified jurisdiction
    if (NS_CC.launched in j_graph.predicates(j_ref)):
        j_graph.remove((j_ref, NS_CC.launched, None))

    # mark it as launched
    j_graph.add((j_ref, NS_CC.launched, 
                 Literal("true", datatype=NS_XSD.boolean)))

    # save the graph
    save_jurisdictions(j_graph, opts.rdf_file)

def add(opts, argdict):
    """Add a new jurisdiction."""

    raise NotImplementedError()

def cli():
    """Command line interface for the jurisdiction tool."""

    parser = makeOpts()
    opts, args = parser.parse_args()

    # make the source file an absolute path
    opts.rdf_file = os.path.abspath(opts.rdf_file)

    if opts.action == INFO:
        info(opts, args)
    elif opts.action == LAUNCH:
        launch(opts, args)
    elif opts.action == ADD:
        launch(opts, args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    cli()
