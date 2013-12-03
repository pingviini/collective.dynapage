from five import grok
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.interface import alsoProvides, noLongerProvides
from collective.dynapage.interfaces import IListsItem, ITopListItem,\
                                           IBottomListItem

mapping = {u'Top': ITopListItem, u'Bottom': IBottomListItem}
other = {u'Top': u'Bottom', u'Bottom': u'Top'}

@grok.subscribe(IListsItem, IObjectAddedEvent)
def addNewListingInterface(listitem, event):
    """Adds marker interface to item depending its desired position in listing."""
    alsoProvides(listitem, mapping[listitem.position])
    listitem.reindexObject(idxs=['object_provides'])


@grok.subscribe(IListsItem, IObjectModifiedEvent)
def addListingInterface(listitem, event):
    """Adds marker interface to item depending its desired position in listing."""
    try:
        provides = mapping[listitem.position]
    except KeyError:
        provides = mapping[unicode(listitem.position)]
    noLongerProvides(listitem, mapping[other[listitem.position]])
    alsoProvides(listitem, provides)
    listitem.reindexObject(idxs=['object_provides'])


