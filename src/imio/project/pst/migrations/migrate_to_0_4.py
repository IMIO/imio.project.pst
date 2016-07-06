# -*- coding: utf-8 -*-
import logging

from plone import api

from imio.migrator.migrator import Migrator
from imio.project.pst.setuphandlers import configureDashboard


logger = logging.getLogger('imio.project.pst')


class Migrate_To_0_4(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        self.runProfileSteps('imio.project.pst', steps=['portlets', ])

        # remove the old collections and configure the dashboard
        if 'collections' in self.portal.pst:
            api.content.delete(obj=self.portal.pst['collections'])

        configureDashboard(self.portal.pst)

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_0_4(context).run()
