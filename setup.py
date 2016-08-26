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
    version='0.3.1dev',
    description="PST management",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
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
        'Products.PasswordStrength > 0.3.1',
        'appy',
        'beautifulsoup4',
        'communesplone.layout',
        'collective.documentgenerator',
        'collective.excelexport',
        'collective.task',
        'dexterity.localrolesfield',
        'imio.dashboard',
        'imio.helpers',
        'imio.project.core',
        'imio.migrator',
        'plone.app.versioningbehavior',
        'plone.directives.form',
        'plonetheme.imioapps',
        'imio.dashboard',
        'imio.helpers',
        'z3c.unconfigure',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
