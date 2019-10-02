# -*- coding: utf-8 -*-

import logging

from Products.CPUtils.Extensions.utils import mark_last_version
from collective.documentgenerator.utils import update_oo_config
from imio.migrator.migrator import Migrator
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.project.pst.setuphandlers import configure_lasting_objectives
from imio.project.pst.setuphandlers import _ as _translate
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility

logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog
        self.ps = self.portal.portal_setup

    def run(self):

        self.various_update()

        # check if oo port must be changed
        update_oo_config()

        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog', 'typeinfo', 'viewlets', 'workflow'])
        self.runProfileSteps('imio.project.pst', steps=['repositorytool'], profile='demo')

        self.adapt_collections()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update')
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default')

        self.runProfileSteps('imio.project.core', steps=['plone.app.registry'], profile='default')

        configure_lasting_objectives(self.context)

        self.install_analytic_budget_behavior()

        self.upgradeAll(omit=['imio.project.pst:default'])

        for prod in ['plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()

    def various_update(self):
        # replace front-page
        frontpage = getattr(self.portal, 'front-page')
        frontpage.title = _translate("front_page_title")
        frontpage.description = _translate("front_page_descr")
        frontpage.text = richtextval(_translate("front_page_text"))
        transitions(frontpage, ('retract', 'publish_internally'))
        frontpage.reindexObject()

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


def migrate(context):
    Migrate_To_1_3(context).run()
