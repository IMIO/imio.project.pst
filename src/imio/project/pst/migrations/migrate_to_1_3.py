# -*- coding: utf-8 -*-

from collective.documentgenerator.utils import update_oo_config
from collective.messagesviewlet.utils import add_message
from dexterity.localroles.utils import add_fti_configuration
from imio.actionspanel.interfaces import IFolderContentsShowableMarker
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import _tr
from imio.project.pst.setuphandlers import configure_pst
from imio.project.pst.setuphandlers import createBaseCollections
from imio.project.pst.setuphandlers import reimport_faceted_config
from imio.project.pst.setuphandlers import set_portlet
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.events import RecordModifiedEvent
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from Products.CPUtils.Extensions.utils import mark_last_version
from zope import event
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.lifecycleevent import modified
from zope.schema.interfaces import IVocabularyFactory

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):

        # check if oo port must be changed
        update_oo_config()

        self.check_roles()
        self.remove_simplify_layout()

        self.install(['collective.portlet.actions'])
        self.install(['collective.behavior.sdg'])
        self.install(['collective.z3cform.chosen'])
        self.upgradeProfile('collective.contact.core:default')

        self.runProfileSteps('imio.project.core', steps=['controlpanel', 'plone.app.registry', 'typeinfo'],
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog', 'componentregistry', 'controlpanel',
                                                        'plone.app.registry', 'portlets', 'typeinfo', 'viewlets',
                                                        'workflow'],
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['portlets', 'repositorytool'], profile='demo',
                             run_dependencies=False)

        # to hide messages-viewlet
        self.runProfileSteps('plonetheme.imioapps', steps=['viewlets'], run_dependencies=False)

        self.correct_component_registry()

        self.various_update()

        set_portlet(self.portal)

        configure_pst(self.portal)

        self.adapt_collections()

        self.migrate_representative_responsible()

        self.update_collections_folder_name()

        self.set_priority()

        self.adapt_templates()

        self.migrate_pstactions()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update',
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default',
                             run_dependencies=False)

        self.runProfileSteps('imio.project.core', steps=['plone.app.registry'], profile='default',
                             run_dependencies=False)

        self.dx_local_roles()

        self.upgradeAll(omit=['imio.project.pst:default'])

        for prod in ['collective.compoundcriterion', 'collective.contact.plonegroup', 'collective.contact.widget',
                     'collective.eeafaceted.batchactions', 'collective.eeafaceted.collectionwidget',
                     'collective.eeafaceted.dashboard', 'collective.eeafaceted.z3ctable', 'communesplone.layout',
                     'dexterity.localroles', 'dexterity.localrolesfield', 'imio.actionspanel', 'imio.dashboard',
                     'imio.pm.wsclient', 'imio.project.core', 'imio.project.pst', 'plone.formwidget.datetime',
                     'plonetheme.classic', 'plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'], run_dependencies=False)

        # Display duration
        self.finish()

    def various_update(self):
        # doc message
        for id in ('doc1-0', 'doc'):
            if id in self.portal['messages-config']:
                api.content.delete(self.portal['messages-config'][id])
        if ('indispo' in self.portal['messages-config'] and
                api.content.get_state(self.portal['messages-config']['indispo']) == 'activated'):
            api.content.transition(self.portal['messages-config']['indispo'], 'deactivate')
        if 'doc' not in self.portal['messages-config']:
            add_message('doc', 'Documentation', u'<p>Vous pouvez consulter la '
                        u'<a href="https://docs.imio.be/imio-doc/ia.pst" target="_blank">documentation en ligne de la '
                        u'dernière version</a>, ainsi que d\'autres documentations liées.</p>', msg_type='significant',
                        can_hide=True, req_roles=['Authenticated'], activate=True)
        # replace front-page
        frontpage = getattr(self.portal, 'front-page')
        frontpage.title = _tr("front_page_title")
        frontpage.description = _tr("front_page_descr")
        frontpage.text = richtextval(_tr("front_page_text"))
        transitions(frontpage, ('retract', 'publish_internally'))
        frontpage.reindexObject()
        # remove portlets on pst
        for brain in self.catalog(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            ann = IAnnotations(brain.getObject())
            if 'plone.portlets.contextassignments' in ann:
                if 'plone.leftcolumn' in ann['plone.portlets.contextassignments']:
                    for name in ('portlet_dashboard', 'navigation', 'portlet_actions'):
                        if name in ann['plone.portlets.contextassignments']['plone.leftcolumn']:
                            del ann['plone.portlets.contextassignments']['plone.leftcolumn'][name]
                    if not len(ann['plone.portlets.contextassignments']['plone.leftcolumn']):
                        del ann['plone.portlets.contextassignments']['plone.leftcolumn']
                if not len(ann['plone.portlets.contextassignments']):
                    del ann['plone.portlets.contextassignments']
        # registry
        api.portal.set_registry_record('collective.contact.core.interfaces.IContactCoreParameters.'
                                       'display_below_content_title_on_views', True)
        registry = getUtility(IRegistry)
        record = registry.records.get('imio.pm.wsclient.browser.settings.IWS4PMClientSettings.generated_actions')
        if record is not None:
            val = api.portal.get_registry_record('imio.pm.wsclient.browser.settings.IWS4PMClientSettings.'
                                                 'generated_actions')
            event.notify(RecordModifiedEvent(record, val, val))
        # update dashboard criterias
        for brain in self.catalog(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            pst = brain.getObject()
            mapping = {
                'strategicobjectives': 'strategicobjective',
                'operationalobjectives': 'operationalobjective',
                'pstactions': 'pstaction',
                'tasks': 'task'
            }
            for col_folder_id, content_type in mapping.iteritems():
                col_folder = pst[col_folder_id]
                reimport_faceted_config(col_folder, xml='{}.xml'.format(content_type),
                                        default_UID=col_folder['all'].UID())
        # rename pst
        titles = {u'PST (2012-2018)': u'PST 2013-2018', u'PST (2018-2024)': u'PST 2019-2024',
                  u'PST (2019-2024)': u'PST 2019-2024'}
        values = titles.values()
        for brain in self.catalog(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            pst = brain.getObject()
            for tit in titles:
                if pst.title == tit:
                    pst.title = titles[tit]
                    modified(pst)
                    break
            else:
                if pst.title not in values:
                    logger.warning("PST rename: not replaced '{}'".format(pst.title))

    def update_collections_folder_name(self):
        """ Update Actions and Tasks folder name """
        elts = [("imio.project.pst.interfaces.IActionDashboardBatchActions", "Actions under"),
                ("imio.project.pst.interfaces.ITaskDashboardBatchActions", "Tasks under")]
        for elt in elts:
            brains = self.catalog(portal_type="Folder", object_provides=elt[0])
            for brain in brains:
                obj = brain.getObject()
                obj.title = _tr(elt[1])
                obj.reindexObject()

    def set_priority(self):
        """  """
        brains = self.catalog(object_provides="imio.project.pst.interfaces.IImioPSTProject")
        for brain in brains:
            obj = brain.getObject()
            if obj.priority[0]['key'] == '':
                obj.priority[0]['key'] = u'0'
                obj.reindexObject()

        brains = self.catalog(object_provides="imio.project.pst.content.operational.IOperationalObjective")
        for brain in brains:
            if brain.priority == []:
                obj = brain.getObject()
                obj.priority = u'0'
                obj.reindexObject()

    def adapt_templates(self):
        """ Include pstsubactions in templates definition """
        templates = self.portal.templates

        # Use reusable functionality
        for id in ('detail', 'follow', 'export'):
            templates[id].is_reusable = True
        for id in ('ddetail', 'ddetail-all', 'ddetail-tasks', 'ddetail-tasks-all', 'detail-all', 'detail-tasks',
                   'detail-tasks-all'):
            templates[id].pod_template_to_use = templates['detail'].UID()
            templates[id].odt_file = None
        for id in ('follow-all', 'follow-tasks', 'follow-tasks-all'):
            templates[id].pod_template_to_use = templates['follow'].UID()
            templates[id].odt_file = None
        templates['dexport'].pod_template_to_use = templates['export'].UID()
        templates['dexport'].odt_file = None

        # Reorder
        for id in reversed(['style', 'detail', 'detail-tasks', 'follow', 'follow-tasks', 'export', 'detail-all',
                            'detail-tasks-all', 'ddetail', 'ddetail-tasks', 'dfollow', 'dfollow-tasks', 'dexport',
                            'ddetail-all', 'ddetail-tasks-all', 'follow-all', 'follow-tasks-all', 'dfollow-all',
                            'dfollow-tasks-all']):
            templates.moveObjectToPosition(id, 0)

        # Adapt portal types and conditions for pstsubaction
        for id in ('detail', 'detail-tasks', 'follow', 'follow-tasks', 'export', 'detail-all', 'detail-tasks-all',
                   'follow-all', 'follow-tasks-all'):
            templates[id].pod_portal_types.append('pstsubaction')

        for id in ('ddetail', 'dfollow'):
            templates[id].tal_condition = "python:" \
                "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or " \
                "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or " \
                "context.getPortalTypeName() == 'pstsubaction')"

        for id in ('ddetail-all', 'dfollow-all'):
            templates[id].tal_condition = "python:" \
                "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors']) and " \
                "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or " \
                "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or " \
                "context.getPortalTypeName() == 'pstsubaction')"

        templates['dexport'].tal_condition = "python:" \
            "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or " \
            "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or " \
            "context.getPortalTypeName() == 'pstsubaction') and " \
            "context.restrictedTraverse('pst-utils')"

    def adapt_collections(self):
        """ various collections modifications """

        # deactivate states collections to lighten menu
        # add ModificationDate column
        # correct query containing list of instance object in old sites : must be list of dict
        for brain in self.catalog(portal_type='DashboardCollection'):
            col = brain.getObject()
            new_query = []
            for parameter in col.query:
                if isinstance(parameter, dict):
                    new_query.append(parameter)
                else:
                    dic = {'i': parameter['i'], 'o': parameter['o']}
                    if parameter.get('v'):
                        dic['v'] = parameter['v']
                    new_query.append(dic)
            col.query = new_query
            if brain.id.startswith('searchfor_') and col.enabled:
                col.enabled = False
                col.reindexObject(idxs=['enabled'])
            if u'ModificationDate' not in col.customViewFields:
                nl = list(col.customViewFields)
                nl.insert(col.customViewFields.index(u'history_actions'), u'ModificationDate')
                col.customViewFields = tuple(nl)

        # Add subactions in actions collections
        pstactions = self.catalog(portal_type="Folder",
                                  object_provides="imio.project.pst.interfaces.IActionDashboardBatchActions")
        for pstaction in pstactions:
            for brain in self.catalog.searchResults({'path': {'query': pstaction.getPath()},
                                                     'portal_type': 'DashboardCollection'}):
                col = brain.getObject()
                for parameter in col.query:
                    if parameter['i'] == 'portal_type':
                        parameter['v'] = [u'pstaction', u'pstsubaction']
                col.query = list(col.query)  # need this to persist change
                if u'responsible' not in col.customViewFields:
                    nl = list(col.customViewFields)
                    nl.insert(col.customViewFields.index(u'manager') + 1, u'responsible')
                    col.customViewFields = tuple(nl)
            # add new collection
            createBaseCollections(pstaction.getObject(), ['pstaction', 'pstsubaction'])

        # add sdgs column on oo and act dashboardes
        dbs = self.catalog(portal_type="Folder",
                           object_provides="imio.project.pst.interfaces.IOODashboardBatchActions") + pstactions
        for db in dbs:
            for brain in self.catalog.searchResults({'path': {'query': db.getPath()},
                                                     'portal_type': 'DashboardCollection'}):
                col = brain.getObject()
                if u'sdgs' not in col.customViewFields:
                    nl = list(col.customViewFields)
                    nl.insert(col.customViewFields.index(u'ModificationDate'), u'sdgs')
                    col.customViewFields = tuple(nl)

        # add tasks collections removed on gembloux
        tasks_f = self.catalog(portal_type="Folder",
                               object_provides="imio.project.pst.interfaces.ITaskDashboardBatchActions")
        for task_f in tasks_f:
            createBaseCollections(task_f.getObject(), ['task'])

    def dx_local_roles(self):
        # add pstsubaction local roles
        conf = {
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
        }
        for keyname in conf:
            add_fti_configuration('pstsubaction', conf[keyname], keyname=keyname, force=False)
        # add administrative_responsible
        fti = getUtility(IDexterityFTI, name='operationalobjective')
        lr = getattr(fti, 'localroles')
        lrar = lr['administrative_responsible']
        for state in ('ongoing',):
            if state in lrar and 'admin_resp' in lrar[state]:
                dic = lrar[state]['admin_resp']
                roles = dic.setdefault('roles', {'roles': ['Reader']})
                for role in ('Editor', 'Contributor'):
                    if role not in roles:
                        roles.append(role)
        lr._p_changed = True

    def check_roles(self):
        # check user roles
        for user in api.user.get_users():
            roles = api.user.get_roles(user=user)
            for role in roles:
                if role in ['Member', 'Authenticated']:
                    continue
                elif role == 'Manager':
                    self.portal.acl_users.source_groups.addPrincipalToGroup(user.id, 'Administrators')
                    api.user.revoke_roles(user=user, roles=['Manager'])
                elif role == 'Site Administrator':
                    self.portal.acl_users.source_groups.addPrincipalToGroup(user.id, 'Site Administrators')
                    api.user.revoke_roles(user=user, roles=['Site Administrator'])
                else:
                    logger.warn("User '{}' has role: {}".format(user.id, role))
        # check group roles
        for group in api.group.get_groups():
            roles = api.group.get_roles(group=group)
            for role in roles:
                if (role == 'Authenticated' or (role == 'Manager' and group.id == 'Administrators') or
                        (role == 'Site Administrator' and group.id == 'Site Administrators') or
                        (role == 'Reviewer' and group.id == 'Reviewers')):
                    continue
                else:
                    logger.warn("Group '{}' has role: {}".format(group.id, role))

    def remove_simplify_layout(self):
        # useless communesplone.layout setup
        group_id = "full-layout"
        if group_id in [g.id for g in api.group.get_groups()]:
            api.group.delete(groupname=group_id)
        self.portal.manage_permission('Review portal content', ('Manager', 'Site Administrator', 'Reviewer'), acquire=1)
        self.portal.manage_permission('Modify constrain types', (), acquire=1)
        self.portal.manage_permission('CMFPlacefulWorkflow: Manage workflow policies', (), acquire=1)
        # css is removed in cssregistry of default profile
        # skins is removed via update profile
        self.runProfileSteps('imio.project.pst', steps=['skins'], profile='update', run_dependencies=False)
        if 'communesplone_layout_simplify' in self.portal.portal_skins:
            api.content.delete(self.portal.portal_skins['communesplone_layout_simplify'])

    def migrate_representative_responsible(self):
        # construct correspondence
        terms = {}
        sub = self.portal.contacts['plonegroup-organization'].echevins
        #if IFolderContentsShowableMarker.providedBy(sub):
        #    return
        alsoProvides(sub, IFolderContentsShowableMarker)
        sub_path = '/'.join(sub.getPhysicalPath())
        sub_path_len = len(sub_path) + 1
        crit = {'path': {"query": sub_path, 'depth': 10}, 'portal_type': "organization",
                'sort_on': 'getObjPositionInParent'}
        brains = self.catalog(**crit)
        levels = {}
        for brain in brains:
            path = brain.getPath()[sub_path_len:]
            if not path:
                continue  # organization_id itself
            value = safe_unicode(brain.id)
            level = len(path.split('/'))
            levels[level] = {'id': value}
            if level > 1:
                value = u'{}-{}'.format(levels[level-1]['id'], value)
            terms[value] = brain.UID
        uids = {v: k for k, v in terms.items()}
        # find existing values and replace by new ones (id -> uid)
        for brain in self.catalog(portal_type=['operationalobjective', 'pstaction']):
            obj = brain.getObject()
            new_val = []
            for rr in (obj.representative_responsible or []):
                if rr in terms:
                    new_val.append(terms[rr])
                elif rr not in uids:  # if migration already done
                    logger.error("'{}' not found in dic {}. Used in {}".format(rr, terms, brain.getURL()))
                    raise Exception("'{}' not found in dic {}. Used in {}".format(rr, terms, brain.getURL()))
            if new_val:
                obj.representative_responsible = new_val
                obj.reindexObject()

    def migrate_pstactions(self):
        for brain in self.catalog(portal_type=['pstaction', 'pstsubaction']):
            obj = brain.getObject()
            obj.reindexObject()

    def correct_component_registry(self):
        """ There is still a trace of imio.project.pst.content.operational.ManagerVocabulary. """
        sm = self.portal.getSiteManager()
        subscribers = sm.utilities._subscribers
        utilities = subscribers[0][IVocabularyFactory]
        from imio.project.pst.content.operational import ManagerVocabulary
        new_tup = tuple([obj for obj in utilities[u''] if not isinstance(obj, ManagerVocabulary)])
        if utilities[u''] != new_tup:
            subscribers[0][IVocabularyFactory][u''] = new_tup
            setattr(sm.utilities, '_subscribers', subscribers)


def migrate(context):
    Migrate_To_1_3(context).run()
