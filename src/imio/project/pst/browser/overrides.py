# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from imio.history.browser.views import IHDocumentBylineViewlet


class DocumentBylineViewlet(IHDocumentBylineViewlet):
    '''
      Overrides the IHDocumentBylineViewlet to hide it for some layouts.
    '''

    def show(self):
        currentLayout = self.context.getLayout()
        if currentLayout in ['facetednavigation_view', ]:
            return False
        return True
