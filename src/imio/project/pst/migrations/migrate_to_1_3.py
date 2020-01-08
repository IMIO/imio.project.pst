# -*- coding: utf-8 -*-

from collective.documentgenerator.utils import update_oo_config
from dexterity.localroles.utils import add_fti_configuration
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import _tr
from imio.project.pst.setuphandlers import configure_lasting_objectives
from imio.project.pst.setuphandlers import set_portlet
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from Products.CPUtils.Extensions.utils import mark_last_version
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog
        self.ps = self.portal.portal_setup

    def run(self):

        # check if oo port must be changed
        update_oo_config()

        self.install(['collective.portlet.actions'])
        self.upgradeProfile('collective.contact.core:default')

        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog', 'componentregistry', 'portlets',
                                                        'typeinfo', 'viewlets', 'workflow'],
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['portlets', 'repositorytool'], profile='demo',
                             run_dependencies=False)

        self.various_update()

        set_portlet(self.portal)

        self.adapt_collections()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update',
                             run_dependencies=False)
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default',
                             run_dependencies=False)

        self.runProfileSteps('imio.project.core', steps=['plone.app.registry'], profile='default',
                             run_dependencies=False)

        configure_lasting_objectives(self.context)

        self.install_analytic_budget_behavior()

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

    def adapt_collections(self):
        """ Include subactions in existing action dashboard collections """
        pstactions = self.pc.searchResults(
            portal_type="Folder",
            object_provides="imio.project.pst.interfaces.IActionDashboardBatchActions"
        )
        for pstaction in pstactions:
            for brain in self.pc.searchResults(
                    {'path': {'query': pstaction.getPath()},
                     'portal_type': 'DashboardCollection'}
            ):
                col = brain.getObject()
                for parameter in col.query:
                    if parameter['i'] == 'portal_type':
                        parameter['v'] = [u'pstaction', u'pstsubaction']
                col.query = list(col.query)  # need this to persist change
        # deactivate states collections to lighten menu
        for brain in self.pc(portal_type='DashboardCollection'):
            if brain.id.startswith('searchfor_'):
                obj = brain.getObject()
                obj.enabled = False
                obj.reindexObject(idxs=['enabled'])

    def install_analytic_budget_behavior(self):

        behavior = "imio.project.core.browser.behaviors.IAnalyticBudget"
        types = [
            u'strategicobjective',
            u'operationalobjective',
            u'pstaction',
            u'action_link',
            u'pstsubaction',
            u'subaction_link'
        ]

        for type_name in types:
            fti = queryUtility(IDexterityFTI, name=type_name)
            if not fti:
                continue
            if behavior in fti.behaviors:
                continue
            behaviors = list(fti.behaviors)
            behaviors.append(behavior)
            fti._updateProperty('behaviors', tuple(behaviors))

    def dx_local_roles(self):
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


def migrate(context):
    Migrate_To_1_3(context).run()
