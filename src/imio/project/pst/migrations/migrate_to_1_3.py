# -*- coding: utf-8 -*-

from collective.documentgenerator.utils import update_oo_config
from collective.messagesviewlet.utils import add_message
from dexterity.localroles.utils import add_fti_configuration
from imio.actionspanel.interfaces import IFolderContentsShowableMarker
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import _tr
from imio.project.pst import CKEDITOR_MENUSTYLES_CUSTOMIZED_MSG
from imio.project.pst.setuphandlers import configure_pst
from imio.project.pst.setuphandlers import createBaseCollections
from imio.project.pst.setuphandlers import reimport_faceted_config
from imio.project.pst.setuphandlers import set_portlet
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.events import RecordModifiedEvent
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.CPUtils.Extensions.utils import change_user_properties
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
        self.upgradeProfile('collective.documentgenerator:default')

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

        self.migrate_description()

        self.adapt_collections()

        self.migrate_representative_responsible()

        self.update_collections_folder_name()

        self.set_priority()

        self.adapt_templates()

        self.migrate_pstactions()

        self.add_missing_attributes()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-override-templates'], profile='update',
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default',
                             run_dependencies=False)

        self.runProfileSteps('imio.project.core', steps=['plone.app.registry'], profile='default',
                             run_dependencies=False)

        self.dx_local_roles()

        self.upgradeAll(omit=['imio.project.pst:default'])

        for prod in ['collective.behavior.talcondition', 'collective.ckeditor', 'collective.compoundcriterion',
                     'collective.contact.plonegroup', 'collective.contact.widget', 'collective.eeafaceted.batchactions',
                     'collective.eeafaceted.collectionwidget', 'collective.eeafaceted.dashboard',
                     'collective.eeafaceted.z3ctable', 'collective.fingerpointing', 'collective.messagesviewlet',
                     'communesplone.layout', 'dexterity.localroles', 'dexterity.localrolesfield', 'eea.jquery',
                     'imio.actionspanel', 'imio.dashboard', 'imio.history', 'imio.pm.wsclient', 'imio.project.core',
                     'imio.project.pst', 'plone.formwidget.datetime', 'plone.formwidget.masterselect',
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
                        u'<a href="https://docs.imio.be/imio-doc/ia.pst/" target="_blank">documentation en ligne de la '
                        u'dernière version</a>, ainsi que <a href="https://www.imio.be/nos-applications/ia-pst/'
                        u'les-actus-de-pst/ia-pst-1-3" target="_blank">les nouveautés</a>.</p>', msg_type='significant',
                        can_hide=True, req_roles=['Authenticated'], activate=True)
        # activate user external edit pref
        change_user_properties(self.portal, kw='ext_editor:True', dochange='1')
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
            if val is not None:
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
                  u'PST (2019-2024)': u'PST 2019-2024', u'PST': u'PST 2019-2024'}
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
        # update ckeditor to remove format and avoid html <h> tags
        cke_props = self.portal.portal_properties.ckeditor_properties
        custom = (u"[\n['AjaxSave'],\n['Cut','Copy','Paste','PasteText','PasteFromWord','-',"
                  u"'Scayt'],\n['Undo','Redo','-','RemoveFormat'],\n['Bold','Italic','Underline','Strike'],\n"
                  u"['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],\n['JustifyLeft',"
                  u"'JustifyCenter', 'JustifyRight','JustifyBlock'],\n['Table','SpecialChar','Link','Unlink'],\n'/',"
                  u"\n['Styles'],\n['Maximize', 'ShowBlocks', 'Source']\n]")
        cke_props.toolbar_Custom = custom
        if cke_props.menuStyles.find(CKEDITOR_MENUSTYLES_CUSTOMIZED_MSG) == -1:
            enc = self.portal.portal_properties.site_properties.getProperty('default_charset')
            msg_highlight_red = _tr('ckeditor_style_highlight_in_red').encode('utf-8')
            msg_highlight_blue = _tr('ckeditor_style_highlight_in_blue').encode('utf-8')
            msg_highlight_green = _tr('ckeditor_style_highlight_in_green').encode('utf-8')
            msg_highlight_yellow = _tr('ckeditor_style_highlight_in_yellow').encode('utf-8')
            msg_x_small = _tr('ckeditor_style_x_small').encode('utf-8')
            msg_small = _tr('ckeditor_style_small').encode('utf-8')
            msg_large = _tr('ckeditor_style_large').encode('utf-8')
            msg_x_large = _tr('ckeditor_style_x_large').encode('utf-8')
            msg_indent = _tr('ckeditor_style_indent_first_line').encode('utf-8')
            msg_table_no_optimization = _tr('ckeditor_style_table_no_optimization').encode('utf-8')

            menuStyles = unicode(
                "[\n{0}\n{{ name : '{1}'\t\t, element : 'span', attributes : {{ 'class' : 'highlight-red' }} }},\n"
                "{{ name : '{2}'\t\t, element : 'span', attributes : {{ 'class' : 'highlight-blue' }} }},\n"
                "{{ name : '{3}'\t\t, element : 'span', attributes : {{ 'class' : 'highlight-green' }} }},\n"
                "{{ name : '{4}'\t\t, element : 'span', attributes : {{ 'class' : 'highlight-yellow' }} }},\n"
                "{{ name : '{5}'\t\t, element : 'p', attributes : {{ 'class' : 'xSmallText' }} }},\n"
                "{{ name : '{6}'\t\t, element : 'p', attributes : {{ 'class' : 'smallText' }} }},\n"
                "{{ name : '{7}'\t\t, element : 'p', attributes : {{ 'class' : 'largeText' }} }},\n"
                "{{ name : '{8}'\t\t, element : 'p', attributes : {{ 'class' : 'xLargeText' }} }},\n"
                "{{ name : '{9}'\t\t, element : 'table', styles : {{ 'table-layout' : 'fixed' }} }},\n"
                "{{ name : '{10}'\t\t, element : 'p', attributes : {{ 'style' : 'text-indent: 40px;' }} }},\n]\n".
                format(CKEDITOR_MENUSTYLES_CUSTOMIZED_MSG,
                       msg_highlight_red, msg_highlight_blue, msg_highlight_green, msg_highlight_yellow,
                       msg_x_small, msg_small, msg_large, msg_x_large,
                       msg_table_no_optimization, msg_indent), enc)
            cke_props.menuStyles = menuStyles

    def migrate_description(self):
        """ Migrate description field to description_rich """
        for brain in self.catalog(object_provides='imio.project.core.content.project.IProject'):
            obj = brain.getObject()
            # old description contains something like : u'ligne1\r\nligne2\r\nligne3'
            if obj.description:
                new_val = []
                for line in obj.description.split('\r\n'):
                    new_val.append(line)
                obj.description_rich = richtextval(u'<p>{}</p>'.format(u'<br />'.join(new_val),
                                                   outputMimeType='text/x-html-safe'))
                obj.description = u''
                obj.reindexObject()

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
            templates[id].style_modification_md5 = templates[id].initial_md5 = u''
        for id in ('follow-all', 'follow-tasks', 'follow-tasks-all'):
            templates[id].pod_template_to_use = templates['follow'].UID()
            templates[id].odt_file = None
            templates[id].style_modification_md5 = templates[id].initial_md5 = u''
        templates['dexport'].pod_template_to_use = templates['export'].UID()
        templates['dexport'].odt_file = None
        templates['dexport'].style_modification_md5 = templates['dexport'].initial_md5 = u''

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

    def add_missing_attributes(self):
        config = {
            'operationalobjective': [('categories', [])],
            'pstaction': [('categories', [])],
            'pstsubaction': [('categories', [])],
        }
        for typ in config:
            for brain in self.catalog(portal_type=typ):
                obj = brain.getObject()
                for attr, value in config[typ]:
                    if not base_hasattr(obj, attr):
                        setattr(obj, attr, type(value)(value))  # make new object of same type to avoid storing same obj
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
