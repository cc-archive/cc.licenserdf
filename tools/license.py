"""
license.py

Maintenance script for license RDF.

Original script developed by Will Frank;
* updated by Nathan Yergler to use new XML schema and explicit options.
* updated by Nathan Yergler to generate RDF files.

(c) 2005-2007, Creative Commons, Will Frank, Nathan R. Yergler
licensed to the public under the GNU GPL version 2.
"""

import sys
import os
import urlparse
from optparse import OptionParser

from support import *

# *******************************************************************
# * command line option support

def get_add_option_parser():
    """Define an option parser for the add_license tool and return it."""
    
    usage = "usage: %prog [options] <new_uri>"
    parser = OptionParser(usage)


    # source options
    parser.add_option( '--rdf_dir', dest='rdf_dir', action='store',
                       help='Directory containing the license RDF files; '
                       'defaults to ./license_rdf')

    # license properties
    parser.add_option( '-b', '--based-on', dest='based_on',
                       help='URI of the license the new one is based on.')
    parser.add_option( '-l', '--legalcode', dest='legalcode',
                       help='URI of the legalcode; defaults to the license '
                       'URI + "/legalcode".')
    parser.add_option( '-j', '--jurisdiction', dest='jurisdiction',
                       help='URI of the jurisdiction for the new license; '
                       'defaults to Unported.')
    parser.add_option( '-v', '--version', dest='version',
                       help='Version number to add; defaults to 3.0.'
                       )
    
    parser.set_defaults(rdf_dir='./license_rdf',
                        version='3.0', 
                        legalcode=None,
                        jurisdiction=None)
    
    return parser


def get_addall_option_parser():

    parser = get_add_option_parser()
    parser.set_usage("usage: %prog [options]")

    parser.add_option( '--jc', '--jurisdiction-code', dest='jurisdiction_code',
                       help='Short code of the jurisdiction to add.')
    parser.add_option( '-c', '--codes', dest='codes',
                       help='License codes to add, comma delimited '
                       '(defaults to primary six)',
                       )

    parser.set_defaults(codes="by-nc,by,by-nc-nd,by-nc-sa,by-sa,by-nd")

    return parser

# * 
# *******************************************************************

def _license_rdf_filename(rdf_dir, license_uri):
    """Map a license URI to the filesystem filename containing the RDF."""

    url_pieces = urlparse.urlparse(license_uri)
    filename = os.path.join(rdf_dir, 
                            "_".join([url_pieces[1]] +
                                     url_pieces[2].split('/')[1:]
                                     ) + '.rdf'
                            )

    return os.path.abspath(filename)

def replace_predicate(graph, s, p, new_value):
    """If (s, p, *) exists in graph, remove it; add (s, p, new_value) 
    to the graph."""

    if (p in graph.predicates(s)):
        graph.remove((s, p, None))

    graph.add((s, p, new_value))

def add_license(license_uri, based_on_uri, version, jurisdiction, 
                legalcode_uri, rdf_dir):
    """Create a new license based on an existing one.  Write the resulting
    graph to the rdf_dir."""

    # make sure the license_uri ends with a slash
    if license_uri[-1] != '/':
        license_uri += '/'

    # load the based on graph
    based_on = load_graph(_license_rdf_filename(rdf_dir, based_on_uri))

    # create the graph for the new license
    license = graph()

    # copy base assertions
    for (p, o) in based_on.predicate_objects(URIRef(based_on_uri)):
        license.add((URIRef(license_uri), p, o))

    # add the jurisdiction, version, source
    if jurisdiction is not None:
        replace_predicate(license, URIRef(license_uri), NS_CC.jurisdiction,
                          URIRef(jurisdiction))
    else:
        # unported; remove any jurisdiction assertion
        license.remove((URIRef(license_uri), NS_CC.jurisdiction, None))

    replace_predicate(license, URIRef(license_uri), NS_DCQ.hasVersion, 
                      Literal(version))
    replace_predicate(license, URIRef(license_uri), NS_DC.source, 
                      URIRef(based_on_uri))

    # determine the legalcode URI
    if legalcode_uri is None:
        legalcode_uri = license_uri + "legalcode"

    # add the legalcode predicate
    replace_predicate(license, URIRef(license_uri), NS_CC.legalcode,
                      URIRef(legalcode_uri))

    # write the graph out
    save_graph(license, _license_rdf_filename(rdf_dir, license_uri))

def add_all_cli():
    """Run add for the core six licenses."""

    parser = get_addall_option_parser()
    opts, args = parser.parse_args()

    for code in opts.codes.split(','):
        base_url = "http://creativecommons.org/licenses/%s/%s/" % (code, 
                                                                   opts.version)

        license_url = "%s%s/" % (base_url, opts.jurisdiction_code)

        add_license(license_url, base_url, opts.version, opts.jurisdiction,
                    None, opts.rdf_dir)


def add_cli():
    """Run the add_license tool."""
    parser = get_add_option_parser()
    opts, args = parser.parse_args()

    add_license(args[0], opts.based_on, opts.version, opts.jurisdiction,
                opts.legalcode, opts.rdf_dir)
