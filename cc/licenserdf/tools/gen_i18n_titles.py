import pkg_resources
import os
import urlparse

import rdflib

from cc.licenserdf.tools import support

I18N_DIR = pkg_resources.resource_filename('cc.i18n', 'i18n/')
LICENSES_DIR = pkg_resources.resource_filename('cc.licenserdf', 'licenses/')


def setup_i18n_title(license_graph, filename):
    license_subj = list(
        license_graph.triples(
            (None, support.NS_RDF['type'], support.NS_CC['License'])))[0][0]

    # see if there's already an i18n node.. if so, blast it
    i18n_triples = [
        (s, p, l) for (s, p, l)
        in license_graph.triples((license_subj, support.NS_DC['title'], None))
        if l.language == u'i18n']
    if i18n_triples:
        for i18n_triple in i18n_triples:
            license_graph.remove(i18n_triple)

    if '/publicdomain/zero/' in str(license_subj):
        license_code = u'cc0'
    else:
        s, p, identifier_literal = list(
            license_graph.triples(
                (license_subj, support.NS_DC['identifier'], None)))[0]
        license_code = unicode(identifier_literal)

    try:
        license_version = unicode(
            list(license_graph.triples(
                    (None, support.NS_DCQ['hasVersion'], None)))[0][2])
    except IndexError:
        try:
            license_version = unicode(
            list(license_graph.triples(
                    (None, support.NS_DC['hasVersion'], None)))[0][2])
        except IndexError:
            license_version = None

    try:
        license_jurisdiction_url = unicode(
            list(
                license_graph.triples(
                    (license_subj, support.NS_CC['jurisdiction'], None)))[0][2])
        license_jurisdiction = urlparse.urlsplit(
            license_jurisdiction_url).path.strip('/').split('/')[1]
    except IndexError:
        license_jurisdiction = None

    i18n_str = support.gen_license_i18n_title(
        license_code, license_version, license_jurisdiction)

    i18n_literal = rdflib.Literal(i18n_str)
    i18n_literal.language = 'i18n'

    license_graph.add(
        (license_subj, support.NS_DC['title'], i18n_literal))

    support.save_graph(license_graph, filename)


def cli():
    for filename in os.listdir(LICENSES_DIR):
        if not filename.endswith('.rdf'):
            continue

        full_filename = os.path.join(LICENSES_DIR, filename)
        license_graph = support.load_graph(full_filename)
        setup_i18n_title(license_graph, full_filename)


if __name__ == '__main__':
    cli()
