# -*- coding: utf-8 -*-
"""Installer for the imio.project.pst package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='imio.project.pst',
    version='1.3.dev0',
    description="PST management",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='',
    author='IMIO',
    author_email='dev@imio.be',
    url='http://pypi.python.org/pypi/imio.project.pst',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['imio', 'imio.project'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Plone',
        'Pillow',
        'Products.CPUtils',
        'appy',
        'collective.behavior.sdg',
        'collective.ckeditor',
        'collective.dexteritytextindexer',
        'collective.documentgenerator',
        'collective.excelexport',
        'collective.externaleditor',
        'collective.messagesviewlet',
        'collective.portlet.actions',
        'collective.task',
        'collective.symlink',
        'dexterity.localrolesfield',
        'imio.annex',
        'imio.dashboard',
        'imio.helpers',
        'imio.project.core',
        'imio.migrator',
        'imio.pyutils',
        'plone.app.contenttypes',
        'plone.app.lockingbehavior',
        'plone.app.versioningbehavior',
        'plone.directives.form',
        'plonetheme.imioapps',
        'z3c.unconfigure',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'ftw.testbrowser',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
