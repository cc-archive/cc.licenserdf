# Copyright (c) 2007 Nathan R. Yergler, Creative Commons
# Copyright (c) 2017 Creative Commons Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from setuptools import setup, find_packages


setup(
    name="cc.licenserdf",
    version="0.3.0",
    packages=find_packages('.'),
    namespace_packages=['cc', ],
    include_package_data=True,

    dependency_links=[
        'https://github.com/creativecommons/cc.i18n/tarball/'
        'master#egg=cc.i18n',
        'https://github.com/creativecommons/cc.licenserdf/tarball/'
        'master#egg=cc.licenserdf'],

    # scripts and dependencies
    install_requires=[
        'Babel>0.99',
        'cc.i18n',
        'future',
        'nose',
        'rdfadict',
        'rdflib',
        'setuptools',
        'zope.i18n'],

    entry_points={
        'console_scripts': [
            'gen_i18n_titles = cc.licenserdf.tools.gen_i18n_titles:cli',
            'jurisdiction = cc.licenserdf.tools.jurisdiction:cli',
            'license = cc.licenserdf.tools.license:cli',
            'make_schema = cc.licenserdf.tools.make_schema:cli',
            'merge = cc.licenserdf.tools.merge:cli',
            'translate_rdf = cc.licenserdf.tools.translate_rdf:cli']},

    # author metadata
    author='Nathan R. Yergler',
    author_email='nathan@creativecommons.org',
    description='Tool scripts for manipulating the license RDF files.',
    license='MIT',
    url='http://creativecommons.org',
    zip_safe=False,
    )
