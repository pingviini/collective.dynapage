from plone.directives import form
from zope.interface import Interface
from zope import schema
from collective.dynapage import _


class IDynapageBrowserLayer(Interface):
    """A layer for dynapage add-on."""


class IDynaItem(form.Schema):
    """Dynapage Item Marker"""


class IDynapageView(Interface):
    """A marker interface for Dynapage View"""


class IDynaCollectionView(Interface):
    """A marker interface for collection view"""


class IDynaImageView(Interface):
    """A marker interface for image view"""


class IDynaFeedView(Interface):
    """A marker interface for feed (collective.dynaitem.feed) view"""


class IDynaRSSView(Interface):
    """A marker interface for rss view"""


class IDynaItemPosition(IDynaItem, form.Schema):
    """DynaItem position marker for dynaitems"""

    position = schema.Choice(
        title=_(u"Position"),
        required=False,
        values=[_(u"Top"), _(u"Bottom")],
        default='Top')


class IListsItem(Interface):
    """Marker interface for collection items"""


class ITopListItem(Interface):
    """Marker interface for items being placed in top collection"""


class IBottomListItem(Interface):
    """Marker interface for items placed in bottom collection"""


class ICarouselItem(Interface):
    """Marker interface for carousel objects"""


class ICarouselView(Interface):
    """Marker interface for carousel view"""
