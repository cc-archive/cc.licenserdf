from distutils.version import StrictVersion
import pkg_resources
import os

from cc.licenserdf.tools import support

I18N_DIR = pkg_resources.resource_filename('cc.licenserdf', 'i18n/i18n/')
LICENSES_DIR = pkg_resources.resource_filename('cc.licenserdf', 'licenses/')


def setup_i18n_title(license_graph, filename):
    # see if there's already an i18n node.. if so, blast it
    i18n_triples = [
        (s, p, l) for (s, p, l)
        in license_graph.triples((None, support.NS_DC['title'], None))
        if l.language == u'i18n']
    if i18n_triples:
        for i18n_triple in i18n_triples:
            license_graph.remove(i18n_triple)

    license_subj, p, identifier_literal = license_graph.triples(
        (None, support.NS_DC['identifier'], None))[0]
    license_code = unicode(identifier_literal)

    if license_code in ('GPL', 'LGPL'):
        pass

    try:
        license_version = unicode(
            license_graph.triples(
                (None, support.NS_DCQ['hasVersion'], None))[0][2])
    except KeyError:
        license_version = None

    try:
        license_version = unicode(
            license_graph.triples(
                (None, support.NS_DCQ['hasVersion'], None))[0][2])
    except KeyError:
        license_version = None

    try:
        license_jurisdiction = unicode(
            license_graph.triples(
                (None, support.NS_cc['jurisdiction'], None))[0][2])
    except KeyError:
        license_jurisdiction = None

    if license_code == 'devnations':
        i18n_str = '${util.Developing_Nations} License'
    elif 'sampling' in license_code:
        i18n_str = '${licenses.pretty_%s} %s' % (license_code, license_version)
    elif 'GPL' in license_code:
        i18n_str = '${license.%s_name_full' % license_code
    elif license_code == 'publicdomain':
        # Copyright-Only Dedication*  (based on United States law)
        # or Public Domain Certification
        i18n_str = '${licenses.pretty_publicdomain}'
    else:
        # 'standard' license
        if license_jurisdiction:
            pass
        else:
            if StrictVersion(license_version) >= StrictVersion('3.0'):
                i18n_str = '${license.pretty_%s} %s ${util.Unported}' % (
                    license_code, license_version)
            else:
                i18n_str = '${license.pretty_%s} %s ${util.Generic}' % (
                    license_code, license_version)
                

    support.save_graph(filename)


def main():
    for filename in os.listdir(LICENSES_DIR):
        full_filename = os.path.join(LICENSES_DIR, filename)
        license_graph = support.load_graph(full_filename)
        setup_i18n_title(license_graph, full_filename)
