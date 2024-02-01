from plone import api
from plone.supermodel import model
from zope import schema
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary



class ITagCache(model.Schema):

    title = schema.TextLine(
            title=u"Title",
            required=True,
        )

    description = schema.Text(
            title=u"Description",
            required=False,
        )


    cache = schema.Dict(
            title=u"Cache Store",
            required=False,
            readonly=True,
            default={},
            missing_value={},
            value_type=schema.TextLine(),
        )
        