# -*- coding: utf-8 -*-

import os
import logging
logger = logging.getLogger('imio.project.pst')
from datetime import datetime
from DateTime import DateTime
from Acquisition import aq_base
from zope.component import getUtility, getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from plone.dexterity.utils import createContentInContainer
from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY, FUNCTIONS_REGISTRY
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from imio.helpers.catalog import addOrUpdateIndexes
logger = logging.getLogger('imio.project.pst: setuphandlers')


def isNotCurrentProfile(context):
    return context.readDataFile("imioprojectpst_marker.txt") is None


def do_transitions(obj, transitions=[], logger=None):
    """
        do the given transitions
    """
    errors = []
    workflowTool = getToolByName(obj, "portal_workflow")
    for transition in transitions:
        try:
            workflowTool.doActionFor(obj, transition)
        except WorkflowException:
            errors.append("Cannot apply transition '%s' on obj '%s'" % (transition, obj))
    if logger:
        [logger.warn(error) for error in errors]
    else:
        return errors


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return
    portal = context.getSite()
    if hasattr(portal, 'front-page'):
        do_transitions(getattr(portal, 'front-page'),
                       transitions=['publish_internally', 'publish_externally'],
                       logger=logger)
    addOrUpdateIndexes(portal, {'reference_number': ('FieldIndex', {})})
    # addOrUpdateIndexes(portal, {'administrative_responsible': ('KeywordIndex', {})})
    # addOrUpdateIndexes(portal, {'manager': ('KeywordIndex', {})})

    # add a default 'templates' directory containing the odt templates
    _addTemplatesDirectory(context)
    # add a default 'PST' projectspace where to store objectives and actions
    _addPSTprojectspace(context)
    # add topics
    _createCollections(context)
    # add some groups of users with different profiles
    _addPSTGroups(context)
    # set default application security
    _setDefaultApplicationSecurity(context)
    # reorder tabs, make sure 'contacts' is after 'PST'
    _reorderTabs(context)
    # Add a mandatory function in contact plonegroup configuration
    _updateContactPlonegroupConfiguration(context)


def _addTemplatesDirectory(context):
    """Add a root directory for templates"""
    if isNotCurrentProfile(context):
        return
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
    do_transitions(folder, transitions=['publish_internally'], logger=logger)
    templates = [
        #('pstaction_template', 'fichepstaction.odt'),
        #('operationalobjective_template', 'ficheoo.odt'),
        ('pst_template', 'pst_full.odt'),
        ('status_template', 'tableaubord.odt'),
    ]
    templates_dir = os.path.join(context._profile_path, 'templates')
    for id, filename in templates:
        if not base_hasattr(folder, id):
#        if True:  # during development
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


