# -*- coding: utf-8 -*-
import logging

from imio.migrator.migrator import Migrator


logger = logging.getLogger('imio.project.pst')


class Migrate_To_0_4(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        self.runProfileSteps('imio.project.pst', steps=['portlets', ])
        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_0_4(context).run()
