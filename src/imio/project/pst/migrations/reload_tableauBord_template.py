# -*- coding: utf-8 -*-

from imio.migrator.migrator import Migrator

import logging
logger = logging.getLogger('imio.project.pst')


class Reload_tableauBord_template(Migrator):
    def __init__(self, context):
        Migrator.__init__(self, context)

    def _delete_status_template_id(self):
        site = self.portal
        folder = site.templates
        id = 'status_template'
        if folder.hasObject(id):
            folder.manage_delObjects(id)

    def run(self):
        logger.info('Reload tableauBord template ...')

        self._delete_status_template_id()
        # reinstall
        self.reinstall(profiles=[u'profile-imio.project.pst:default', ])
        # Display duration
        self.finish()


def reload(context):
    Reload_tableauBord_template(context).run()
