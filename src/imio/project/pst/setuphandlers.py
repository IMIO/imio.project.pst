# -*- coding: utf-8 -*-

import os
import logging
logger = logging.getLogger('imio.project.pst')
from Acquisition import aq_base
from zope.component import getUtility, getMultiAdapter
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.i18n.interfaces import ITranslationDomain
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY, FUNCTIONS_REGISTRY
from imio.dashboard.utils import enableFacetedDashboardFor, _updateDefaultCollectionFor
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.security import is_develop_environment
from dexterity.localroles.utils import add_fti_configuration

from data import get_os_oo_ac_data
from imio.project.pst.utils import list_wf_states


logger = logging.getLogger('imio.project.pst: setuphandlers')


def _(msgid, context=None, domain='imio.project.pst'):
    translation_domain = queryUtility(ITranslationDomain, domain)
    return translation_domain.translate(msgid, context=getRequest())


def reimport_faceted_config(folder, xml, default_UID=None):
    """Reimport faceted navigation config."""
    folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(
        import_file=open(os.path.dirname(__file__) + '/faceted_conf/%s' % xml))
    if default_UID:
        _updateDefaultCollectionFor(folder, default_UID)


def configure_faceted_folder(folder, xml=None, default_UID=None):
    """Configure faceted navigation for incoming-mail folder."""
    enableFacetedDashboardFor(folder, xml and os.path.dirname(__file__) + '/faceted_conf/%s' % xml or None)
    if default_UID:
        _updateDefaultCollectionFor(folder, default_UID)


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
    adaptDefaultPortal(portal)
    addOrUpdateIndexes(portal, {'reference_number': ('FieldIndex', {})})
    # addOrUpdateIndexes(portal, {'administrative_responsible': ('KeywordIndex', {})})
    # addOrUpdateIndexes(portal, {'manager': ('KeywordIndex', {})})

    # add a default 'templates' directory containing the odt templates
    _addTemplatesDirectory(context)
    # add a default 'PST' projectspace where to store objectives and actions. Add dashboard
    _addPSTprojectspace(context)

    # add some groups of users with different profiles
    _addPSTGroups(context)
    # set default application security
    _setDefaultApplicationSecurity(context)
    # reorder tabs, make sure 'contacts' is after 'PST'
    _reorderTabs(context)
    # Add a mandatory function in contact plonegroup configuration
    _updateContactPlonegroupConfiguration(context)
    # configure dexterity.localrolesfield
    configure_rolefields(portal)


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
        folder.setLocallyAllowedTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        folder.setImmediatelyAddableTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        folder.setExcludeFromNav(True)
    folder = site.templates
    do_transitions(folder, transitions=['publish_internally'], logger=logger)

    templates = [
        #('pstaction_template', 'fichepstaction.odt'),
        #('operationalobjective_template', 'ficheoo.odt'),
        ('pst_full', u'pst_full.odt'),
        ('tableaubord', u'tableaubord.odt'),
    ]
    for id, filename in templates:
        if not base_hasattr(folder, id):
            tmpl = api.content.create(
                type='ConfigurablePODTemplate',
                id=id,
                title=filename,
                odt_file=NamedBlobFile(
                    data=context.readDataFile('templates/%s' % filename),
                    contentType='applications/odt',
                    filename=filename,
                ),
                container=folder,
                # excludeFromNav=True,
                pod_formats=['odt'],
                pod_portal_types=['projectspace', 'strategicobjective', 'operationalobjective'],
                # style_template=[style_template.UID()],
                # merge_templates=[{'template': sub_template.UID(), 'pod_context_name': 'header',}],
            )
            do_transitions(tmpl, transitions=['publish_internally'])


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
    configureDashboard(projectspace)
    behaviour.setConstrainTypesMode(1)
    behaviour.setLocallyAllowedTypes(['strategicobjective', 'File', ])
    behaviour.setImmediatelyAddableTypes(['strategicobjective', 'File', ])


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


