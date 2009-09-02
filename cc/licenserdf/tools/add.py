import os

from rdflib import URIRef, Namespace, Literal
from rdflib.Graph import Graph


NS_DC = Namespace("http://purl.org/dc/elements/1.1/")
NS_DCQ = Namespace("http://purl.org/dc/terms/")
NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
NS_XSD = Namespace("http://www.w3.org/2001/XMLSchema-datatypes#")
NS_FOAF = Namespace("http://xmlns.com/foaf/0.1/")

NS_CC = Namespace("http://creativecommons.org/ns#")

# helper functions
def code_from_uri(uri):
    """Given a URI representing a CC license, parse out the license_code."""
    base = 'http://creativecommons.org/licenses/'
    return uri[len(base):].split('/')[0]

def image_uris(uri):
    """Given a CC license URI, return a sequence of image URIs."""
    base = 'http://creativecommons.org/licenses/'
    img_base = 'http://i.creativecommons.org/l/'
    img_uri = img_base + uri[len(base):]
    if not img_uri.endswith('/'):
        img_uri = img_uri  + '/'
    return (img_uri + '88x31.png', img_uri + '80x15.png')

for root, dirs, files in os.walk('./license_rdf'):
    for filename in files:
        if filename[-4:] != '.rdf':
            continue
        store = Graph()
        store.bind("cc", "http://creativecommons.org/ns#")
        store.bind("dc", "http://purl.org/dc/elements/1.1/")
        store.bind("dcq","http://purl.org/dc/terms/")
        store.bind("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        store.bind("foaf","http://xmlns.com/foaf/0.1/")
        store.load(os.path.join(root, filename))

        for license in store.subjects(NS_RDF.type, NS_CC.License):

            print 'processing %s ...' % license

            # add short code
            #code = code_from_uri(license)
            #print '  code is %s' % code
            #store.remove( (license, NS_DC.identifier, None) )
            #store.add( (license, NS_DC.identifier, Literal(code)) )

            # associate each License with a LicenseSelector
            #if 'sampling' in code:
            #    sel = 'http://creativecommons.org/license/sampling/'
            #elif code in ('GPL', 'LGPL'):
            #    sel = 'http://creativecommons.org/license/software'
            #elif code == 'publicdomain':
            #    sel = 'http://creativecommons.org/license/publicdomain/'
            #else:
            #    sel = 'http://creativecommons.org/license/'
            #print '  LicenseSelector is %s' % sel
            #store.remove( (license, NS_CC.licenseClass, None) )
            #store.add( (license, NS_CC.licenseClass, URIRef(sel)) )

            # add image uris
            store.remove( (license, NS_FOAF.logo, None) )
            for img in image_uris(license):
                print img
                store.add( (license, NS_FOAF.logo, img) )

        file(os.path.join(root, filename), 'w').write(
            store.serialize(format="pretty-xml", max_depth=1))

