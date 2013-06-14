# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('imio.project.pst')
from Acquisition import aq_base
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import base_hasattr


def isNotCurrentProfile(context):
    return context.readDataFile("imioprojectpst_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return
    site = context.getSite()
    logger.info('Adding templates directory')
    if base_hasattr(site, 'templates'):
        logger.warn("Nothing done: directory 'templates' already exists!")
        return
    params = {'title': "Templates"}
    site.invokeFactory('Folder', 'templates', **params)
    folder = site.templates
    folder.setConstrainTypesMode(1)
    folder.setLocallyAllowedTypes(['File', ])
    folder.setImmediatelyAddableTypes(['File', ])
    folder.setExcludeFromNav(True)
    # add a default 'PST' directory where to store objectives and actions
    _addPSTDirectory(context)


def _addPSTDirectory(context):
    """
        Add a root directory for PST
    """
    if not context.readDataFile("imioprojectpst_data_marker.txt"):
        return
    site = context.getSite()
    logger.info('Adding PST directory')
    if hasattr(aq_base(site), 'pst'):
        logger.warn('Nothing done: directory \'pst\' already exists!')
        return

    params = {'title': "PST"}
    site.invokeFactory('Folder', 'pst', **params)
    folder = site.pst
    folder.setConstrainTypesMode(1)
    folder.setLocallyAllowedTypes(['strategicobjective', ])
    folder.setImmediatelyAddableTypes(['strategicobjective', ])


def addDemoOrganization(context):
    """
        Add french demo data: own organization
    """
    if not context.readDataFile("imioprojectpst_data_marker.txt"):
        return
    site = context.getSite()

    # add the 'contacts' directory if it does not already exists
    if not hasattr(site, 'contacts'):
        organization_types = [{'name': u'Commune', 'token': 'commune'}, ]

        organization_levels = [{'name': u'Echevinat', 'token': 'echevinat'},
                               {'name': u'Service', 'token': 'service'}, ]

        params = {'title': "Contacts",
                  'position_types': [],
                  'organization_types': organization_types,
                  'organization_levels': organization_levels,
                  }
        site.invokeFactory('directory', 'contacts', **params)

    contacts = site.contacts

    if hasattr(contacts, 'plonegroup-organization'):
        logger.warn('Nothing done: plonegroup-organization already exists. You must first delete it to reimport!')
        return

    # Organisations creation (in directory)
    params = {'title': u"Mon organisation",
              'organization_type': u'commune',
              'zip_code': u'0010',
              'city': u'Ma ville',
              'street': u'Rue de la commune',
              'number': u'1',
              }
    contacts.invokeFactory('organization', 'plonegroup-organization', **params)
    own_orga = contacts['plonegroup-organization']

    # Departments and services creation
    sublevels = [
        (u'echevinat',
         u'Echevins',
         [u'1er échevin', u'2ème échevin', u'3ème échevin',
          u'4ème échevin', u'5ème échevin', u'6ème échevin',
          u'7ème échevin', u'8ème échevin', u'9ème échevin', ]),
        (u'service',
         u'Services',
         [u'Accueil', u'Cabinet du Bourgmestre', u'ADL', u'Cellule Marchés Publics',
          u'Receveur Communal', u'Secrétariat Communal', u'Service de l\'Enseignement',
          u'Service Etat-civil', u'Service Finances', u'Service Informatique',
          u'Service du Personnel', u'Service Propreté', u'Service Population',
          u'Service Travaux', u'Service de l\'Urbanisme', ]),
    ]
    idnormalizer = queryUtility(IIDNormalizer)
    for (organization_type, department, services) in sublevels:
        orga_id = own_orga.invokeFactory('organization', idnormalizer.normalize(department),
                                         **{'title': department, 'organization_type': organization_type})
        dep = own_orga[orga_id]
        for service in services:
            dep.invokeFactory('organization', idnormalizer.normalize(service),
                              **{'title': service, 'organization_type': u'service'})


def addDemoData(context):
    """
        Add data for demo purpose
    """
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    # data content with every types and levels
    return
