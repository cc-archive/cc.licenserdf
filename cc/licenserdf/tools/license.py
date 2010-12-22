"""
license.py

Maintenance script for license RDF.

Original script developed by Will Frank;
* updated by Nathan Yergler to use new XML schema and explicit options.
* updated by Nathan Yergler to generate RDF files.

(c) 2005-2009, Creative Commons, Will Frank, Nathan R. Yergler, Chris Webber
licensed to the public under the GNU GPL version 2.
"""

import pkg_resources
import sys
import os
import urlparse
from argparse import ArgumentParser

from support import *


RDF_DIR = pkg_resources.resource_filename('cc.licenserdf', 'licenses')


# * 
# *******************************************************************

def _printer(string):
    """
    A simple wrapper for the print statement so we can do testing on
    the info method
    """
    print string

def license_rdf_filename(license_uri, rdf_dir=RDF_DIR):
    """Map a license URI to the filesystem filename containing the RDF."""

    url_pieces = urlparse.urlparse(license_uri)
    filename = os.path.join(
        rdf_dir, 
        "_".join([url_pieces[1]] +
                 url_pieces[2].split('/')[1:]) + '.rdf')

    return os.path.abspath(filename)


def replace_predicate(graph, s, p, new_value):
    """If (s, p, *) exists in graph, remove it; add (s, p, new_value) 
    to the graph."""

    if (p in graph.predicates(s)):
        graph.remove((s, p, None))

    graph.add((s, p, new_value))


def add_license(license_uri, based_on_uri, version, jurisdiction, 
                legalcode_uri, rdf_dir, license_code):
    """Create a new license based on an existing one.  Write the resulting
    graph to the rdf_dir."""

    # make sure the license_uri ends with a slash
    if license_uri[-1] != '/':
        license_uri += '/'

    # create the graph for the new license
    license = graph()

    if based_on_uri:
        # we're starting from an existing license

        # load the based on graph
        based_on = load_graph(license_rdf_filename(based_on_uri, rdf_dir))

        # copy base assertions
        for (p, o) in based_on.predicate_objects(URIRef(based_on_uri)):
            license.add((URIRef(license_uri), p, o))

        replace_predicate(
            license, URIRef(license_uri), NS_DC.source,
            URIRef(based_on_uri))

        # Record the existing FOAF:logos for reference
        old_logos = [
            result[2].split('/')[-1]
            for result in license.triples(
                (URIRef(license_uri), NS_FOAF.logo, None))]

        # Add the FOAF:logos
        license.remove(
            (URIRef(license_uri), NS_FOAF.logo, None))

        # Images get put into /l/ or /p/ depending on whether they are
        # /licenses/ or /publicdomain/ respectively...
        group_letter = urlparse.urlparse(license_uri)[2].lstrip('/')[0]

        for old_logo in old_logos:
            # http://i.creativecommons.org/l/by/3.0/88x31.png
            logo_url = "http://i.creativecommons.org/%s/%s/%s/" % (
                group_letter, license_code, version)

            if jurisdiction:
                logo_url += jurisdiction + "/"

            image_name = old_logo.split('/')[-1]
            logo_url += image_name

            license.add(
                ((URIRef(license_uri), NS_FOAF.logo,
                  URIRef(logo_url))))

    else:
        # add the basic framework -- this is a license
        license.add((URIRef(license_uri), NS_RDF.type, NS_CC.License))

    # add the jurisdiction, version, source
    if jurisdiction is not None:
        jurisdiction_url = "http://creativecommons.org/international/%s/" % (
            jurisdiction)
        replace_predicate(license, URIRef(license_uri), NS_CC.jurisdiction,
                          URIRef(jurisdiction_url))
    else:
        # unported; remove any jurisdiction assertion
        license.remove((URIRef(license_uri), NS_CC.jurisdiction, None))

    # set/replace the version
    replace_predicate(license, URIRef(license_uri), NS_DCQ.hasVersion, 
                      Literal(version))

    # determine the legalcode URI
    if legalcode_uri is None:
        legalcode_uri = license_uri + "legalcode"

    # add the legalcode predicate
    replace_predicate(license, URIRef(license_uri), NS_CC.legalcode,
                      URIRef(legalcode_uri))

    # Add the i18n string
    replace_predicate(
        license, URIRef(license_uri), NS_DC['title'],
        Literal(gen_license_i18n_title(license_code, version, jurisdiction),
                lang="i18n"))

    translate_graph(license)

    # write the graph out
    save_graph(license, license_rdf_filename(license_uri, rdf_dir))