def _addPSTprojectspace(context):
    """Add a projectspace at the root of the site for PST"""
    if isNotCurrentProfile(context):
        return
    site = context.getSite()
    logger.info('Adding PST projectspace')
    if hasattr(aq_base(site), 'pst'):
        logger.warn('Nothing done: projectspace \'pst\' already exists!')
        return

    params = {'title': u"PST"}
    # datagridfield categories
    categories = [
        {'label': u"Volet interne : Administration générale - Accessibilité de l'Administration",
         'key': "volet-interne-adm-generale-accessibilite-administration"},
        {'label': u"Volet interne : Administration générale - Amélioration de l'Administration",
         'key': "volet-interne-adm-generale-amelioration-administration"},
        {'label': u"Volet interne : Administration générale - Structure de pilotage de l'Administration",
         'key': "volet-interne-adm-generale-structure-pilotage-administration"},
        {'label': u"Volet interne : Administration générale - Gestion des ressources humaines",
         'key': "volet-interne-adm-generale-gestion-ressources-humaines"},
        {'label': u"Volet interne : Administration générale - Structuration des services",
         'key': "volet-interne-adm-generale-structuration-services"},
        {'label': u"Volet interne : Administration générale - Fonctionnement propre à chacun des services",
         'key': "volet-interne-adm-generale-fonctionnement-propre-chacun-services"},
        {'label': u"Volet interne : Administration générale - Processus et simplification administrative",
         'key': "volet-interne-adm-generale-processus-simplification-administrative"},
        {'label': u"Volet interne : Administration générale - Communication interne",
         'key': "volet-interne-adm-generale-communication-interne"},
        {'label': u"Volet interne : Administration générale - Gestion du patrimoine",
         'key': "volet-interne-adm-generale-gestion-patrimoine"},
        {'label': u"Volet interne : Administration générale - Gestion informatique et Egouvernement",
         'key': "volet-interne-adm-generale-gestion-informatique-egouvernement"},
        {'label': u"Volet interne : Administration générale - Synergie avec d'autres institutions publiques",
         'key': "volet-interne-adm-generale-synergie-autres-institutions-publiques"},
        {'label': u"Volet externe : Développement des politiques - Action sociale",
         'key': "volet-externe-dvp-politiques-action-sociale"},
        {'label': u"Volet externe : Développement des politiques - Aménagement du territoire",
         'key': "volet-externe-dvp-politiques-amenagement-territoire"},
        {'label': u"Volet externe : Développement des politiques - Culture",
         'key': "volet-externe-dvp-politiques-culture"},
        {'label': u"Volet externe : Développement des politiques - Développement économique",
         'key': "volet-externe-dvp-politiques-dvp-economique"},
        {'label': u"Volet externe : Développement des politiques - Egouvernement",
         'key': "volet-externe-dvp-politiques-egouvernement"},
        {'label': u"Volet externe : Développement des politiques - Energie",
         'key': "volet-externe-dvp-politiques-energie"},
        {'label': u"Volet externe : Développement des politiques - Environnement",
         'key': "volet-externe-dvp-politiques-environnement"},
        {'label': u"Volet externe : Développement des politiques - Internationnal",
         'key': "volet-externe-dvp-politiques-internationnal"},
        {'label': u"Volet externe : Développement des politiques - Logement",
         'key': "volet-externe-dvp-politiques-logement"},
        {'label': u"Volet externe : Développement des politiques - Mobilité",
         'key': "volet-externe-dvp-politiques-mobilite"},
        {'label': u"Volet externe : Développement des politiques - Propreté et sécurité publique",
         'key': "volet-externe-dvp-politiques-proprete-securite-publique"},
        {'label': u"Volet externe : Développement des politiques - Sport",
         'key': "volet-externe-dvp-politiques-sport"},
        {'label': u"Volet externe : Développement des politiques - Tourisme",
         'key': "volet-externe-dvp-politiques-tourisme"},
    ]
    params['categories'] = categories
    # datagridfield priority
    priority = [
        {'label': u"1",
         'key': "1"},
        {'label': u"2",
         'key': "2"},
    ]
    params['priority'] = priority
    # datagridfield budget_types
    budget_types = [
        {'label': u"Europe",
         'key': "europe"},
        {'label': u"Fédéral",
         'key': "federal"},
        {'label': u"Wallonie",
         'key': "wallonie"},
        {'label': u"Fédération Wallonie-Bruxelles",
         'key': "federation-wallonie-bruxelles"},
        {'label': u"Province",
         'key': "province"},
        {'label': u"Ville",
         'key': "ville"},
        {'label': u"Autres",
         'key': "autres"},
    ]
    params['budget_types'] = budget_types
    createContentInContainer(site, 'projectspace', **params)
    projectspace = site.pst
    # we do not publish because, in published state, editors cannot more modify
    # do_transitions(projectspace, transitions=['publish_internally'], logger=logger)
    # set locally allowed types
    behaviour = ISelectableConstrainTypes(projectspace)
    behaviour.setConstrainTypesMode(1)
    behaviour.setLocallyAllowedTypes(['strategicobjective', 'File', ])
    behaviour.setImmediatelyAddableTypes(['strategicobjective', 'File', ])

def _createCollections(context):
    site = context.getSite()
    pst = site.pst
    if hasattr(pst, 'collections'):
        return
    site.portal_types.projectspace.filter_content_types = False
    behaviour = ISelectableConstrainTypes(pst)
    behaviour.setConstrainTypesMode(0)
    pst.invokeFactory(
            'Folder',
            'collections',
            title = 'Collections'
    )
    collections = getattr(pst, 'collections')
    collections.setConstrainTypesMode(1)
    collections.setLocallyAllowedTypes(['Collection', ])
    collections.setImmediatelyAddableTypes(['Collection', ])
    collections.setExcludeFromNav(True)
    collections.setExpirationDate(DateTime('2014/08/28 00:00:00 GMT+2'))

    _createStatesCollections(context, collections, 'strategicobjective')
    _createStatesCollections(context, collections, 'operationalobjective')
    _createStatesCollections(context, collections, 'pstaction')

    site.portal_types.projectspace.filter_content_types = True
    behaviour.setConstrainTypesMode(1)

