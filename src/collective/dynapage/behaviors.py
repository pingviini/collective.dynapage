from zope import schema
from collective.dynapage.source import DynapagePathSourceBinder
from z3c.relationfield.schema import RelationChoice
from zope.interface import alsoProvides
from plone.directives import form
from collective.dynapage import _


class ICarousel(form.Schema):
    """Add tags to content
    """

    form.fieldset(
        'carousel',
        label=_(u'Carousel'),
        fields=('active', 'changeDelay', 'changingMethod','showNavigation', 'overridingContent'))

    active = schema.Bool(
        title=_(u"Activate carousel"),
        required=False,
        default=1,)

    changeDelay = schema.Int(
        title=_(u"Carousel change delay"),
        description=_(u"Carousel item display time in seconds."),
        default=10,
        required=False)

    changingMethod = schema.Choice(
        title=_(u"Carousel changing method"),
        required=False,
        values=['randomly','folderly'],
        default='folderly',)

    showNavigation = schema.Bool(
        title=_(u"Show navigation"),
        required=False,
        default=0,)

    overridingContent = RelationChoice(
        title=_(u"Sticky carousel item"),
        description=_(u"Select item which is always visible above content \
                        overriding other carousel items."),
        source=DynapagePathSourceBinder(),
        required=False,
        default=None,
        )

alsoProvides(ICarousel, form.IFormFieldProvider)


