from plone.formwidget.contenttree.source import PathSourceBinder,\
                                                PathSource
from zope.component import getMultiAdapter
from zope.schema.vocabulary import SimpleTerm
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from Products.CMFCore.utils import getToolByName


class DynapagePathSource(PathSource):

    def __init__(self, context, selectable_filter, navigation_tree_query=None):
        self.context = context

        query_builder = getMultiAdapter((context, self),
                                        INavigationQueryBuilder)
        query = query_builder()
        if 'Image' not in query['portal_type']:
            query['portal_type'].append('Image')

        if navigation_tree_query is None:
            navigation_tree_query = {}

        # Copy path from selectable_filter into the navigation_tree_query
        # normally it does not make sense to show elements that wouldn't be
        # selectable anyway and are unneeded to navigate to selectable items
        if ('path' not in navigation_tree_query and
            'path' in selectable_filter.criteria):
            navigation_tree_query['path'] = selectable_filter.criteria['path']

        query.update(navigation_tree_query)

        self.navigation_tree_query = query
        self.selectable_filter = selectable_filter

        self.catalog = getToolByName(context, "portal_catalog")

        portal_tool = getToolByName(context, "portal_url")
        self.portal_path = portal_tool.getPortalPath()


class DynapageObjPathSource(DynapagePathSource):

    def _getBrainByValue(self, value):
        return self._getBrainByToken('/'.join(value.getPhysicalPath()))

    def getTermByBrain(self, brain, real_value=True):
        if real_value:
            value = brain._unrestrictedGetObject()
        else:
            value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)


class DynapagePathSourceBinder(PathSourceBinder):
    path_source = DynapageObjPathSource