def _createStatesCollections(context, container, portal_type):
    site = context.getSite()
    for workflow in site.portal_workflow.getWorkflowsFor(portal_type):
        for value in workflow.states.values():
            if not hasattr(container, portal_type + '-' + value.id):
                container.invokeFactory(
                        'Collection',
                        portal_type + '-' + value.id,
                        title = portal_type + ' ' + value.id
                )
                collection = getattr(container, portal_type + '-' + value.id)
                query = [
                    {
                        'i': 'portal_type',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': [portal_type,]
                    }, {
                        'i': 'review_state',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': [value.id,]
                    }
                ]
                collection.query = query
                #collection.limit = 10
                collection.sort_on = u'reference_number'


def _addPSTGroups(context):
    """
       Add groups of 'pst' application users...
    """
    if isNotCurrentProfile(context):
        return
    logger.info('Adding PST groups')
    site = context.getSite()
    #add 3 groups
    #one with pst Managers
    site.portal_groups.addGroup("pst_managers", title="PST Managers")
    #one with pst Readers
    site.portal_groups.addGroup("pst_readers", title="PST Readers")
    #one with pst Editors
    site.portal_groups.addGroup("pst_editors", title="PST Editors")


def _setDefaultApplicationSecurity(context):
    """
       Set sharing on the PST projectspace to access the application
    """
    if isNotCurrentProfile(context):
        return
    logger.info('Setting default application security')
    site = context.getSite()
    # permissions for the PST projectspace
    site.pst.manage_addLocalRoles("pst_managers", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
    site.pst.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
    site.pst.manage_addLocalRoles("pst_readers", ('Reader', ))
    # permissions for the contacts
    site.contacts.manage_addLocalRoles("pst_managers", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))


def _updateContactPlonegroupConfiguration(context):
    """
        Add a mandatory function in plonegroup config
    """
    if isNotCurrentProfile(context):
        return
    registry = getUtility(IRegistry)
    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'actioneditor']:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [{'fct_title': u"Gestionnaire d'action",
                                                                        'fct_id': u'actioneditor'}]


def _reorderTabs(context):
    """
       Reorder displayed tabs, 'PST' then 'contacts'
    """
    if isNotCurrentProfile(context):
        return
    logger.info('Reordering tabs')
    site = context.getSite()
    # just make sure the folder 'PST' is displayed before 'Contacts'
    # intervert those 2 elements
    contactsPosition = site.getObjectPosition('contacts')
    pstPosition = site.getObjectPosition('pst')
    if pstPosition > contactsPosition:
        site.moveObject('pst', contactsPosition)