def add_plonegroups_to_registry():
    registry = getUtility(IRegistry)
    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'actioneditor']:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [
            {
                'fct_title': u"Gestionnaire d'action",
                'fct_id': u'actioneditor'
            }
        ]
    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'admin_resp']:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [
            {
                'fct_title': u"Responsable administratif",
                'fct_id': u'admin_resp'
            }
        ]

    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'editeur']:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [
            {
                'fct_title': u'Éditeur',
                'fct_id': u'editeur'
            }
        ]

    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'validateur']:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [
            {
                'fct_title': u'Validateur',
                'fct_id': u'validateur'
            }
        ]


def _updateContactPlonegroupConfiguration(context):
    """
        Add a mandatory function in plonegroup config
    """
    if isNotCurrentProfile(context):
        return

    add_plonegroups_to_registry()


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


def adaptDefaultPortal(site):
    """Adapt some properties of the default portal"""

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
    if 'front-page' in site and 'pst' not in site:
        frontpage = getattr(site, 'front-page')
        frontpage.setTitle(_("front_page_title"))
        frontpage.setDescription(_("front_page_descr"))
        frontpage.setText(_("front_page_text"), mimetype='text/html')
        #remove the presentation mode
        frontpage.setPresentation(False)
        frontpage.reindexObject()
        logger.info('front page adapted')

    #we apply a method of CPUtils to configure CKeditor
    logger.info("Configuring CKeditor")
    try:
        from Products.CPUtils.Extensions.utils import configure_ckeditor
        if (not hasattr(site.portal_properties, 'ckeditor_properties')
           or site.portal_properties.site_properties.default_editor != 'CKeditor'):
            configure_ckeditor(site, custom='urban')
    except ImportError:
        pass

    logger.info("Configuring externaleditor")
    registry = getUtility(IRegistry)
    registry['externaleditor.ext_editor'] = True
    if 'Image' in registry['externaleditor.externaleditor_enabled_types']:
        registry['externaleditor.externaleditor_enabled_types'] = ['PODTemplate', 'ConfigurablePODTemplate',
                                                                   'DashboardPODTemplate', 'SubTemplate',
                                                                   'StyleTemplate']


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
    params = {'title': u"Mon organisation", 'organization_type': u'commune',
              'zip_code': u'0010', 'city': u'Ma ville',
              'street': u'Rue de la commune', 'number': u'1',
              }
    # use invokeFactory for the special 'plonegroup-organization'
    # or it fails with collective.contact.plonegroup while adding content here under...
    contacts.invokeFactory('organization', id='plonegroup-organization', **params)
    own_orga = contacts['plonegroup-organization']
    notify(ObjectCreatedEvent(own_orga))

    # Departments and services creation
    sublevels = [
        (u'echevinat', u'Echevins',
         [u'1er échevin', u'2ème échevin', u'3ème échevin',
          u'4ème échevin', u'5ème échevin', u'6ème échevin',
          u'7ème échevin', u'8ème échevin', u'9ème échevin', ]),
        (u'service', u'Services',
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
                                       **{'title': department, 'organization_type': organization_type})
        for service in services:
            obj = createContentInContainer(dep, 'organization',
                                           **{'title': service, 'organization_type': u'service'})
            if department == 'Services' and obj.UID() not in registry[ORGANIZATIONS_REGISTRY]:
                group_ids.append(obj.UID())
    if group_ids:
        registry[ORGANIZATIONS_REGISTRY] = registry[ORGANIZATIONS_REGISTRY] + group_ids


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
    registry = getUtility(IRegistry)
    registry[ORGANIZATIONS_REGISTRY]
    groups = {}
    for uid in registry[ORGANIZATIONS_REGISTRY]:
        service = uuidToObject(uid)
        groups[service.id] = uid

    # data has 3 levels :
    # - strategicobjective
    # - operationalobjective
    # - pstaction
    data = get_os_oo_ac_data(groups)

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
    password = 'Project69!'
    if is_develop_environment():
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


COLUMNS_FOR_CONTENT_TYPES = {
    'strategicobjective': (u'select_row', u'pretty_link', u'review_state', u'categories', u'history_actions'),
    'operationalobjective': (u'select_row', u'pretty_link', u'review_state', u'manager', u'planned_end_date',
                             u'priority', u'categories', u'history_actions'),
    'pstaction': (u'select_row', u'pretty_link', u'review_state', u'manager', u'planned_begin_date',
                  u'planned_end_date', u'effective_begin_date', u'effective_end_date', u'progress',
                  u'health_indicator', u'history_actions'),
    'task': (u'select_row', u'pretty_link', u'task_parent', u'assigned_group',
             u'assigned_user', u'due_date', u'CreationDate', u'history_actions'),
}


def add_db_col_folder(folder, id, title, content_type, position, displayed=''):
    """Add dashboard collection folder."""
    if base_hasattr(folder, id):
        return folder[id]

    ttool = api.portal.get_tool('portal_types')
    ttool.Folder._constructInstance(
        folder, id=id, title=title, rights=displayed)
    folder.moveObjectToPosition(id, position)
    col_folder = folder[id]
    col_folder.setConstrainTypesMode(1)
    col_folder.setLocallyAllowedTypes(['DashboardCollection'])
    col_folder.setImmediatelyAddableTypes(['DashboardCollection'])
    col_folder.setExcludeFromNav(True)
    folder.portal_workflow.doActionFor(col_folder, "publish_internally")
    createBaseCollections(col_folder, content_type)
    createStateCollections(col_folder, content_type)
    # configure faceted
    configure_faceted_folder(
        col_folder, xml='{}.xml'.format(content_type),
        default_UID=col_folder['all'].UID())
    return col_folder


def configureDashboard(pst):
    """Configure dashboard (add folders and collections)."""
    collection_folders = [
        # (folder id, folder title, content type for the collections)
        ('strategicobjectives', _("Strategic objectives"), 'strategicobjective'),
        ('operationalobjectives', _("Operational objectives"), 'operationalobjective'),
        ('pstactions', _("Actions"), 'pstaction'),
        ('tasks', _("Tasks"), 'task'),
    ]
    for i, (name, title, content_type) in enumerate(collection_folders):
        if name not in pst:
            add_db_col_folder(pst, name, title, content_type, i, displayed='')

    # configure faceted for container
    default_UID = pst['strategicobjectives']['all'].UID()
    configure_faceted_folder(
        pst, xml='default_dashboard_widgets.xml', default_UID=default_UID)


def createStateCollections(folder, content_type):
    """
        create a collection for each contextual workflow state
    """
    conditions = {
        'strategicobjective': {},
        'operationalobjective': {},
        'pstaction': {},
        'task': {},
    }
    showNumberOfItems = {
        # 'dmsincomingmail': ('created',),
    }
    state_title_mapping = {
        'created': _("State: created"),
        'ongoing': _("State: ongoing"),
        'achieved': _("State: achieved"),
        # pstaction
        # 'created',
        'to_be_scheduled': _("State: to be scheduled"),
        # 'ongoing',
        'terminated': _("State: terminated"),
        'stopped': _("State: stopped"),
        # task
        'closed': _("State: closed"),
        'created': _("State: created"),
        'in_progress': _("State: in progress"),
        'realized': _("State: realized"),
        'to_do': _("State: to do"),
        'to_assign': _("State: to assign"),
    }

    for state in list_wf_states(folder, content_type):
        col_id = "searchfor_%s" % state
        if not base_hasattr(folder, col_id):
            folder.invokeFactory(
                "DashboardCollection",
                id=col_id,
                title=state_title_mapping[state],
                query=[
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': [state]}
                ],
                customViewFields=COLUMNS_FOR_CONTENT_TYPES[content_type],
                tal_condition=conditions[content_type].get(state),
                showNumberOfItems=(
                    state in showNumberOfItems.get(content_type, [])),
                roles_bypassing_talcondition=['Manager', 'Site Administrator'],
                sort_on=u'created',
                sort_reversed=True,
                b_size=30,
                limit=0)
            col = folder[col_id]
            col.setSubject((u'search', ))
            col.reindexObject(['Subject'])
            col.setLayout('tabular_view')
            folder.portal_workflow.doActionFor(col, "publish_internally")


def createDashboardCollections(folder, collections):
    """Use collections dict to create and configure collections in folder."""
    for i, dic in enumerate(collections):
        if not base_hasattr(folder, dic['id']):
            folder.invokeFactory("DashboardCollection",
                                 dic['id'],
                                 title=dic['tit'],
                                 query=dic['query'],
                                 tal_condition=dic['cond'],
                                 roles_bypassing_talcondition=dic['bypass'],
                                 customViewFields=dic['flds'],
                                 showNumberOfItems=dic['count'],
                                 sort_on=dic['sort'],
                                 sort_reversed=dic['rev'],
                                 b_size=30,
                                 limit=0)
            collection = folder[dic['id']]
            folder.portal_workflow.doActionFor(collection, "publish_internally")
            if 'subj' in dic:
                collection.setSubject(dic['subj'])
                collection.reindexObject(['Subject'])
            collection.setLayout('tabular_view')
        if folder.getObjectPosition(dic['id']) != i:
            folder.moveObjectToPosition(dic['id'], i)


def createBaseCollections(folder, content_type):
    collections = [
        {
            'id': 'all',
            'tit': _('All'),
            'subj': (u'search', ),
            'query': [
                {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
            ],
            'cond': u"",
            'bypass': [],
            'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
            'sort': u'created',
            'rev': True,
            'count': False
        },
    ]

    additional_collections_by_types = {

        'strategicobjective': [],

        'operationalobjective': [
            {
                'id': 'i-am-administrative_responsible',
                'tit': _("Which I am administrative responsible"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-administrative-responsible'},
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
            {
                'id': 'i-am-manager',
                'tit': _("Which I am manager"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-actioneditor'},
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
            {
                'id': 'action-deadline-has-passed',
                'tit': _("Which an action deadline has passed"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'has-child-action-deadline-has-passed'},
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
        ],

        'pstaction': [
            {
                'id': 'i-am-manager',
                'tit': _("Which I am manager"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-actioneditor'},
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
            {
                'id': 'deadline-has-passed',
                'tit': _("Which deadline has passed"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'planned_end_date', 'o': 'plone.app.querystring.operation.date.beforeToday'},
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
            {
                'id': 'beginning-is-late',
                'tit': _("Which beginning is late"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': [content_type]},
                    {'i': 'planned_begin_date', 'o': 'plone.app.querystring.operation.date.beforeToday'},
                    {'i': 'effective_begin_date', 'o': 'plone.app.querystring.operation.date.afterToday'},
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
        ],

        'task': [
            # {
            #     'id': 'to_validate',
            #     'tit': _('tasks_to_validate'),
            #     'subj': (u'todo', ),
            #     'query': [
            #         {
            #             'i': 'portal_type',
            #             'o': 'plone.app.querystring.operation.selection.is',
            #             'v': ['task']
            #         },
            #         {
            #             'i': 'CompoundCriterion',
            #             'o': 'plone.app.querystring.operation.compound.is',
            #             'v': 'task-validation'
            #         }
            #     ],
            #     'cond': u"python:object.restrictedTraverse('idm-utils').user_has_review_level('task')",
            #     'bypass': ['Manager', 'Site Administrator'],
            #     'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
            #     'sort': u'created',
            #     'rev': True,
            #     'count': True
            # },
            {
                'id': 'to_treat',
                'tit': _('task_to_treat'),
                'subj': (u'todo', ),
                'query': [
                    {
                        'i': 'portal_type',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['task']
                    },
                    {
                        'i': 'assigned_user',
                        'o': 'plone.app.querystring.operation.string.currentUser'
                    },
                    {
                        'i': 'review_state',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['to_do']
                    }
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': True
            },
            {
                'id': 'im_treating',
                'tit': _('task_im_treating'),
                'subj': (u'todo', ),
                'query': [
                    {
                        'i': 'portal_type',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['task']
                    },
                    {
                        'i': 'assigned_user',
                        'o': 'plone.app.querystring.operation.string.currentUser'
                    },
                    {
                        'i': 'review_state',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['in_progress']
                    }
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': True
            },
            {
                'id': 'have_treated',
                'tit': _('task_have_treated'),
                'subj': (u'search', ),
                'query': [
                    {
                        'i': 'portal_type',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['task']
                    },
                    {
                        'i': 'assigned_user',
                        'o': 'plone.app.querystring.operation.string.currentUser'
                    },
                    {
                        'i': 'review_state',
                        'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['closed', 'realized']
                    }
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
            {
                'id': 'in_my_group',
                'tit': _('tasks_in_my_group'),
                'subj': (u'search', ),
                'query': [
                    {
                        'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['task']
                    },
                    {
                        'i': 'CompoundCriterion',
                        'o': 'plone.app.querystring.operation.compound.is',
                        'v': 'task-in-assigned-group'
                    }
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
            {
                'id': 'due_date_passed',
                'tit': _('tasks_with_due_date_passed'),
                'subj': (u'search', ),
                'query': [
                    {
                        'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is',
                        'v': ['task']
                    },
                    {
                        'i': 'due_date',
                        'o': 'plone.app.querystring.operation.date.beforeToday'
                    },
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type],
                'sort': u'created',
                'rev': True,
                'count': False
            },
        ],

    }

    collections.extend(additional_collections_by_types[content_type])
    createDashboardCollections(folder, collections)


def configure_rolefields(portal):
    """Configure the rolefields on types."""
    config = {
        'pstaction': {
            'manager': {
                'created': {
                    'actioneditor': {'roles': ['Editor', 'Reviewer']}
                },
                'to_be_scheduled': {
                    'actioneditor': {'roles': ['Editor', 'Reviewer']}
                },
                'ongoing': {
                    'actioneditor': {'roles': ['Editor', 'Reviewer']}
                },
                'terminated': {
                    'actioneditor': {'roles': ['Editor', 'Reviewer']}
                },
                'stopped': {
                    'actioneditor': {'roles': ['Editor', 'Reviewer']}
                },
            }
        },
        'operationalobjective': {
            'manager': {
                'achieved': {
                    'actioneditor': {'roles': ['Contributor']}
                },
                'created': {
                    'actioneditor': {'roles': ['Contributor']}
                },
                'ongoing': {
                    'actioneditor': {'roles': ['Contributor']}
                },
            },
            'administrative_responsible': {
                'achieved': {
                    'admin_resp': {'roles': ['Reader']},
                },
                'created': {
                    'admin_resp': {'roles': ['Reader']},
                },
                'ongoing': {
                    'admin_resp': {'roles': ['Reader']},
                }
            }
            # TODO: representative_responsible
        },
        'task': {
            'assigned_group': {
                'to_assign': {
                    'validateur': {
                        'roles': ['Contributor', 'Editor', 'Reviewer'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                },
                'to_do': {
                    'editeur': {
                        'roles': ['Contributor', 'Editor'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                    'validateur': {
                        'roles': ['Contributor', 'Editor', 'Reviewer'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                },
                'in_progress': {
                    'editeur': {
                        'roles': ['Contributor', 'Editor'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                    'validateur': {
                        'roles': ['Contributor', 'Editor', 'Reviewer'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                },
                'realized': {
                    'editeur': {
                        'roles': ['Contributor', 'Editor'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                    'validateur': {
                        'roles': ['Contributor', 'Editor', 'Reviewer'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                },
                'closed': {
                    'editeur': {
                        'roles': ['Reader'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                    'validateur': {
                        'roles': ['Editor', 'Reviewer'],
                        'rel': "{'collective.task.related_taskcontainer':['Reader']}"
                    },
                },
            },
        },
    }
    for portal_type, roles_config in config.iteritems():
        for keyname in roles_config:
            # don't overwrite existing configuration unless for task type if not set yet
            force = False
            if portal_type == 'task':
                if (base_hasattr(portal.portal_types.task, 'localroles') and
                        portal.portal_types.task.localroles.get('assigned_group', '') and
                        portal.portal_types.task.localroles['assigned_group'].get('created') and
                        '' in portal.portal_types.task.localroles['assigned_group']['created']):
                    force = True

            msg = add_fti_configuration(
                portal_type, roles_config[keyname], keyname=keyname,
                force=force)
            if msg:
                logger.warn(msg)
