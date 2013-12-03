from five import grok
from zope import schema
from plone.dexterity.content import Item
from plone.directives import form
from collective.dynapage.interfaces import IDynaItem, IListsItem
from collective.dynapage import _


class IDynaFeed(IDynaItem, form.Schema):
    """A Dynapage RSS item."""

    feed_url = schema.URI(
        title=_(u"Feed URL"),
        required=True,)


class DynaFeed(Item):
    """A DynaFeed class"""
    grok.implements(IListsItem)


class View(grok.View):
    """DynaFeed View"""

    grok.context(IDynaFeed)
    grok.require('zope2.View')


class ListView(View):
    """Listview for DynaFeed"""
    grok.name('listview')

