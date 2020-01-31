# -*- coding: utf-8 -*-

from collective.documentgenerator.utils import update_oo_config
from dexterity.localroles.utils import add_fti_configuration
from imio.actionspanel.interfaces import IFolderContentsShowableMarker
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import _tr
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
from zope.component import queryUtility
from zope.interface import alsoProvides

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

        self.runProfileSteps('imio.project.core', steps=['typeinfo'], run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog', 'componentregistry', 'portlets',
                                                        'typeinfo', 'viewlets', 'workflow'],
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['portlets', 'repositorytool'], profile='demo',
                             run_dependencies=False)

        self.various_update()

        set_portlet(self.portal)

        self.adapt_collections()

        self.migrate_representative_responsible()

        self.update_collections_folder_name()

        self.set_priority()

        self.adapt_templates()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update',
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default',
                             run_dependencies=False)

        self.runProfileSteps('imio.project.core', steps=['plone.app.registry'], profile='default',
                             run_dependencies=False)

        self.dx_local_roles()

        self.upgradeAll(omit=['imio.project.pst:default'])

        for prod in ['plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'], run_dependencies=False)

        # Display duration
        self.finish()

    def various_update(self):
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
        """ Include pstsubactions in templates denifition """
        templates = self.portal.templates
        for id in ('detail', 'detail-tasks', 'follow', 'follow-tasks', 'export', 'detail-all', 'detail-tasks-all',
                   'follow-all', 'follow-tasks-all'):
            templates[id].pod_portal_types.append('pstsubaction')

    def adapt_collections(self):
        """ Include subactions in existing action dashboard collections """
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
        # deactivate states collections to lighten menu
        # add ModificationDate column
        for brain in self.catalog(portal_type='DashboardCollection'):
            col = brain.getObject()
            if brain.id.startswith('searchfor_') and col.enabled:
                col.enabled = False
                col.reindexObject(idxs=['enabled'])
            if u'ModificationDate' not in col.customViewFields:
                nl = list(col.customViewFields)
                nl.insert(col.customViewFields.index(u'history_actions'), u'ModificationDate')
                col.customViewFields = tuple(nl)
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
        if IFolderContentsShowableMarker.providedBy(sub):
            return
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
        # find existing values and replace by new ones (id -> uid)
        for brain in self.catalog(portal_type=['operationalobjective', 'pstaction']):
            obj = brain.getObject()
            new_val = []
            for rr in (obj.representative_responsible or []):
                if rr in terms:
                    new_val.append(terms[rr])
                else:
                    logger.error("'{}' not found in dic {}. Used in {}".format(rr, terms, brain.getURL()))
                    raise Exception("'{}' not found in dic {}. Used in {}".format(rr, terms, brain.getURL()))
            if new_val:
                obj.representative_responsible = new_val
                obj.reindexObject()


def migrate(context):
    Migrate_To_1_3(context).run()