def legalcode_list(license_url, rdf_dir, _printer=_printer):
    """
    List all legalcodes for license_url
    """
    license_filename = license_rdf_filename(license_url, rdf_dir)
    graph = load_graph(license_filename)
    for row in graph.query((
            'SELECT ?title where '
            '{ ?x <http://creativecommons.org/ns#legalcode> ?title . }')):
        _printer(unicode(row[0]))


def legalcode_add(license_url, legalcode_url, rdf_dir, legalcode_lang=None):
    """
    Add a legalcode url the license rdf specified at license_url
    """
    license_filename = license_rdf_filename(license_url, rdf_dir)
    graph = load_graph(license_filename)
    graph.add((URIRef(license_url), NS_CC.legalcode, URIRef(legalcode_url)))

    if legalcode_lang:
        graph.add(
            (URIRef(legalcode_url), NS_DCQ.language,
             Literal(legalcode_lang)))

    save_graph(graph, license_filename)


# *******************************************************************
# * command line option support

def get_args():
    """Get all args taken by this app"""
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")

    add_subparser = subparsers.add_parser(
        'add', help="Add one or more licenses.")
    legalcode_subparser = subparsers.add_parser(
        'legalcode', help="List or operate on the legalcode of a license")

    def add_common_args(subparser):
        # source options
        subparser.add_argument(
            '--rdf_dir', dest='rdf_dir', action='store',
            help='Directory containing the license RDF files; '
            'defaults to ./cc/licenserdf/licenses/')

    ## Add subparser options
    add_common_args(add_subparser)
    add_subparser.add_argument(
        '--all', action="store_true",
        help="Run add for the core six licenses")
        
    # license properties
    add_subparser.add_argument(
        '-b', '--based-on', dest='based_on',
        help='URI of the license the new one is based on.')
    add_subparser.add_argument(
        '-l', '--legalcode', dest='legalcode',
        help='URI of the legalcode; defaults to the license '
        'URI + "/legalcode".')
    add_subparser.add_argument(
        '-j', '--jurisdiction-code', dest='jurisdiction_code', required=True,
        help='Short code of the jurisdiction to add.')
    add_subparser.add_argument(
        '-v', '--version', dest='version',
        help='Version number to add; defaults to 3.0.')
    add_subparser.add_argument(
        '-c', '--codes', dest='codes',
        help=('License codes to add, comma delimited '
              '(defaults to primary six)'))

    add_subparser.add_argument(
        'codes', nargs='*',
        help=('list of license codes to add '
              '(if --all is not specified)'))

    ## Legalcode subparser options
    lc_subparsers = legalcode_subparser.add_subparsers(dest="legalcode_action")
    lc_list_subparser = lc_subparsers.add_parser("list")
    add_common_args(lc_list_subparser)
    lc_list_subparser.add_argument(
        'license_url', nargs=1)

    lc_add_subparser = lc_subparsers.add_parser("add")
    add_common_args(lc_add_subparser)
    lc_add_subparser.add_argument(
        '--lang', dest="legalcode_add_lang",
        help="Mark the language of this legalcode")
    lc_add_subparser.add_argument(
        'license_url', nargs=1)
    lc_add_subparser.add_argument(
        'legalcode_url', nargs=1)

    parser.set_defaults(
        rdf_dir=RDF_DIR,
        version='3.0', 
        legalcode=None,
        jurisdiction=None)

    return parser.parse_args()


def cli_add_action(opts):
    """
    Handle `./bin/license add`
    """
    if opts.all:
        license_codes = (
            'by-nc', 'by', 'by-nc-nd', 'by-nc-sa', 'by-sa', 'by-nd')
    else:
        license_codes = opts.codes

    if not license_codes:
        print "Either a list of codes must be provided as arguments,"
        print "or else the --all flag must be used.  (Did you mean --all?)"
        return 1

    for license_code in license_codes:
        base_url = "http://creativecommons.org/licenses/%s/%s/" % (
            license_code, opts.version)

        license_url = "%s%s/" % (base_url, opts.jurisdiction_code)

        add_license(
            license_url, base_url, opts.version, opts.jurisdiction_code,
            opts.legalcode, opts.rdf_dir, license_code)


def cli():
    """
    Method to handle ./bin/license
    """
    opts = get_args()

    if opts.action == 'add':
        return cli_add_action(opts)
    elif opts.action == 'legalcode' and opts.legalcode_action == 'list':
        return legalcode_list(opts.license_url[0], opts.rdf_dir)
    elif opts.action == 'legalcode' and opts.legalcode_action == 'add':
        return legalcode_add(
            opts.license_url[0], opts.legalcode_url[0], opts.rdf_dir,
            opts.legalcode_add_lang)
    else:
        print "This shouldn't happen."
        return 1
