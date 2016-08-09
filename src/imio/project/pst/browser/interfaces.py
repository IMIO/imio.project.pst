from eea.facetednavigation.interfaces import IFacetedNavigable


class IMyFacetedNavigable(IFacetedNavigable):
    """More specific IFacetedNavigable to be able to override
    ICriteria adapter only for specific OO and OS.
    """
