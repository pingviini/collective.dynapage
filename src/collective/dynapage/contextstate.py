from zope.interface import implements
from zope.component import getMultiAdapter
from plone.memoize.view import memoize
from Acquisition import aq_inner, aq_parent
from plone.app.layout.globals.context import ContextState
from plone.app.layout.globals.interfaces import IContextState


class DynapageContextState(ContextState):
    """
    Overrides is_default_page method to check if current page url is the
    same as context url. In Plone this means our context is the object and
    not its container which default page our object is. By faking this we should see
    Add new... menu with correct types.
    """
    implements(IContextState)

    @memoize
    def folder(self):
        context = aq_inner(self.context)
        if self.is_structural_folder():
            if self.is_default_page():
                if context.absolute_url() in self.current_page_url():
                    return context
                else:
                    return aq_parent(context)
            else:
                return context
        else:
            return aq_parent(context)
        return context
