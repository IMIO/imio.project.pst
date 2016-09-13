from imio.dashboard.browser.facetedcollectionportlet import Renderer as BaseRenderer
from imio.dashboard.browser.facetedcollectionportlet import IFacetedCollectionPortlet
from .facetediframe import get_criteria_holder


class IFacetedCollectionPortletPST(IFacetedCollectionPortlet):
    pass


class Renderer(BaseRenderer):
    @property
    def _criteriaHolder(self):
        return get_criteria_holder(self.context)
