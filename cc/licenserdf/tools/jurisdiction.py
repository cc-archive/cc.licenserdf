"""
jurisdiction.py

Maintenance script for manipulating jurisidiction information representated
as RDF.

Based on a script developed by Will Frank, updated by Nathan R. Yergler to 
manipulate RDF files.

(c) 2005-2009, Creative Commons, Will Frank,
               Nathan R. Yergler, Christopher Webber
licensed to the public under the GNU GPL version 2.
"""

import pkg_resources
import sys
import os
from cc.i18n import mappers

from support import *

import argparse

# *******************************************************************
# * command line option support

def makeOpts():
    """Define an option parser and return it."""
    
    usage = """usage: %prog <action> <jurisdiction> [options]

Jurisdictions are specified by their short letter codes (ie, us).

--launch, --info, --add are mutually exclusive.
"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")

    # action
    info_subparser = subparsers.add_parser(
        'info', help="Display jurisdiction information.")
    launch_subparser = subparsers.add_parser(
        'launch', help="Mark the jurisdiction as launched.")
    add_subparser = subparsers.add_parser(
        'add', help="Add the jurisdiction.")
    
    def add_common_args(subparser):
        subparser.add_argument(
            '-f', '--file', dest='rdf_file', action='store',
            help='Location of the jurisdictions RDF file; '
            'defaults to ./rdf/jurisdictions.rdf')
        subparser.add_argument(
            'jurisdiction', nargs=1,
            help='Jurisdiction to operate on.')

    # info-specific options
    add_common_args(info_subparser)

    # launch-specific options
    add_common_args(launch_subparser)

    # add-specific options
    add_common_args(add_subparser)
    add_subparser.add_argument(
        '-i', '--i18n-dir', dest='i18n_dir', action='store',
        help=('Location containing .po files; defaults to '
              'cc.i18n/cc/i18n/i18n/'))
    add_subparser.add_argument(
        '--lang', dest='langs',
        help=("Comma delimited list of languages for the "
              "specified jurisdiction"))
    add_subparser.add_argument(
        '--uri', dest='juris_uri',
        help="The URI of the jurisdiction specific web page.")

    parser.set_defaults(
        rdf_file=pkg_resources.resource_filename(
            'cc.licenserdf', 'rdf/jurisdictions.rdf'))
    add_subparser.set_defaults(
        juris_uri=None,
        i18n_dir=pkg_resources.resource_filename(
            'cc.i18n', 'i18n/'))

    return parser

# * 
# *******************************************************************

def _printer(string):
    """
    A simple wrapper for the print statement so we can do testing on
    the info method
    """
    print string


def info(opts, printer=_printer):
    """Print information for the jurisdiction."""
    j_graph = load_graph(opts.rdf_file)
    jurisdiction = opts.jurisdiction[0]
    if jurisdiction[-1] != '/':
        jurisdiction += '/'
    j_ref = NS_CC_JURISDICTION[jurisdiction]
    
    if ((j_ref, NS_RDF.type, NS_CC.Jurisdiction)
        not in j_graph):

        raise KeyError("Unknown jurisdiction: %s" % jurisdiction)

    # print the info for this jurisdiction
    for p, o in j_graph.predicate_objects(j_ref):
        # Maybe better output would be nice
        printer("%s %s" % (p, o))

def launch(opts, save_graph=save_graph):
    """Mark the jurisdiction as launched."""

    # load the RDF graph
    j_graph = load_graph(opts.rdf_file)
    jurisdiction = opts.jurisdiction[0]
    if jurisdiction[-1] != '/':
        jurisdiction += '/'
    j_ref = NS_CC_JURISDICTION[jurisdiction]
    
    if ((j_ref, NS_RDF.type, NS_CC.Jurisdiction)
        not in j_graph):

        raise KeyError("Unknown jurisdiction: %s" % jurisdiction)

    # find the specified jurisdiction
    if (NS_CC.launched in j_graph.predicates(j_ref)):
        j_graph.remove((j_ref, NS_CC.launched, None))

    # mark it as launched
    j_graph.add((j_ref, NS_CC.launched, 
                 Literal("true", datatype=NS_XSD.boolean)))

    # save the graph
    save_graph(j_graph, opts.rdf_file)

        
def add(opts, __save_graph=save_graph):
    """Add a new jurisdiction."""

    # load the RDF graph
    j_graph = load_graph(opts.rdf_file)
    jurisdiction = opts.jurisdiction[0]
    if jurisdiction[-1] != '/':
        jurisdiction += '/'
    j_ref = NS_CC_JURISDICTION[jurisdiction]

    # add the new jurisdiction
    j_graph.add((j_ref, NS_RDF.type, NS_CC.Jurisdiction))

    # set the default launched status
    j_graph.add((j_ref, NS_CC.launched, 
                 Literal("false", datatype=NS_XSD.boolean)))
    
    # set the default jurisdictionSite
    if opts.juris_uri is not None:
        j_graph.add((j_ref, NS_CC.jurisdictionSite, URIRef(opts.juris_uri)))

    # Add the i18n string
    j_graph.add((
            j_ref, NS_DC['title'],
            Literal(u"${%s}" % mappers.COUNTRY_MAP[jurisdiction[:-1]],
                    lang="i18n")))

    # add the translated names
    translate_graph(j_graph)

    # add langs
    langs = None
    if opts.langs:
        langs = opts.langs.split(',')

    if langs:
        j_graph.add((j_ref, NS_CC['defaultLanguage'], Literal(langs[0])))

    # save the graph
    __save_graph(j_graph, opts.rdf_file)


def cli():
    """Command line interface for the jurisdiction tool."""

    parser = makeOpts()
    opts = parser.parse_args()

    # make the source file an absolute path
    opts.rdf_file = os.path.abspath(opts.rdf_file)

    if opts.action == 'info':
        info(opts)
    elif opts.action == 'launch':
        launch(opts)
    elif opts.action == 'add':
        add(opts)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    cli()
