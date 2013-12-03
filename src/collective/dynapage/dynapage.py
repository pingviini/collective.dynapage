from five import grok
from zope.site.hooks import getSite
from plone.directives import form
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer
from Products.CMFCore.utils import getToolByName
from collective.dynapage.interfaces import IDynapageView
from collective.dynapage import _


class IDynapage(form.Schema):
    """A dynamic page."""

    text = RichText(
        title=_(u"Content"),
        required=False,)


class View(grok.View):
    """Grok view."""

    grok.context(IDynapage)
    grok.implements(IDynapageView)
    grok.require('zope2.View')

    @property
    def feeds(self):
        pc = getToolByName(self.context, 'portal_catalog')
        results = pc.searchResults({
            'portal_type': 'collective.dynaitem.collection',
            'review_state': 'published',
            'path': '/'.join(self.context.getPhysicalPath())
        })
        return results

    @property
    def text_output(self):
        # XXX: a workaround for https://dev.plone.org/ticket/12442
        text = self.context.text
        site = getSite()
        if text.mimeType == text.outputMimeType:
            return text.raw_encoded
        else:
            transformer = ITransformer(site, None)
            if transformer is None:
                return None
            transformer.context = self.context  # set the transform context
            return transformer(text, text.outputMimeType)
