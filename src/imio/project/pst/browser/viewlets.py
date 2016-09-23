# -*- coding: utf-8 -*-

from imio.dashboard.browser.overrides import IDDocumentGeneratorLinksViewlet


class PSTDocumentGeneratorLinksViewlet(IDDocumentGeneratorLinksViewlet):

    def available(self):
        # don't exclude the viewlet if there is also a faceted view
        return super(IDDocumentGeneratorLinksViewlet, self).available()
