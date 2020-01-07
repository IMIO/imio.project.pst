# -*- coding: utf-8 -*-

from Acquisition import aq_base
from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
from collective.documentgenerator.utils import update_templates
from collective.eeafaceted.collectionwidget.interfaces import ICollectionCategories
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from collective.eeafaceted.dashboard.utils import enableFacetedDashboardFor
from data import get_os_oo_ac_data
from data import get_styles_templates
from data import get_templates
from data import TMPL_DIR
from dexterity.localroles.utils import add_fti_configuration
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.content import create
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.helpers.security import generate_password
from imio.helpers.security import get_environment
from imio.project.core.utils import getProjectSpace
from imio.project.pst import _tr as _
from imio.project.pst import add_path
from imio.project.pst import PRODUCT_DIR
from imio.project.pst.interfaces import IActionDashboardBatchActions
from imio.project.pst.interfaces import IImioPSTProject
from imio.project.pst.interfaces import IOODashboardBatchActions
from imio.project.pst.interfaces import IOSDashboardBatchActions
from imio.project.pst.interfaces import ITaskDashboardBatchActions
from plone import api
from plone.app.controlpanel.markup import MarkupControlPanelAdapter
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getToolByName
from utils import list_wf_states
from zope.annotation.interfaces import IAnnotations
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import logging
import os


logger = logging.getLogger('imio.project.pst: setuphandlers')


def reimport_faceted_config(folder, xml, default_UID=None):
    """Reimport faceted navigation config."""
    folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(
        import_file=open(add_path('faceted_conf/%s' % xml)))
    if default_UID:
        _updateDefaultCollectionFor(folder, default_UID)


def configure_faceted_folder(folder, xml=None, default_UID=None):
    """Configure faceted navigation for pst folder."""
    enableFacetedDashboardFor(folder, xml and add_path('faceted_conf/%s' % xml) or None)
    if default_UID:
        _updateDefaultCollectionFor(folder, default_UID)


def isNotCurrentProfile(context):
    return context.readDataFile("imioprojectpst_marker.txt") is None


