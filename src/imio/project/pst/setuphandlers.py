# -*- coding: utf-8 -*-

import os
import logging
logger = logging.getLogger('imio.project.pst')
from datetime import datetime
from Acquisition import aq_base
from zope.component import queryUtility
from plone.dexterity.utils import createContentInContainer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import base_hasattr


def isNotCurrentProfile(context):
    return context.readDataFile("imioprojectpst_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return
    # add a default 'templates' directory containing the odt templates
    _addTemplatesDirectory(context)
    # add a default 'PST' directory where to store objectives and actions
    _addPSTDirectory(context)


def _addTemplatesDirectory(context):
    """
        Add a root directory for templates
    """
    site = context.getSite()
    logger.info('Adding templates directory')
    if base_hasattr(site, 'templates'):
        logger.warn("Nothing done: directory 'templates' already exists!")
    else:
        params = {'title': "Templates"}
        site.invokeFactory('Folder', 'templates', **params)
        folder = site.templates
        folder.setConstrainTypesMode(1)
        folder.setLocallyAllowedTypes(['File', ])
        folder.setImmediatelyAddableTypes(['File', ])
        folder.setExcludeFromNav(True)
    folder = site.templates
    templates = [
        ('pstaction', 'fichepstaction.odt'),
        ('operationalobjective', 'ficheoo.odt'),
    ]
    templates_dir = os.path.join(context._profile_path, 'templates')
    for id, filename in templates:
#        if not base_hasattr(folder, id):
        if True:  # during development
            filename_path = os.path.join(templates_dir, filename)
            try:
                f = open(filename_path, 'rb')
                file_content = f.read()
                f.close()
            except:
                continue
            try:
                folder.invokeFactory("File", id=id, title=filename, file=file_content)
            except:
                pass
            new_template = getattr(folder, id)
            new_template.setFile(file_content)
            new_template.setFilename(filename)
            new_template.setFormat("application/vnd.oasis.opendocument.text")


def _addPSTDirectory(context):
    """
        Add a root directory for PST
    """
    if isNotCurrentProfile(context):
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
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    logger.info('Adding demo organizations')
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
       Add some demo data : some objectives and actions
    """
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    logger.info('Adding demo data')

    # data has 3 levels :
    # - strategicobjective
    # - operationalobjective
    # - pstaction
    data = {
        'commune-bon-vivre':
        {
        'title': u'Etre une commune où il fait bon vivre dans un cadre agréable, propre et en toute séciruté',
        'categories': u'volet-externe-dvp-politiques-proprete-securite-publique',
        'operationalobjectives': [
            {
            'title': u'Assurer la propreté dans l\'ensemble des parcs de la commune de manière à '
            u'résuire la présence de déchets de 90% au 31 12 2015',
            u'result_indicator': [{'value': 0, 'label': u'Pourcentage de déchets récoltés '
                                u'chaque année et à l\'échéance (31 12 2015)'}],
            'priority': u'1',
            'planned_end_date': datetime.date(datetime(2015, 12, 31)),
            'representative_responsible': ['2eme-echevin', '3eme-echevin'],
            'administrative_responsible': ['secretariat-communal'],
            'manager': ['service-proprete', 'service-travaux'],
            'visible_for': ['service-proprete', 'service-travaux'],
            'extra_concerned_people': u'Police\r\nAgents constatateurs communaux\r\nAgent sanctionnauteur communal\r\nStewards urbains',
            'budget': u'Fonds propres (en cours de chiffrage) et subventions (dossier introduit pour l\'engagement de deux stewards urbains)',
            'comments': u'',
            'actions': [
                {'title': u'Installer des distributeurs de sacs "ramasse crottes", dans les parcs (entrée et sortie)',
                 'manager': ['service-proprete', ],
                 'planned_end_date': datetime.date(datetime(2014, 06, 30)),
                 'extra_concerned_people': u'La firme adjudicatrice au terme du marché public',
                 'budget': u'1000 euros\r\nBudget ordinaire\r\nArticle budgétaire n°: ...',
                 'health_indicator': u'risque',
                 'health_indicator_details': u'Agent traitant malade pour minimum 3 mois -> risque de retard dans le planning',
                 'work_plan': '<p>Les principales tâches à réaliser dans un ordre logique sont:<p>'
                              '<ul>'
                              '<li>inventaire des parcs existants sur la commune (Maxime/Patrick) finalisé pour le 01 06 2013</li>'
                              '<li>passation d\'un marché public pour commander les distributeurs (Michèle) finalisé pour le 01 09 2013</li>'
                              '<li>réception des distributeurs à l\'excution du marché (Michèle)</li>'
                              '<li>placement des distributeurs (Maxime/Patrick) pour le 01 12 2013</li>'
                              '<li>gestion des stocks de sachets (Michèle)</li>'
                              '<li>réapprovisionnement (Maxime)</li>'
                              '</ul>',
                 'comments': u'Attendre le placement des nouvelles poubelles (avant le 01 12 2013)'
                 },
                ]
            },
            ],
        },
        'commune-moderne':
        {
        'title': u'Etre une commune qui offre un service public moderne, efficace et efficient',
        'categories': u'volet-interne-adm-generale-amelioration-administration',
        'operationalobjectives': [
            {
            'title': u'Diminuer le temps d\'attente de l\'usager au guichet population de 20% dans les 12 mois à venir',
            u'result_indicator':
                [
                    {'value': 0, 'label': u'Temps d\'attente diminué de 20% (en %)'},
                ],
            'priority': u'1',
            'planned_end_date': datetime.date(datetime(2013, 12, 31)),
            'representative_responsible': ['1er-echevin'],
            'administrative_responsible': ['secretariat-communal'],
            'manager': ['service-population', 'service-etat-civil'],
            'visible_for': [],
            'extra_concerned_people': u'',
            'budget': u'',
            'comments': u'',
            'actions': [
                {'title': u'Engager 2 agents pour le Service Population',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'Créer un guichet supplémentaire dans les 3 mois',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'Mettre en ligne sur le site internet différents documents "population" à télécharger de chez soi',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                ]
            },
            {
            'title': u'Optimiser l\'accueil au sein de l\'administration communale',
            u'result_indicator':
                [
                    {'value': 0, 'label': u'50% de visiteurs satisfaits (document de satisfaction à remplir) sur un an (en %)'},
                    {'value': 0, 'label': u'Moins de 5% de plaintes (document de plainte à disposition) (en %)'},
                ],
            'priority': u'1',
            'planned_end_date': datetime.date(datetime(2013, 12, 31)),
            'representative_responsible': ['1er-echevin'],
            'administrative_responsible': ['secretariat-communal'],
            'manager': ['service-population', 'service-etat-civil'],
            'visible_for': [],
            'extra_concerned_people': u'',
            'budget': u'',
            'comments': u'',
            'actions': [
                {'title': u'Placer des pictogrammes de guidance',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'Installer une rampe d\'accès pour PMR',
                 'manager': ['service-population', 'service-travaux'],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'risque',
                 'health_indicator_details': u'Problème, retard dû à l\'exécution du marché',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'Mettre en place des parmanences sur rendez-vous',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'risque',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                ]
            },
            ],
        },
        'commune-durable':
        {
        'title': u'Etre une commune qui s\'inscrit dans la lignée des accords de réductions '
                 u'des gaz à effet de serre afin d\'assurer le développement durable',
        'categories': u'volet-externe-dvp-politiques-energie',
        'operationalobjectives': [
            {
            'title': u'Doter la commune de compétences en matière énergétique pour fin 2014 compte tenu du budget',
            u'result_indicator':
                [
                    {'value': 0, 'label': u'Personnel engagé fin 2014 (en nombre de personnes)'},
                    {'value': 0, 'label': u'Personnel formé fin 2014 (en nombre de personnes)'},
                ],
            'priority': u'1',
            'planned_end_date': datetime.date(datetime(2014, 12, 31)),
            'representative_responsible': ['4eme-echevin'],
            'administrative_responsible': ['secretariat-communal'],
            'manager': ['service-de-lurbanisme'],
            'visible_for': ['service-travaux', ],
            'extra_concerned_people': u'',
            'budget': u'',
            'comments': u'',
            'actions': [
                {'title': u'Procéder à l\'engagement d\'un conseiller en énergie',
                 'manager': ['service-de-lurbanisme', ],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'Répondre à l\'appel à projet "écopasseur" de la Wallonie',
                 'manager': ['service-de-lurbanisme', ],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'Inscrire systématiquement les agents du service travaux aux formations énergétiques',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                ]
            },
            {
            'title': u'Réduire la consommation énergétique de la masion commune de 15% sur l\'année 2013',
            u'result_indicator':
                [
                    {'value': 0, 'label': u'Quantité de mazout réduite de 15% au 31 12 2013 (en %)'},
                ],
            'priority': u'1',
            'planned_end_date': datetime.date(datetime(2013, 12, 31)),
            'representative_responsible': ['1er-echevin'],
            'administrative_responsible': ['secretariat-communal'],
            'manager': ['service-de-lurbanisme'],
            'visible_for': [],
            'extra_concerned_people': u'',
            'budget': u'',
            'comments': u'',
            'actions': [
                {'title': u'Réaliser un audit énergétique de l\'administration communale',
                 'manager': ['service-de-lurbanisme', ],
                 'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'En fonction des résultats, procéder à l\'isolation du bâtiment',
                 'manager': ['service-travaux'],
                 'planned_end_date': datetime.date(datetime(2013, 10, 31)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'',
                 'work_plan': '',
                 'comments': u''
                 },
                {'title': u'En fonction des résultats, installer une pompe à chaleur',
                 'manager': ['service-population', ],
                 'planned_end_date': datetime.date(datetime(2013, 10, 31)),
                 'extra_concerned_people': u'',
                 'budget': u'',
                 'health_indicator': u'bon',
                 'health_indicator_details': u'Devenu sans objet compte tenu des résultats de l\'audit',
                 'work_plan': '',
                 'comments': u''
                 },
                ]
            },
            ],
        }
    }

    # create all this in a folder named 'pst' at the root of the Plone Site
    pst = site.pst
    for strategicobjective in data:
        strategicObj = createContentInContainer(pst, "strategicobjective", **data[strategicobjective])
        for operationalobjective in data[strategicobjective]['operationalobjectives']:
            operationalObj = createContentInContainer(strategicObj,
                                                      "operationalobjective",
                                                      **operationalobjective)
            for action in operationalobjective['actions']:
                createContentInContainer(operationalObj,
                                         "pstaction",
                                         **action)

    # reindex portal_catalog
    site.portal_catalog.refreshCatalog()
