import os
import pkg_resources

from cc.licenserdf.tools import license

RDF_DIR = pkg_resources.resource_filename('cc.licenserdf', 'licenses')
TEST_RDF_DIR = pkg_resources.resource_filename(
    'cc.licenserdf.tests', 'rdf/licenses')


def test_license_rdf_filename():
    expected_url = os.path.join(
        RDF_DIR, 'creativecommons.org_licenses_by_2.0_.rdf')
    assert license.license_rdf_filename(
        'http://creativecommons.org/licenses/by/2.0/') == expected_url

    expected_url = os.path.join(
        RDF_DIR, 'creativecommons.org_licenses_by_2.0_cl_.rdf')
    assert license.license_rdf_filename(
        'http://creativecommons.org/licenses/by/2.0/cl/') == expected_url

    expected_url = os.path.join(
        RDF_DIR, 'creativecommons.org_licenses_BSD_.rdf')
    assert license.license_rdf_filename(
        'http://creativecommons.org/licenses/BSD/') == expected_url

    expected_url = os.path.join(
        RDF_DIR, 'creativecommons.org_publicdomain_zero_1.0_.rdf')
    assert license.license_rdf_filename(
        'http://creativecommons.org/publicdomain/zero/1.0/') == expected_url




