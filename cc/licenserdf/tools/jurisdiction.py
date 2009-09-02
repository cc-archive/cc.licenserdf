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
from babel.messages import pofile

from support import *

# *******************************************************************
# * command line option support

INFO = 'info'
ADD = 'add'
LAUNCH = 'launch'
UPDATE = 'update'

def makeOpts():
    """Define an option parser and return it."""
    
    usage = """usage: %prog <action> <jurisdiction> [options]

Jurisdictions are specified by their short letter codes (ie, us).

--launch, --info, --add are mutually exclusive.
"""
    parser = OptionParser(usage)

    # source options
    parser.add_option( '-f', '--file', dest='rdf_file', action='store',
                       help='Location of the jurisdictions RDF file; '
                       'defaults to ./rdf/jurisdictions.rdf')
    parser.add_option( '-i', '--i18n-dir', dest='i18n_dir', action='store',
                       help='Location containing .po files; defaults to '
                       './i18n/')

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
    parser.set_defaults(action=INFO,
                        langs=[],
                        juris_uri=None,
                        i18n_dir='./i18n',
                        rdf_file='./rdf/jurisdictions.rdf')
    
    return parser

# * 
# *******************************************************************

def info(opts, args):
    """Print information for the jurisdiction."""

    j_graph = load_graph(opts.rdf_file)
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
    j_graph = load_graph(opts.rdf_file)
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
    save_graph(j_graph, opts.rdf_file)

def _set_translations(opts, graph, subject, j_code):
    """Replace dc:title assertions for a given jurisdiction with updated
    translations."""

    str_id = 'country.%s' % j_code

    for root, dirnames, files in os.walk(os.path.abspath(opts.i18n_dir), 
                                     topdown=True):

        for dir in dirnames:

            if dir in ('test', 'templates',):
                # ignore fake translations
                continue

            # load the message catalog
            if not os.path.exists(os.path.join(root, dir, 'cc_org.po')):
                continue

            catalog = pofile.read_po(file(os.path.join(root, dir, 'cc_org.po')))
            
            # see if this language has translated the country string
            if str_id not in catalog:
                continue

            # add the assertion
            graph.add((subject, NS_DC['title'], Literal(catalog[str_id].string,
                                                     lang=dir)))
            
        # only walk one level
        dirnames = []

        
def add(opts, args):
    """Add a new jurisdiction."""

    # load the RDF graph
    j_graph = load_graph(opts.rdf_file)
    if args[0][-1] != '/':
        args[0] += '/'
    j_ref = NS_CC_JURISDICTION[args[0]]

    # add the new jurisdiction
    j_graph.add((j_ref, NS_RDF.type, NS_CC.Jurisdiction))

    # set the default launched status
    j_graph.add((j_ref, NS_CC.launched, 
                 Literal("false", datatype=NS_XSD.boolean)))
    
    # set the default jurisdictionSite
    if opts.juris_uri is not None:
        j_graph.add((j_ref, NS_CC.jurisdictionSite, URIRef(opts.juris_uri)))

    # add the translated names
    _set_translations(opts, j_graph, j_ref, args[0][:-1])

    # save the graph
    save_graph(j_graph, opts.rdf_file)

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
        add(opts, args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    cli()