def do_transitions(obj, transitions=[], logger=None):
    """
        do the given transitions
        NOW SAME IN imio.helpers.content
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
    if getattr(portal, '_TESTING_SITE_', False):
        portal.portal_properties.site_properties.manage_changeProperties(default_language='fr')

    if hasattr(portal, 'front-page'):
        do_transitions(getattr(portal, 'front-page'),
                       transitions=['publish_internally', 'publish_externally'],
                       logger=logger)
    adaptDefaultPortal(portal)
    set_portlet(portal)
    addOrUpdateIndexes(portal, {'reference_number': ('FieldIndex', {})})
    # addOrUpdateIndexes(portal, {'administrative_responsible': ('KeywordIndex', {})})
    # addOrUpdateIndexes(portal, {'manager': ('KeywordIndex', {})})

    # add a default 'templates' directory containing the odt templates
    # _addTemplatesDirectory(context)  # import step
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
    # configure collective.task
    configure_task_config(portal)
    # configure collective.task localroles
    configure_task_rolefields(portal)
    # configure actions panel registry
    configure_actions_panel(portal)

    # add usefull methods
    try:
        from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
        manage_addExternalMethod(portal, 'sge_clean_examples', '', 'imio.project.pst.utils', 'clean_examples')
    except:
        pass


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
        behaviour = ISelectableConstrainTypes(folder)
        behaviour.setConstrainTypesMode(1)
        behaviour.setLocallyAllowedTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        behaviour.setImmediatelyAddableTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        folder.exclude_from_nav = True
        folder.layout = 'dg-templates-listing'
    folder = site.templates
    do_transitions(folder, transitions=['publish_internally'], logger=logger)

    cids = create(get_styles_templates(), pos=True)
    cids.update(create(get_templates(cids), pos=True))


def _extract_templates_infos(lst):
    ret = []
    for dic in lst:
        ret.append(('templates/%s' % dic['id'], '%s/%s' % (TMPL_DIR, dic['attrs']['odt_file'].filename)))
    return ret


def common_dg_templates(context, force):
    if context.readDataFile("imioprojectpst_update_marker.txt") is None:
        return
    site = context.getSite()
    templates = _extract_templates_infos(get_styles_templates())
    templates += _extract_templates_infos(get_templates({1: site.templates['style']}))
    logger.info('Updating templates')
    templates = update_templates(templates, force=force)
    log = ["Template '%s' (%s): %s" % (tup[0], tup[1][len(PRODUCT_DIR)+1:], tup[2]) for tup in templates]
    [logger.info(msg) for msg in log]
    return '\n'.join(log)


def update_dg_templates(context):
    """ Update documentgenerator templates"""
    return common_dg_templates(context, False)


def override_dg_templates(context):
    """ Update documentgenerator templates"""
    return common_dg_templates(context, True)


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
        {'label': u"Volet externe : Développement des politiques - International",
         'key': "volet-externe-dvp-politiques-international"},
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
        {'label': u"0",
         'key': ""},
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
    if getattr(site, '_TESTING_SITE_', False):
        params['budget_years'] = [2019, 2020, 2021, 2022, 2023, 2024]
    else:
        params['budget_years'] = [2019, 2020, 2021, 2022, 2023, 2024]

    createContentInContainer(site, 'projectspace', **params)
    projectspace = site.pst
    alsoProvides(projectspace, IImioPSTProject)
    # local roles
    projectspace.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
    # dashboard
    configureDashboard(projectspace)
    # set default view to not be a faceted view
    projectspace.setLayout('view')
    # set locally allowed types
    behaviour = ISelectableConstrainTypes(projectspace)
    behaviour.setConstrainTypesMode(1)
    behaviour.setLocallyAllowedTypes(['strategicobjective', 'File', ])
    behaviour.setImmediatelyAddableTypes(['strategicobjective', 'File', ])
    transitions(projectspace, ['publish_internally'])


def _addPSTGroups(context):
    """
       Add groups of 'pst' application users...
    """
    if isNotCurrentProfile(context):
        return
    logger.info('Adding PST groups')
    site = context.getSite()
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
    # permissions for the contacts
    site.contacts.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))


def add_plonegroups_to_registry():
    registry = getUtility(IRegistry)
    to_add = []
    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'actioneditor']:
        to_add.append({'fct_title': u"Gestionnaire d'action", 'fct_id': u'actioneditor', 'fct_orgs': []})

    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'admin_resp']:
        to_add.append({'fct_title': u"Responsable administratif", 'fct_id': u'admin_resp', 'fct_orgs': []})

    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'editeur']:
        to_add.append({'fct_title': u'Éditeur (agent)', 'fct_id': u'editeur', 'fct_orgs': []})

    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'validateur']:
        to_add.append({'fct_title': u'Validateur (chef service)', 'fct_id': u'validateur', 'fct_orgs': []})

    if to_add:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + to_add


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
        frontpage.title = _("front_page_title")
        frontpage.description = _("front_page_descr")
        frontpage.text = richtextval(_("front_page_text"))
        #remove the presentation mode
        #frontpage.setPresentation(False)
        transitions(frontpage, ('retract', 'publish_internally'))
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

    # Set markup allowed types: for RichText field, don't display anymore types listbox
    adapter = MarkupControlPanelAdapter(site)
    adapter.set_allowed_types(['text/html'])

    # Activate browser message
    msg = site['messages-config']['browser-warning']
    try:
        # test if robotframework is there
        from robot import run  # NOQA
        run  # avoid pyflakes message
    except ImportError:
        api.content.transition(obj=msg, to_state='activated')

    #for collective.externaleditor
    registry = getUtility(IRegistry)
    registry['externaleditor.ext_editor'] = True
    if 'Image' in registry['externaleditor.externaleditor_enabled_types']:
        registry['externaleditor.externaleditor_enabled_types'] = ['PODTemplate', 'ConfigurablePODTemplate',
                                                                   'DashboardPODTemplate', 'SubTemplate',
                                                                   'StyleTemplate']

    #permissions
    #Removing owner to 'hide' sharing tab
    site.manage_permission('Sharing page: Delegate roles', ('Manager', 'Site Administrator'), acquire=0)
    #Hiding layout menu
    site.manage_permission('Modify view template', ('Manager', 'Site Administrator'), acquire=0)
    #List undo
    site.manage_permission('List undoable changes', ('Manager', 'Site Administrator'), acquire=0)
    #History: can revert to previous versions
    site.manage_permission('CMFEditions: Revert to previous versions', ('Manager', 'Site Administrator'), acquire=0)
    #Hiding folder contents
    site.manage_permission('List folder contents', ('Manager', 'Site Administrator'), acquire=0)

    paob = site.portal_actions.object_buttons
    for act in ('faceted.sync', 'faceted.disable', 'faceted.enable', 'faceted.search.disable',
                'faceted.search.enable', 'faceted.actions.disable', 'faceted.actions.enable'):
        if act in paob:
            paob[act].visible = False


def addDemoOrganization(context):
    """
        Add french demo data: own organization
    """
    if not context.readDataFile("imioprojectpst_demo_marker.txt"):
        return
    site = context.getSite()

    logger.info('Adding demo organizations')
    contacts = site.contacts
    contacts.exclude_from_nav = True
    contacts.reindexObject(['exclude_from_nav'])
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
         [u'bourgmestre', u'1er échevin', u'2ème échevin', u'3ème échevin',
          u'4ème échevin', u'5ème échevin', u'6ème échevin',
          u'7ème échevin', u'8ème échevin', u'9ème échevin', ]),
        (u'service', u'Services',
         [u'Accueil', u'Cabinet du Bourgmestre', u'ADL', u'Cellule Marchés Publics',
          u'Receveur Communal', u'Secrétariat Communal', u'Service de l\'Enseignement',
          u'Service Etat-civil', u'Service Finances', u'Service Informatique',
          u'Service du Personnel', u'Service Propreté', u'Service Population',
          u'Service Travaux', u'Service de l\'Urbanisme', ]),
    ]
    act_srv = [u'Cellule Marchés Publics', u'Secrétariat Communal', u'Service Etat-civil', u'Service Informatique',
               u'Service Propreté', u'Service Population', u'Service Travaux', u'Service de l\'Urbanisme']
    registry = getUtility(IRegistry)
    group_ids = []

    for (organization_type, department, services) in sublevels:
        dep = createContentInContainer(own_orga, 'organization',
                                       **{'title': department, 'organization_type': organization_type})
        for service in services:
            obj = createContentInContainer(dep, 'organization',
                                           **{'title': service, 'organization_type': u'service'})
            if service in act_srv and obj.UID() not in registry[ORGANIZATIONS_REGISTRY]:
                group_ids.append(obj.UID())
    if group_ids:
        registry[ORGANIZATIONS_REGISTRY] = registry[ORGANIZATIONS_REGISTRY] + group_ids
    # locally allowed types
    behaviour = ISelectableConstrainTypes(own_orga)
    behaviour.setConstrainTypesMode(1)
    behaviour.setLocallyAllowedTypes([])
    behaviour.setImmediatelyAddableTypes([])
    ISelectableConstrainTypes(own_orga['echevins']).setConstrainTypesMode(0)
    ISelectableConstrainTypes(own_orga['services']).setConstrainTypesMode(0)


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

    def getPSTStartYear(site):
        if getattr(site, '_TESTING_SITE_', False):
            return 2019
        else:
            return 2019

    logger.info('Adding demo data')
    registry = getUtility(IRegistry)
    registry[ORGANIZATIONS_REGISTRY]
    groups = {}
    for uid in registry[ORGANIZATIONS_REGISTRY]:
        service = uuidToObject(uid)
        groups[service.id] = uid

    # data has 4 levels :
    # - strategicobjective
    # - operationalobjective
    # - pstaction
    # - task
    data = get_os_oo_ac_data(groups, getPSTStartYear(site))

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

    for so_dict in data:
        strategicObj = createContentInContainer(pst, "strategicobjective", **so_dict)
        do_transitions(strategicObj, transitions=['begin'], logger=logger)
        for oo_dict in so_dict.get('operationalobjectives', []):
#            managers = oo_dict.pop('manager', '')
            operationalObj = createContentInContainer(strategicObj, "operationalobjective", **oo_dict)
            do_transitions(operationalObj, transitions=['begin'], logger=logger)
#            if managers:
#                _edit_fields(operationalObj, {'manager': managers})
            for act_dict in oo_dict.get('actions', []):
#                managers = action.pop('manager', '')
                action_obj = createContentInContainer(operationalObj, "pstaction", **act_dict)
                do_transitions(action_obj, transitions=['set_to_be_scheduled'], logger=logger)
#                if managers:
#                    _edit_fields(action_obj, {'manager': managers})
                for task_dict in act_dict.get('tasks', []):
                    task_obj = createContentInContainer(action_obj, "task", **task_dict)
                    do_transitions(task_obj, transitions=['do_to_assign'], logger=logger)

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
    if get_environment() == 'prod':
        password = generate_password()
        logger.info("Generated password='%s'" % password)
        site.plone_utils.addPortalMessage("Generated password='%s'" % password, type='warning')
    act_srv = [u'cellule-marches-publics', u'secretariat-communal', u'service-etat-civil', u'service-informatique',
               u'service-proprete', u'service-population', u'service-travaux', u'service-de-lurbanisme']
    srv_obj = site['contacts']['plonegroup-organization']['services']
    orgs = dict([(srv, srv_obj[srv].UID()) for srv in act_srv])
    users = {
        ('psteditor', u'PST editeur global'): ["pst_editors"],
        ('pstreader', u'PST lecteur global'): ["pst_readers"],
        ('chef', u'Michel Chef'): (['%s_%s' % (orgs[org], fct) for org in orgs for fct in ('admin_resp', 'validateur')]
                                   + ["pst_readers"]),
        ('agent', u'Fred Agent'): (['%s_%s' % (orgs[org], fct) for org in orgs for fct in ('actioneditor', 'editeur')]
                                   + ["pst_readers"]),
    }

    for uid, fullname in users.keys():
        try:
            member = site.portal_registration.addMember(id=uid, password=password)
            member.setMemberProperties({'fullname': fullname, 'email': 'test@macommune.be'})
            for gp in users[(uid, fullname)]:
                api.group.add_user(groupname=gp, username=uid)
        except ValueError, exc:
            if str(exc).startswith('The login name you selected is already in use'):
                continue
            logger("Error creating user '%s': %s" % (uid, exc))


COLUMNS_FOR_CONTENT_TYPES = {
    'strategicobjective': (u'select_row', u'pretty_link', u'review_state', u'categories', u'history_actions'),
    'operationalobjective': (u'select_row', u'pretty_link', u'parents', u'review_state', u'manager',
                             u'planned_end_date', u'priority', u'categories', u'history_actions'),
    'pstaction': (u'select_row', u'pretty_link', u'parents', u'review_state', u'manager', u'planned_begin_date',
                  u'planned_end_date', u'effective_begin_date', u'effective_end_date', u'progress',
                  u'health_indicator', u'history_actions'),
    'task': (u'select_row', u'pretty_link', u'parents', u'review_state', u'assigned_group',
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

    behaviour = ISelectableConstrainTypes(col_folder)
    behaviour.setConstrainTypesMode(1)
    behaviour.setLocallyAllowedTypes(['DashboardCollection'])
    behaviour.setImmediatelyAddableTypes(['DashboardCollection'])
    col_folder.exclude_from_nav = True
    alsoProvides(col_folder, ICollectionCategories)
    folder.portal_workflow.doActionFor(col_folder, "publish_internally")
    createBaseCollections(col_folder, content_type)
    createStateCollections(col_folder, content_type)
    # configure faceted
    configure_faceted_folder(
        col_folder, xml='{}.xml'.format(content_type[0]),
        default_UID=col_folder['all'].UID())
    return col_folder


def configureDashboard(pst):
    """Configure dashboard (add folders and collections)."""
    collection_folders = [
        # (folder id, folder title, content type for the collections)
        ('strategicobjectives', _("Strategic objectives"), ['strategicobjective'], IOSDashboardBatchActions),
        ('operationalobjectives', _("Operational objectives"), ['operationalobjective'], IOODashboardBatchActions),
        ('pstactions', _("Actions"), ['pstaction', 'pstsubaction'], IActionDashboardBatchActions),
        ('tasks', _("Tasks"), ['task'], ITaskDashboardBatchActions),
    ]
    for i, (name, title, content_type, inf) in enumerate(collection_folders):
        if name not in pst:
            folder = add_db_col_folder(pst, name, title, content_type, i, displayed='')
            alsoProvides(folder, inf)

    # configure faceted for container
    # default_UID = pst['strategicobjectives']['all'].UID()
    configure_faceted_folder(pst, xml='default_dashboard_widgets.xml', default_UID=None)


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

    for state in list_wf_states(folder, content_type[0]):
        col_id = "searchfor_%s" % state
        ps_path = '/'.join(getProjectSpace(folder).getPhysicalPath())
        if not base_hasattr(folder, col_id):
            folder.invokeFactory(
                "DashboardCollection",
                id=col_id,
                title=state_title_mapping[state],
                query=[
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': [state]},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                customViewFields=COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                tal_condition=conditions[content_type[0]].get(state),
                showNumberOfItems=(
                    state in showNumberOfItems.get(content_type[0], [])),
                roles_bypassing_talcondition=['Manager', 'Site Administrator'],
                sort_on=u'sortable_title',
                sort_reversed=True,
                b_size=30,
                limit=0,
                enabled=False)
            col = folder[col_id]
            col.setSubject((u'search', ))
            col.reindexObject(['Subject'])
            col.setLayout('tabular_view')


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
                                 limit=0,
                                 enabled=True)
            collection = folder[dic['id']]
            if 'subj' in dic:
                collection.setSubject(dic['subj'])
                collection.reindexObject(['Subject'])
            collection.setLayout('tabular_view')
        if folder.getObjectPosition(dic['id']) != i:
            folder.moveObjectToPosition(dic['id'], i)


def createBaseCollections(folder, content_type):
    ps_path = '/'.join(getProjectSpace(folder).getPhysicalPath())
    collections = [
        {
            'id': 'all',
            'tit': _('All'),
            'subj': (u'search', ),
            'query': [
                {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
            ],
            'cond': u"",
            'bypass': [],
            'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
            'sort': u'sortable_title',
            'rev': False,
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
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-administrative-responsible'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
            {
                'id': 'i-am-manager',
                'tit': _("Which I am manager"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-actioneditor'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
            {
                'id': 'action-deadline-has-passed',
                'tit': _("Which an action deadline has passed"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'has-child-action-deadline-has-passed'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
        ],

        'pstaction': [
            {
                'id': 'i-am-manager',
                'tit': _("Which I am manager"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-actioneditor'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
            {
                'id': 'deadline-has-passed',
                'tit': _("Which deadline has passed"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'planned_end_date', 'o': 'plone.app.querystring.operation.date.beforeToday'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
            {
                'id': 'beginning-is-late',
                'tit': _("Which beginning is late"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'planned_begin_date', 'o': 'plone.app.querystring.operation.date.beforeToday'},
                    {'i': 'effective_begin_date', 'o': 'plone.app.querystring.operation.date.afterToday'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
        ],

        'task': [
            {
                'id': 'to_assign',
                'tit': _('tasks_to_assign'),
                'subj': (u'todo', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['to_assign']},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'task-validation'}
                ],
                'cond': u"python:object.restrictedTraverse('pst-utils').user_has_review_level()",
                'bypass': ['Manager', 'Site Administrator'],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': True
            },
            {
                'id': 'to_treat',
                'tit': _('task_to_treat'),
                'subj': (u'todo', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'assigned_user', 'o': 'plone.app.querystring.operation.string.currentUser'},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['to_do']},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': True
            },
            {
                'id': 'im_treating',
                'tit': _('task_im_treating'),
                'subj': (u'todo', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'assigned_user', 'o': 'plone.app.querystring.operation.string.currentUser'},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['in_progress']},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': True
            },
            {
                'id': 'have_treated',
                'tit': _('task_have_treated'),
                'subj': (u'search', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'assigned_user', 'o': 'plone.app.querystring.operation.string.currentUser'},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is',
                     'v': ['closed', 'realized']},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
            {
                'id': 'in_my_group',
                'tit': _('tasks_in_my_group'),
                'subj': (u'search', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'task-in-assigned-group'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
            {
                'id': 'to_close',
                'tit': _('tasks_to_close'),
                'subj': (u'todo', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['realized']},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'task-validation'}
                ],
                'cond': u"python:object.restrictedTraverse('pst-utils').user_has_review_level()",
                'bypass': ['Manager', 'Site Administrator'],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': True
            },
            {
                'id': 'due_date_passed',
                'tit': _('tasks_with_due_date_passed'),
                'subj': (u'search', ),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['task']},
                    {'i': 'due_date', 'o': 'plone.app.querystring.operation.date.beforeToday'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
        ],

    }

    collections.extend(additional_collections_by_types[content_type[0]])
    createDashboardCollections(folder, collections)


def configure_rolefields(portal):
    """Configure the rolefields on types."""
    config = {
        ('projectspace', ): {
            'static_config': {
                'internally_published': {'pst_readers': {'roles': ['Reader']}}
            }
        },
        ('operationalobjective',): {
            'manager': {
                'achieved': {'actioneditor': {'roles': ['Contributor']}},
                'created': {'actioneditor': {'roles': ['Contributor']}},
                'ongoing': {'actioneditor': {'roles': ['Contributor']}},
            },
            'administrative_responsible': {
                'achieved': {'admin_resp': {'roles': ['Reader']}},
                'created': {'admin_resp': {'roles': ['Reader']}},
                'ongoing': {'admin_resp': {'roles': ['Reader']}}
            }
            # TODO: representative_responsible
        },
        ('pstaction', 'pstsubaction'): {
            'static_config': {
                'created': {'pst_editors': {'roles': ['Reader', 'Editor', 'Reviewer', 'Contributor']}},
                'to_be_scheduled': {'pst_editors': {'roles': ['Reader', 'Editor', 'Reviewer', 'Contributor']},
                                    'pst_readers': {'roles': ['Reader']}},
                'ongoing': {'pst_editors': {'roles': ['Reader', 'Editor', 'Reviewer', 'Contributor']},
                            'pst_readers': {'roles': ['Reader']}},
                'stopped': {'pst_editors': {'roles': ['Reader', 'Editor', 'Reviewer', 'Contributor']},
                            'pst_readers': {'roles': ['Reader']}},
                'terminated': {'pst_editors': {'roles': ['Reader', 'Editor', 'Reviewer', 'Contributor']},
                               'pst_readers': {'roles': ['Reader']}},
            },
            'manager': {
                'created': {'actioneditor': {'roles': ['Editor', 'Reviewer', 'Contributor']}},
                'to_be_scheduled': {'actioneditor': {'roles': ['Editor', 'Reviewer', 'Contributor']}},
                'ongoing': {'actioneditor': {'roles': ['Editor', 'Reviewer', 'Contributor']}},
                'terminated': {'actioneditor': {'roles': ['Editor', 'Reviewer']}},
                'stopped': {'actioneditor': {'roles': ['Editor', 'Reviewer']}},
            }
        },
    }
    for portal_types, roles_config in config.iteritems():
        for portal_type in portal_types:
            for keyname in roles_config:
                add_fti_configuration(portal_type, roles_config[keyname], keyname=keyname, force=False)


def configure_task_config(context):
    """
        Configure collective task
    """
    PARENTS_FIELDS_CONFIG = [
        {'fieldname': u'parents_assigned_groups', 'attribute': u'assigned_group', 'attribute_prefix': u'ITask',
         'provided_interface': u'collective.task.interfaces.ITaskContent'},
        {'fieldname': u'parents_enquirers', 'attribute': u'enquirer', 'attribute_prefix': u'ITask',
         'provided_interface': u'collective.task.interfaces.ITaskContent'},
        {'fieldname': u'parents_assigned_groups', 'attribute': u'manager', 'attribute_prefix': None,
         'provided_interface': u'imio.project.pst.content.action.IPSTAction'},
    ]
    registry = getUtility(IRegistry)
    logger.info("Configure registry")
    registry['collective.task.parents_fields'] = PARENTS_FIELDS_CONFIG


def configure_task_rolefields(portal, force=False):
    """
        Configure the rolefields on task
    """
    roles_config = {
        'static_config': {
            'created': {
                'pst_editors': {'roles': ['Contributor', 'Editor', 'Reviewer']},
            },
            'to_assign': {
                'pst_editors': {'roles': ['Contributor', 'Editor', 'Reviewer']},
            },
            'to_do': {
                'pst_editors': {'roles': ['Contributor', 'Editor', 'Reviewer']},
            },
            'in_progress': {
                'pst_editors': {'roles': ['Contributor', 'Editor', 'Reviewer']},
            },
            'realized': {
                'pst_editors': {'roles': ['Contributor', 'Editor', 'Reviewer']},
            },
            'closed': {
                'pst_editors': {'roles': ['Contributor', 'Editor', 'Reviewer']},
            },
        },
        'assigned_group': {
            'to_assign': {
                'validateur': {'roles': ['Contributor', 'Editor', 'Reviewer'],
                               'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
            },
            'to_do': {
                'editeur': {'roles': ['Contributor', 'Editor'],
                            'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
                'validateur': {'roles': ['Contributor', 'Editor', 'Reviewer'],
                               'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
            },
            'in_progress': {
                'editeur': {'roles': ['Contributor', 'Editor'],
                            'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
                'validateur': {'roles': ['Contributor', 'Editor', 'Reviewer'],
                               'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
            },
            'realized': {
                'editeur': {'roles': ['Contributor', 'Editor'],
                            'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
                'validateur': {'roles': ['Contributor', 'Editor', 'Reviewer'],
                               'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
            },
            'closed': {
                'editeur': {'roles': ['Reader'],
                            'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
                'validateur': {'roles': ['Editor', 'Reviewer'],
                               'rel': "{'collective.task.related_taskcontainer':['Reader']}"},
            },
        },
        'assigned_user': {
        },
        'enquirer': {
        },
        'parents_assigned_groups': {
            'created': {
                'actioneditor': {'roles': ['Reader']},
                'editeur': {'roles': ['Reader']},
                'validateur': {'roles': ['Reader']},
            },
            'to_assign': {
                'actioneditor': {'roles': ['Reader']},
                'editeur': {'roles': ['Reader']},
                'validateur': {'roles': ['Reader']},
            },
            'to_do': {
                'actioneditor': {'roles': ['Reader']},
                'editeur': {'roles': ['Reader']},
                'validateur': {'roles': ['Reader']},
            },
            'in_progress': {
                'actioneditor': {'roles': ['Reader']},
                'editeur': {'roles': ['Reader']},
                'validateur': {'roles': ['Reader']},
            },
            'realized': {
                'actioneditor': {'roles': ['Reader']},
                'editeur': {'roles': ['Reader']},
                'validateur': {'roles': ['Reader']},
            },
            'closed': {
                'actioneditor': {'roles': ['Reader']},
                'editeur': {'roles': ['Reader']},
                'validateur': {'roles': ['Reader']},
            },
        },
        'parents_enquirers': {
        },
    }

        # we overwrite existing configuration from task installation !
    if (base_hasattr(portal.portal_types.task, 'localroles') and
            portal.portal_types.task.localroles.get('assigned_group', '') and
            portal.portal_types.task.localroles['assigned_group'].get('created') and
            '' in portal.portal_types.task.localroles['assigned_group']['created']):
        force = True

    for keyname in roles_config:
        logger.info("Setting task local roles configuration for '%s' with force=%s" % (keyname, force))
        msg = add_fti_configuration('task', roles_config[keyname], keyname=keyname, force=force)
        if msg:
            logger.warn(msg)


def configure_actions_panel(portal):
    """
        Configure actions panel registry
    """
    logger.info('Configure actions panel registry')
    registry = getUtility(IRegistry)

    if not registry.get('imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions'):
        registry['imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions'] = \
            ['strategicobjective.back_to_created|', 'strategicobjective.back_to_ongoing|',
             'operationalobjective.back_to_created|', 'operationalobjective.back_to_ongoing|',
             'pstaction.back_to_created|', 'pstaction.back_to_ongoing|',
             'pstaction.back_to_be_scheduled|', 'task.back_in_created|', 'task.back_in_to_assign|',
             'task.back_in_to_do|', 'task.back_in_progress|', 'task.back_in_realized|', ]


def configure_wsclient(context):
    """ Configure wsclient """
    if context.readDataFile("imioprojectpst_update_marker.txt") is None:
        return
    site = context.getSite()
    logger.info('Configure wsclient step')
    log = ['Installing imio.pm.wsclient']
    site.portal_setup.runAllImportStepsFromProfile('profile-imio.pm.wsclient:default')

    log.append('Defining settings')
    prefix = 'imio.pm.wsclient.browser.settings.IWS4PMClientSettings'
    if not api.portal.get_registry_record('{}.pm_url'.format(prefix), default=False):
        pmurl = psturl = os.getenv('PUBLIC_URL', '')
        pmurl = pmurl.replace('-prj', '-pm')
        if pmurl != psturl:
            api.portal.set_registry_record('{}.pm_url'.format(prefix), u'{}/ws4pm.wsdl'.format(pmurl))
        api.portal.set_registry_record('{}.pm_username'.format(prefix), u'admin')
        pmpass = os.getenv('PM_PASS', '')
        if pmpass:
            api.portal.set_registry_record('{}.pm_password'.format(prefix), pmpass)
        api.portal.set_registry_record('{}.only_one_sending'.format(prefix), False)
        from imio.pm.wsclient.browser.vocabularies import pm_item_data_vocabulary
        orig_call = pm_item_data_vocabulary.__call__
        pm_item_data_vocabulary.__call__ = lambda self, context: SimpleVocabulary([SimpleTerm(u'title'),
                                                                                   SimpleTerm(u'description'),
                                                                                   SimpleTerm(u'detailedDescription')])
        api.portal.set_registry_record('{}.field_mappings'.format(prefix),
                                       [{'field_name': u'title', 'expression': u'context/Title'},
                                        {'field_name': u'description',
                                         'expression': u'context/@@ProjectWSClient/description'},
                                        {'field_name': u'detailedDescription',
                                         'expression': u'context/@@ProjectWSClient/detailed_description'}])
        # u'string: ${context/@@ProjectWSClient/description}<br />${context/@@ProjectWSClient/detailed_description}'
        pm_item_data_vocabulary.__call__ = orig_call
        #api.portal.set_registry_record('{}.user_mappings'.format(prefix),
        #                               [{'local_userid': u'admin', 'pm_userid': u'dgen'}])
        from imio.pm.wsclient.browser.vocabularies import pm_meeting_config_id_vocabulary
        orig_call = pm_meeting_config_id_vocabulary.__call__
        pm_meeting_config_id_vocabulary.__call__ = lambda self, context: SimpleVocabulary(
            [SimpleTerm(u'meeting-config-college')])
        from imio.pm.wsclient.browser.settings import notify_configuration_changed
        from plone.registry.interfaces import IRecordModifiedEvent
        gsm = getGlobalSiteManager()
        gsm.unregisterHandler(notify_configuration_changed, (IRecordModifiedEvent, ))
        api.portal.set_registry_record('{}.generated_actions'.format(prefix),
                                       [{'pm_meeting_config_id': u'meeting-config-college',
                                         'condition': u"python: context.getPortalTypeName() in ('pstaction', 'task',"
                                                      u"'pstsubaction')",
                                         'permissions': 'Modify view template'}])
        pm_meeting_config_id_vocabulary.__call__ = orig_call
        gsm.registerHandler(notify_configuration_changed, (IRecordModifiedEvent, ))
    [logger.info(msg) for msg in log]
    return '\n'.join(log)


def configure_lasting_objectives(context):
    """
        Configure lasting objectives
    """

    LASTING_OBJECTIVES_CONFIG = {
        # u'obj01': {u'title': u'', u'url': u''},
        # u'obj02': {u'title': u'', u'url': u''},
        # u'obj03': {u'title': u'', u'url': u''},
    }
    registry = getUtility(IRegistry)
    logger.info("Configure registry (lasting objectives)")
    registry['imio.project.core.lasting_objectives'] = LASTING_OBJECTIVES_CONFIG


def set_portlet(obj):
    ann = IAnnotations(obj)
    portlet = ann['plone.portlets.contextassignments']['plone.leftcolumn']['portlet_actions']
    portlet.category = u'portlet'
    portlet._p_changed = True
