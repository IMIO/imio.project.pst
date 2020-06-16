from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from collective.eeafaceted.dashboard.browser.facetedcollectionportlet import Renderer as BaseRenderer
from eea.facetednavigation.criteria.interfaces import ICriteria
from imio.project.pst.browser.facetediframe import get_criteria_holder


class Renderer(BaseRenderer):

    @property
    def available(self):
        return self._criteriaHolder.portal_type != 'Plone Site'

    @property
    def _criteriaHolder(self):
        return get_criteria_holder(self.context)

    @property
    def widget_render(self):
        if getattr(self, 'rendered_widgets', None):
            return self.rendered_widgets
        # get the IFacetedNavigable element the criteria are define on
        criteriaHolder = self._criteriaHolder
        criteria = ICriteria(criteriaHolder)
        widgets = []
        for criterion in criteria.values():
            if criterion.widget != CollectionWidget.widget_type:
                continue
            widget_cls = criteria.widget(wid=criterion.widget)
            widget = widget_cls(criteriaHolder, self.request, criterion)
            widget.display_fieldset = False

            # if we are not on the criteriaHolder, it means
            # that the portlet is displayed on children, we use another template
            # for rendering the widget
            if self._isPortletOutsideFaceted(self.context, self._criteriaHolder):
                self.context.REQUEST.set('force_redirect_to', True)
                #self.context.REQUEST.set('no_redirect', '1')
            # initialize the widget
            rendered_widget = widget()
            # render the widget as "portlet outside facetednav"
#            if self._isPortletOutsideFaceted(self.context, self._criteriaHolder):
#                # compute default criteria to display in the URL
#                widget.base_url = self._buildBaseLinkURL(criteria)
#                rendered_widget = ViewPageTemplateFile('templates/widget.pt')(widget)
            widgets.append(rendered_widget)
        return ''.join([w for w in widgets])