def adaptDefaultPortal(context):
    """Adapt some properties of the default portal"""
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    #deactivate tabs auto generation in navtree_properties
    #site.portal_properties.site_properties.disable_folder_sections = True
    #remove default created objects like events, news, ...
    for id in ('events', 'news', 'Members'):
        try:
            site.manage_delObjects(ids=[id, ])
            logger.info('%s folder deleted' % id)
        except AttributeError:
            continue

    #change the content of the front-page
    try:
        frontpage = getattr(site, 'front-page')
        #translation doesn't work !!
        #frontpage.setTitle(_("front_page_title"))
        frontpage.setTitle("Programme Stratégique Transversal 0.3")
        #frontpage.setDescription(unicode(_("front_page_descr")))
        frontpage.setDescription(u"Bienvenue sur notre outil vous permettant de définir votre PST")
        #frontpage.setText(unicode(_("front_page_text")), mimetype='text/html')
        frontpage.setText("<p></p><p>L'application de gestion du PST contient actuellement les <strong>fonctionnalités "
                          "suivantes</strong>:</p><ul><li>encodage des objectifs stratégiques</li><li>encodage des "
                          "objectifs opérationnels</li><li>encodage des actions</li><li>ajout d'une référence unique "
                          "par projet facilitant la recherche</li><li>génération au format bureautique</li><li>exportation "
                          "des données au format excel</li><li>gestion des contacts (services traitants, échevins)</li>"
                          "<li>gestion des droits par service</li><li>workflow de traitement sur tous les types d'éléments</li>"
                          "<li>portlet de recherche par état</li><li>...</li></ul><p> </p><p>Les "
                          "<strong>documents générés</strong> sont:</p><ul><li>l'ensemble du PST</li><li>le tableau "
                          "de bord général du PST</li><li>la fiche de l'objectif opérationnel</li><li>la fiche de "
                          "l'objectif stratégique</li></ul><p></p><p>Les <strong>fonctionnalités à venir"
                          "</strong>:</p><ul><li>gestion des tâches</li><li>lien avec la gestion du collège / conseil</li>"
                          "<li>ajout de tableau de bord dans l'application</li><li>...</li></ul><p></p><p> </p>"
                          "<p><a href='pst'>Cliquez ici pour accéder à l'application</a></p>"
                          "<p class='discreet'>Vous devez disposer d'un nom d'utilisateur et d'un mot de passe</p>",
                          mimetype='text/html')
        #remove the presentation mode
        frontpage.setPresentation(False)
        frontpage.reindexObject()
        logger.info('front page adapted')
    except AttributeError:
        #the 'front-page' object does not exist...
        pass

    #we apply a method of CPUtils to configure CKeditor
    logger.info("Configuring CKeditor")
    try:
        from Products.CPUtils.Extensions.utils import configure_ckeditor
        if (not hasattr(site.portal_properties, 'ckeditor_properties')
           or site.portal_properties.site_properties.default_editor != 'CKeditor'):
            configure_ckeditor(site, custom='urban')
    except ImportError:
        pass


def addDemoOrganization(context):
    """
        Add french demo data: own organization
    """
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    logger.info('Adding demo organizations')
    contacts = site.contacts
    # change the state of contacts
    do_transitions(contacts, transitions=['publish_internally'], logger=logger)

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
    # use invokeFactory for the special 'plonegroup-organization'
    # or it fails with collective.contact.plonegroup while adding content here under...
    contacts.invokeFactory('organization', id='plonegroup-organization', **params)
    own_orga = contacts['plonegroup-organization']
    notify(ObjectCreatedEvent(own_orga))

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
    registry = getUtility(IRegistry)
    group_ids = []

    for (organization_type, department, services) in sublevels:
        dep = createContentInContainer(own_orga, 'organization',
                                       **{'title': department,
                                          'organization_type': organization_type}
                                       )
        for service in services:
            obj = createContentInContainer(dep, 'organization',
                                           **{'title': service,
                                              'organization_type': u'service'}
                                           )
            if department == 'Services' and obj.UID() not in registry[ORGANIZATIONS_REGISTRY]:
                group_ids.append(obj.UID())
    if group_ids:
        registry[ORGANIZATIONS_REGISTRY] = registry[ORGANIZATIONS_REGISTRY] + group_ids


def _richtextval(text):
    """ Return a RichTextValue """
    if not isinstance(text, unicode):
        text = text.decode('utf8')
    return RichTextValue(raw=text, mimeType='text/html', outputMimeType='text/html', encoding='utf-8')


def _edit_fields(obj, fields):
    """
        Call the edit form to update some fields
        fields is a dict like {'manager': [a, b]}
    """
    edit = getMultiAdapter((obj, obj.REQUEST), name=u'edit', context=obj)
    edit_form = edit.form_instance
    # form fields and widgets update
    edit_form.update()
    # save "extracted data"
    edit_form.applyChanges(fields)


