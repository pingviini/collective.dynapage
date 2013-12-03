#from five import grok
#from plone.app.contentmenu.interfaces import IContentMenuItem
#from zope.app.publisher.browser.menu import BrowserSubMenuItem
#from zope.publisher.interfaces.browser import IBrowserRequest
#from collective.dynapage.dynapage import IDynapage
#
#
#class DisplaySubMenuItem(grok.MultiAdapter, BrowserSubMenuItem):
#    grok.name("plone.contentmenu.display")
#    grok.provides(IContentMenuItem)
#    grok.adapts(IDynapage, IBrowserRequest)
#
#    def available(self):
#         return False
