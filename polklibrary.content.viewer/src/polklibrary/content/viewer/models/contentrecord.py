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


content_types = SimpleVocabulary([
    SimpleTerm(value=u'book', title=u'Book'),
    SimpleTerm(value=u'dvd', title=u'DVD'),
    SimpleTerm(value=u'game', title=u'Board Game'),
    SimpleTerm(value=u'stream', title=u'Streaming Video'),
])


disable_embed_opts = SimpleVocabulary([
    SimpleTerm(value=u'yes', title=u'Yes'),
    SimpleTerm(value=u'no', title=u'No'),
])

@provider(IFormFieldProvider)
class IContentRecord(model.Schema):

    id = schema.TextLine(
            title=u"ID",
            required=True,
        )
    
    title = schema.TextLine(
            title=u"Title",
            required=True,
        )
        
    description = schema.Text(
            title=u"Description",
            required=False,
        )
        
    content_type = schema.Choice(
            title=u"Content Type",
            source=content_types,
            required=False,
            default='stream',
            missing_value='stream',
        )

    creator = schema.TextLine(
            title=u"Creator",
            required=False,
        )  

    runtime = schema.TextLine(
            title=u"Runtime",
            required=False,
        )

    date_of_publication = schema.TextLine(
            title=u"Date of Publication",
            required=False,
        )  
        
    direct_url = schema.TextLine(
            title=u"Direct URL (Override)",
            required=False,
        )  
        
    embed_code = schema.Text(
            title=u"Embed Code (Override)",
            required=False,
        )  
        
    # disable_embed = schema.Choice(
            # title=u"Disable Embed",
            # description=u"This will make the embed window a link.",
            # source=disable_embed_opts,
            # required=False,
            # default=u'no',
            # missing_value=u'no',
        # )
    disable_embed = schema.Bool(
            title=u"Disable Embed",
            description=u"This will make the embed window a link.",
            required=False,
            default=False
        )
        
    # --- Categorization FieldSet ---
    model.fieldset(
        'categorizing',
        label=u'Categorization', 
        fields=['series_title', 'subject_heading', 'associated_entity', 'geography', 'genre'],
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
        
        
    subject_heading = schema.Tuple(
        title=u'Subject Heading',
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )
    directives.widget(
        'subject_heading',
        AjaxSelectFieldWidget,
        vocabulary='polklibrary.content.viewer.vocabularies.SubjectHeadingVocabularyFactory'
    )
    directives.read_permission(subject_heading='cmf.AddPortalContent')
    directives.write_permission(subject_heading='cmf.AddPortalContent')
    directives.omitted('subject_heading')
    directives.no_omit(IEditForm, 'subject_heading')
    directives.no_omit(IAddForm, 'subject_heading')
    
    
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
    
    
    # --- Image FieldSet ---
    model.fieldset(
        'imageset',
        label=u'Image', 
        fields=['image_url', 'image'],
    )
    
    
    image_url = schema.TextLine(
            title=u"Image URL",
            description=u"Looks like: /@@download/image/NAME_OF_IMAGE_YOU_JUST_UPLOADED.jpg",
            required=False,
        )
        
    image = NamedBlobImage(
            title=u"Image File",
            required=False,
        )
        
    
    # --- Stats FieldSet ---
    model.fieldset(
        'statset',
        label=u'Stats', 
        fields=['likes', 'visits'],
    )
    
    likes = schema.Int(
            title=u"Total Likes",
            default=0
        )
        
    visits = schema.Int(
            title=u"Total Visits",
            default=0
        )
        
        
@indexer(IContentRecord)
def make_searchable(object, **kwargs):
    #import re
    #portal_transforms = api.portal.get_tool(name='portal_transforms')
    #data = portal_transforms.convertTo('text/plain', object.body.output, mimetype='text/structured')
    #text = data.getData()
    #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', object.body.output)
    data = []
    
    try:
        data += object.title.lower().split(' ')
        data += object.description.lower().split(' ')
        data += [object.content_type.lower()]
        data += [object.creator.lower()]
        data += [object.date_of_publication.lower()]
        data += [ x.lower() for x in list(object.series_title)]
        data += [ x.lower() for x in list(object.subject_heading)]
        data += [ x.lower() for x in list(object.associated_entity)]
        data += [ x.lower() for x in list(object.geography)]
        data += [ x.lower() for x in list(object.genre)]
    except:
        print "Error on reindex of content record"
        return []
        
    return data
        
        
        
        
        
        