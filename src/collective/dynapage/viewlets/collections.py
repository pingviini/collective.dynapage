from five import grok
from zope.security import checkPermission
from zope.component import getMultiAdapter
from collective.dynapage.dynapage import IDynapage
from collective.dynapage.interfaces import IDynapageView
from plone.app.layout.viewlets.interfaces import IBelowContentTitle,\
                                                 IBelowContentBody


class Collections:

    def getCollections(self):
        objects = self.context.getFolderContents({
            'object_provides': self.getPosition(),
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending'},
            full_objects=True)

        return objects

    def getPosition(self):
        """This method should be overwritten by actual viewlet. By default we
           return all items which provide IListsItem interface."""
        return 'collective.dynapage.interfaces.IListsItem'

    def search(self):
        collections = self.getCollections()
        data = []
        results = 0
        if collections:
            for collection in collections:
                collection_view = getMultiAdapter((collection, self.request),
                                                   name='listview')
                tmp = {}
                tmp['title'] = collection.title
                tmp['view'] = collection_view()
                tmp['len'] = len(collection_view.search())
                data.append(tmp)
                if len(collection_view.search()) > 0:
                    results += 1

        return {'data': data, 'len': results}

    def canModify(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)


class TopCollections(grok.Viewlet, Collections):
    grok.context(IDynapage)
    grok.viewletmanager(IBelowContentTitle)
    grok.view(IDynapageView)
    grok.template('collections')

    def getPosition(self):
        return 'collective.dynapage.interfaces.ITopListItem'


class BottomCollections(grok.Viewlet, Collections):
    grok.context(IDynapage)
    grok.viewletmanager(IBelowContentBody)
    grok.view(IDynapageView)
    grok.template('collections')

    def getPosition(self):
        return 'collective.dynapage.interfaces.IBottomListItem'