def addDemoData(context):
    """
       Add some demo data : some objectives and actions
    """
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    logger.info('Adding demo data')
    groups = {}
    for service in site.contacts['plonegroup-organization']['services'].objectValues():
        if not service in groups:
            groups[service.id] = '%s_actioneditor' % service.UID()

    # data has 3 levels :
    # - strategicobjective
    # - operationalobjective
    # - pstaction
    currentYear = datetime.now().year
    data = {
        'commune-bon-vivre':
        {
        'title': u'Etre une commune où il fait bon vivre dans un cadre agréable, propre et en toute sécurité',
        'categories': u'volet-externe-dvp-politiques-proprete-securite-publique',
        'budget': [],
        'budget_comments': _richtextval(u''),
        'operationalobjectives': [
            {
                'title': u'Assurer la propreté dans l\'ensemble des parcs de la commune de manière à '
                         u'réduire la présence de déchets de 90% au 31 12 2015',
                u'result_indicator': [{'value': 50, 'label': u'Nombre de sacs poubelles récoltés '
                                      u'chaque année et à l\'échéance (31 12 2015)',
                                      'reached_value': 0}],
                'priority': u'1',
                'planned_end_date': datetime.date(datetime(2015, 12, 31)),
                'representative_responsible': ['2eme-echevin', '3eme-echevin'],
                'administrative_responsible': ['secretariat-communal'],
                'manager': [groups['service-proprete'], groups['service-travaux']],
                'extra_concerned_people': u'Police\r\nAgents constatateurs communaux\r\nAgent sanctionnauteur communal'
                                          u'\r\nStewards urbains',
                'budget': [],
                'budget_comments': _richtextval(u'Fonds propres (en cours de chiffrage) et subventions (dossier '
                                                u'introduit pour l\'engagement de deux stewards urbains)'),
                'comments': _richtextval(u''),
                'actions': [
                    {'title': u'Installer des distributeurs de sacs "ramasse crottes", dans les parcs '
                              u'(entrée et sortie)',
                     'manager': [groups['service-proprete'], ],
                     'planned_end_date': datetime.date(datetime(2014, 06, 30)),
                     'extra_concerned_people': u'La firme adjudicatrice au terme du marché public',
                     'budget': [{'amount': 12500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 2500.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 250.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear},
                                {'amount': 250.0, 'budget_type': 'province', 'year': currentYear},
                                ],
                     'budget_comments': _richtextval(u'1000 euros\r\nBudget ordinaire\r\nArticle budgétaire n°: ...'),
                     'health_indicator': u'risque',
                     'health_indicator_details': u'Agent traitant malade pour minimum 3 mois -> risque de retard dans '
                                                 u'le planning',
                     'work_plan': _richtextval(u'<p>Les principales tâches à réaliser dans un ordre logique sont:</p>'
                                               u'<ul>'
                                               u'<li>inventaire des parcs existants sur la commune (Maxime/Patrick) '
                                               u'finalisé pour le 01 06 2013</li>'
                                               u'<li>passation d\'un marché public pour commander les distributeurs '
                                               u'(Michèle) finalisé pour le 01 09 2013</li>'
                                               u'<li>réception des distributeurs à l\'excution du marché (Michèle)</li>'
                                               u'<li>placement des distributeurs (Maxime) pour le 01 12 2013</li>'
                                               u'<li>gestion des stocks de sachets (Michèle)</li>'
                                               u'<li>réapprovisionnement (Maxime)</li>'
                                               u'</ul>'),
                     'comments': _richtextval(u'Attendre le placement des nouvelles poubelles (avant le 01 12 2013)')
                     },
                ]
            },
        ],
        },
        'commune-moderne':
        {
        'title': u'Etre une commune qui offre un service public moderne, efficace et efficient',
        'categories': u'volet-interne-adm-generale-amelioration-administration',
        'budget': [],
        'budget_comments': _richtextval(u''),
        'operationalobjectives': [
            {
                'title': u"Diminuer le temps d'attente de l'usager au guichet population de 20% dans les 12 mois "
                         u"à venir",
                u'result_indicator':
                [
                    {'value': 20, 'label': u'Diminution du temps d\'attente (en %)', 'reached_value': 0},
                ],
                'priority': u'1',
                'planned_end_date': datetime.date(datetime(2013, 12, 31)),
                'representative_responsible': ['1er-echevin'],
                'administrative_responsible': ['secretariat-communal'],
                'manager': [groups['service-population'], groups['service-etat-civil']],
                'extra_concerned_people': u'',
                'budget': [],
                'comments': _richtextval(u''),
                'actions': [
                    {'title': u'Engager 2 agents pour le Service Population',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 200.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 215.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear},
                                {'amount': 250.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                {'amount': 100.0, 'budget_type': 'europe', 'year': currentYear+1},
                                {'amount': 115.50, 'budget_type': 'federation-wallonie-bruxelles',
                                 'year': currentYear+1},
                                {'amount': 1111.00, 'budget_type': 'province', 'year': currentYear+1},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u''),
                     },
                    {'title': u'Créer un guichet supplémentaire dans les 3 mois',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 200.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 215.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear},
                                {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u''),
                     },
                    {'title': u'Mettre en ligne sur le site internet différents documents "population" à télécharger '
                              u'de chez soi',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 1500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 18500.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 2000.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear},
                                {'amount': 3000.0, 'budget_type': 'province', 'year': currentYear},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u''),
                     },
                ]
            },
            {
                'title': u'Optimiser l\'accueil au sein de l\'administration communale',
                u'result_indicator':
                [
                    {'value': 50, 'label': u'Pourcentage minimum de visiteurs satisfaits (document de satisfaction '
                                           u'à remplir) sur un an', 'reached_value': 0},
                    {'value': 5, 'label': u'Pourcentage maximum de plaintes (document de plainte à disposition)',
                     'reached_value': 0},
                ],
                'priority': u'1',
                'planned_end_date': datetime.date(datetime(2013, 12, 31)),
                'representative_responsible': ['1er-echevin'],
                'administrative_responsible': ['secretariat-communal'],
                'manager': [groups['service-population'], groups['service-etat-civil']],
                'extra_concerned_people': u'',
                'budget': [],
                'comments': _richtextval(u''),
                'actions': [
                    {'title': u'Placer des pictogrammes de guidance',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 50.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 250.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 15.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear},
                                {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear+1},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u''),
                     },
                    {'title': u'Installer une rampe d\'accès pour PMR',
                     'manager': [groups['service-population'], groups['service-travaux']],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 600.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                {'amount': 841.0, 'budget_type': 'europe', 'year': currentYear+1},
                                {'amount': 1552.0, 'budget_type': 'federation-wallonie-bruxelles',
                                 'year': currentYear+1},
                                {'amount': 123.0, 'budget_type': 'ville', 'year': currentYear+1},
                                ],
                     'health_indicator': u'risque',
                     'health_indicator_details': u'Problème, retard dû à l\'exécution du marché',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u''),
                     },
                    {'title': u'Mettre en place des permanences sur rendez-vous',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                     'extra_concerned_people': u'',
                     'budget': [],
                     'health_indicator': u'risque',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u''),
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
        'budget': [],
        'budget_comments': _richtextval(u''),
        'operationalobjectives': [
            {
                'title': u'Doter la commune de compétences en matière énergétique pour fin 2014 compte tenu du budget',
                u'result_indicator':
                [
                    {'value': 2, 'label': u'Nombre de personnes engagées fin 2014', 'reached_value': 0},
                    {'value': 8, 'label': u'Nombre de personnes formées fin 2014', 'reached_value': 0},
                ],
                'priority': u'1',
                'planned_end_date': datetime.date(datetime(2014, 12, 31)),
                'representative_responsible': ['4eme-echevin'],
                'administrative_responsible': ['secretariat-communal'],
                'manager': [groups['service-de-lurbanisme']],
                'extra_concerned_people': u'',
                'budget': [],
                'comments': _richtextval(u''),
                'actions': [
                    {'title': u'Procéder à l\'engagement d\'un conseiller en énergie',
                     'manager': [groups['service-de-lurbanisme'], ],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u'')
                     },
                    {'title': u'Répondre à l\'appel à projet "écopasseur" de la Wallonie',
                     'manager': [groups['service-de-lurbanisme'], ],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 0.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 50.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 5.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear},
                                {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear+1},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u'')
                     },
                    {'title': u'Inscrire systématiquement les agents du service travaux aux formations énergétiques',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 550.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 5250.0, 'budget_type': 'europe', 'year': currentYear},
                                {'amount': 515.55, 'budget_type': 'federation-wallonie-bruxelles',
                                 'year': currentYear+1},
                                {'amount': 5215.0, 'budget_type': 'ville', 'year': currentYear+1},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u'')
                     },
                ]
            },
            {
                'title': u'Réduire la consommation énergétique de la maison commune de 15% sur l\'année 2013',
                u'result_indicator':
                [
                    {'value': 2000, 'label': u'Diminution du nombre de litres de mazout au 31 12 2013',
                     'reached_value': 0},
                ],
                'priority': u'1',
                'planned_end_date': datetime.date(datetime(2013, 12, 31)),
                'representative_responsible': ['1er-echevin'],
                'administrative_responsible': ['secretariat-communal'],
                'manager': [groups['service-de-lurbanisme']],
                'extra_concerned_people': u'',
                'budget': [],
                'comments': _richtextval(u''),
                'actions': [
                    {'title': u'Réaliser un audit énergétique de l\'administration communale',
                     'manager': [groups['service-de-lurbanisme'], ],
                     'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+2},
                                {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+3},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u'')
                     },
                    {'title': u'En fonction des résultats, procéder à l\'isolation du bâtiment',
                     'manager': [groups['service-travaux']],
                     'planned_end_date': datetime.date(datetime(2013, 10, 31)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear},
                                {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+2},
                                {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+3},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u'')
                     },
                    {'title': u'En fonction des résultats, installer une pompe à chaleur',
                     'manager': [groups['service-population'], ],
                     'planned_end_date': datetime.date(datetime(2013, 10, 31)),
                     'extra_concerned_people': u'',
                     'budget': [{'amount': 500.0, 'budget_type': 'europe', 'year': currentYear+2},
                                {'amount': 500.0, 'budget_type': 'federal', 'year': currentYear+2},
                                {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+2},
                                {'amount': 500.0, 'budget_type': 'autres', 'year': currentYear+2},
                                ],
                     'health_indicator': u'bon',
                     'health_indicator_details': u'Devenu sans objet compte tenu des résultats de l\'audit',
                     'work_plan': _richtextval(u''),
                     'comments': _richtextval(u'')
                     },
                ]
            },
        ],
        }
    }

    # needed to avoid ComponentLookupError in edit_view.update()
    from zope.event import notify
    from zope.traversing.interfaces import BeforeTraverseEvent
    notify(BeforeTraverseEvent(site, site.REQUEST))

    # create all this in a folder named 'pst' at the root of the Plone Site
    pst = site.pst
    # needed to avoid invalid attribute in BudgetTypeVocabulary class

    class Dummy(object):
        def __init__(self, context):
            self.context = context

    site.REQUEST['PUBLISHED'] = Dummy(pst)

    for strategicobjective in data:
        strategicObj = createContentInContainer(pst, "strategicobjective", **data[strategicobjective])
        do_transitions(strategicObj, transitions=['begin'], logger=logger)
        for operationalobjective in data[strategicobjective]['operationalobjectives']:
            managers = operationalobjective.pop('manager', '')
            operationalObj = createContentInContainer(strategicObj,
                                                      "operationalobjective",
                                                      **operationalobjective)
            do_transitions(operationalObj, transitions=['begin'], logger=logger)
            if managers:
                _edit_fields(operationalObj, {'manager': managers})
            for action in operationalobjective['actions']:
                managers = action.pop('manager', '')
                action_obj = createContentInContainer(operationalObj,
                                                      "pstaction", **action)
                do_transitions(action_obj, transitions=['set_to_be_scheduled'], logger=logger)
                if managers:
                    _edit_fields(action_obj, {'manager': managers})

    # add some test users
    _addPSTUsers(context)
    # reindex portal_catalog
    site.portal_catalog.refreshCatalog()


def _addPSTUsers(context):
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return

    logger.info('Adding PST users')
    site = context.getSite()
    # mount point ?
    password = 'Project69!'
    if len(site.absolute_url_path().split('/')) <= 2:
        try:
            site.portal_registration.addMember(id="pstmanager", password=password)
            site.portal_registration.addMember(id="pstreader", password=password)
            site.portal_registration.addMember(id="psteditor", password=password)
            #put users in the correct group
            site.acl_users.source_groups.addPrincipalToGroup("pstmanager", "pst_managers")
            site.acl_users.source_groups.addPrincipalToGroup("pstreader", "pst_readers")
            site.acl_users.source_groups.addPrincipalToGroup("psteditor", "pst_editors")
        except ValueError, exc:
            if not str(exc).startswith('The login name you selected is already in use'):
                logger("Error creating user: %s" % (exc))
