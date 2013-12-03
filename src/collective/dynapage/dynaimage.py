from five import grok
from zope import schema
from plone.directives import form
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.namedfile.field import NamedImage
from collective.dynapage.interfaces import IDynaItem, ICarouselItem,\
                                           IDynaImageView
from collective.dynapage import _


class IDynaImage(form.Schema):
    """A Dynapage image item"""

    image = NamedImage(
        title=_(u"Image"),
        required=True,)

    text = RichText(
        title=_(u"Content"),
        required=False,)

    link_url = schema.TextLine(
        title=_(u"Link URL"),
        required=False,)


class DynaImage(Item):
    grok.implements(IDynaItem, ICarouselItem)


class View(grok.View):
    grok.context(IDynaImage)
    grok.implements(IDynaImageView)
    grok.require('zope2.View')

    def getAltText(self):
        return self.context.description or self.context.title or \
               self.context.image.filename


class CarouselView(grok.View):
    grok.context(IDynaImage)
    grok.require('zope2.View')
    grok.name('carouselview')

    def getAltText(self):
        return self.context.description or self.context.title or \
               self.context.image.filename
