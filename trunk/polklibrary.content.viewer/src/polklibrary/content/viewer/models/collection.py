from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model

from plone.indexer.decorator import indexer

from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import provider, directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


yesno = SimpleVocabulary([
    SimpleTerm(value=u'0', title=u'No'),
    SimpleTerm(value=u'1', title=u'Yes'),
])

andor = SimpleVocabulary([
    SimpleTerm(value=u'or', title=u'OR'),
    SimpleTerm(value=u'and', title=u'AND'),
])

content_types = SimpleVocabulary([
    SimpleTerm(value=u'book', title=u'Book'),
    SimpleTerm(value=u'dvd', title=u'DVD'),
    SimpleTerm(value=u'game', title=u'Board Game'),
    SimpleTerm(value=u'stream', title=u'Streaming Video'),
])

modes = SimpleVocabulary([
    SimpleTerm(value=u'created', title=u'Add Date'),
    SimpleTerm(value=u'modified', title=u'Last Modified'),
    SimpleTerm(value=u'random', title=u'Randomize'),
    SimpleTerm(value=u'Title', title=u'Title'),
])

directional = SimpleVocabulary([
    SimpleTerm(value=u'ascending', title=u'Ascending'),
    SimpleTerm(value=u'descending', title=u'Descending'),
])

class ICollection(model.Schema):

    title = schema.TextLine(
            title=u"Title",
            description=u"WARNING: Cached for 5 minutes.  Changes may take 5 minutes to appear.",
            required=True,
        )

    description = schema.Text(
            title=u"Description",
            required=False,
        )

    format_type = schema.List(
            title=u"Restrict content types in this collection",
            required=False,
            value_type=schema.Choice(source=content_types),
        )
          
    limit = schema.Int(
            title=u"Limit size of collection",
            default=250,
            required=False,
        )
          
    enabled_browse = schema.Bool(
            title=u"Will appear in 'Select A Collection' dropdown?",
            required=False,
        )
        
        
    # --- Query FieldSet ---
    model.fieldset(
        'query',
        label=u'Query', 
        fields=['query_logic', 'by_id', 'series_title', 'subject_group', 'associated_entity', 'geography', 'genre', 'sort_type', 'sort_direction'],
    )
    
    query_logic = schema.TextLine(
            title=u"Query Logic",
            description=u"Left to right logic, no parentheses allowed. Select OR or AND in subject_group[OR|AND] to combine terms. by_id has no operators.  Example: by_id OR series_title[OR] OR subject_group[OR] OR associated_entity[OR] OR geography[OR] OR genre[OR]",
            default=u"series_title[OR] OR subject_group[OR] OR associated_entity[OR] OR geography[OR] OR genre[OR]",
            required=True,
        )

    by_id = schema.Text(
            title=u"List of ID's to include",
            required=False,
            missing_value=u"",
            default=u"",
        )
    
    series_title = schema.Tuple(
        title=u'Series Title',
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )
    directives.widget(
        'series_title',
        AjaxSelectFieldWidget,
        vocabulary='polklibrary.content.viewer.vocabularies.SeriesTitleVocabularyFactory'
    )
    directives.read_permission(series_title='cmf.AddPortalContent')
    directives.write_permission(series_title='cmf.AddPortalContent')
    directives.omitted('series_title')
    directives.no_omit(IEditForm, 'series_title')
    directives.no_omit(IAddForm, 'series_title')
    
    
    subject_group = schema.Tuple(
        title=u'Subject Heading',
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )
    directives.widget(
        'subject_group',
        AjaxSelectFieldWidget,
        vocabulary='polklibrary.content.viewer.vocabularies.SubjectGroupVocabularyFactory'
    )
    directives.read_permission(subject_group='cmf.AddPortalContent')
    directives.write_permission(subject_group='cmf.AddPortalContent')
    directives.omitted('subject_group')
    directives.no_omit(IEditForm, 'subject_group')
    directives.no_omit(IAddForm, 'subject_group')
    

    associated_entity = schema.Tuple(
        title=u'Associated Entity',
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )
    directives.widget(
        'associated_entity',
        AjaxSelectFieldWidget,
        vocabulary='polklibrary.content.viewer.vocabularies.AssociatedEntityVocabularyFactory'
    )
    directives.read_permission(associated_entity='cmf.AddPortalContent')
    directives.write_permission(associated_entity='cmf.AddPortalContent')
    directives.omitted('associated_entity')
    directives.no_omit(IEditForm, 'associated_entity')
    directives.no_omit(IAddForm, 'associated_entity')

        
    geography = schema.Tuple(
        title=u'Geography',
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )
    directives.widget(
        'geography',
        AjaxSelectFieldWidget,
        vocabulary='polklibrary.content.viewer.vocabularies.GeographyVocabularyFactory'
    )
    directives.read_permission(geography='cmf.AddPortalContent')
    directives.write_permission(geography='cmf.AddPortalContent')
    directives.omitted('geography')
    directives.no_omit(IEditForm, 'geography')
    directives.no_omit(IAddForm, 'geography')

    
    genre = schema.Tuple(
        title=u'Genre',
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )
    directives.widget(
        'genre',
        AjaxSelectFieldWidget,
        vocabulary='polklibrary.content.viewer.vocabularies.GenreVocabularyFactory'
    )
    directives.read_permission(genre='cmf.AddPortalContent')
    directives.write_permission(genre='cmf.AddPortalContent')
    directives.omitted('genre')
    directives.no_omit(IEditForm, 'genre')
    directives.no_omit(IAddForm, 'genre')
    
    
    sort_type = schema.Choice(
            title=u"Sort By",
            default=u"created",
            required=False,
            source=modes,
        )
        
    sort_direction = schema.Choice(
            title=u"Sort Direction",
            default=u"ascending",
            required=False,
            source=directional,
        )
        
        
        