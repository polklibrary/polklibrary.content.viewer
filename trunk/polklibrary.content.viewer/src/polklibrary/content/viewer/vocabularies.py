from BTrees.IIBTree import intersection
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.site.hooks import getSite
from Products.CMFPlone.utils import safe_unicode
from binascii import b2a_qp
from plone.app.content.browser.vocabulary import _permissions, PERMISSIONS


def safe_encode(value):
    if isinstance(value, str):
        # no need to use portal encoding for transitional encoding from
        # unicode to ascii. utf-8 should be fine.
        value = value.encode('utf-8')
    return value


def safe_simpleterm_from_value(value):
    """create SimpleTerm from an untrusted value.
    - token need cleaned up: Vocabulary term tokens *must* be 7 bit values
    - anything for display has to be cleaned up, titles *must* be unicode
    """
    return SimpleTerm(value, b2a_qp(safe_encode(value)), safe_unicode(value))


def safe_simplevocabulary_from_values(values, query=None):
    """Creates (filtered) SimpleVocabulary from iterable of untrusted values.
    """
    items = [
        safe_simpleterm_from_value(i)
        for i in values
        if query is None or safe_encode(query) in safe_encode(i)
    ]
    return SimpleVocabulary(items)




@implementer(IVocabularyFactory)
class KeywordsVocabulary(object):

    keyword_index = 'Subject'
    path_index = 'path'

    def __init__(self, index, path='path'):
        self.keyword_index = index
        self.path_index = path
        
    def section(self, context):
        """gets section from which subjects are used.
        """
        registry = queryUtility(IRegistry)
        if registry is None:
            return None
        if registry.get('plone.subjects_of_navigation_root', False):
            portal = getToolByName(context, 'portal_url').getPortalObject()
            return getNavigationRootObject(context, portal)
        return None

    def all_keywords(self, kwfilter):
        site = getSite()
        self.catalog = getToolByName(site, 'portal_catalog', None)
        if self.catalog is None:
            return SimpleVocabulary([])
        index = self.catalog._catalog.getIndex(self.keyword_index)
        return safe_simplevocabulary_from_values(index._index, query=kwfilter)

    def keywords_of_section(self, section, kwfilter):
        """Valid keywords under the given section.
        """
        pcat = getToolByName(section, 'portal_catalog')
        cat = pcat._catalog
        path_idx = cat.indexes[self.path_index]
        tags_idx = cat.indexes[self.keyword_index]
        result = []
        # query all oids of path - low level
        pquery = {
            self.path_index: {
                'query': '/'.join(section.getPhysicalPath()),
                'depth': -1,
            }
        }
        kwfilter = safe_encode(kwfilter)
        # uses internal zcatalog specific details to quickly get the values.
        path_result, info = path_idx._apply_index(pquery)
        for tag in tags_idx.uniqueValues():
            if kwfilter and kwfilter not in safe_encode(tag):
                continue
            tquery = {self.keyword_index: tag}
            tags_result, info = tags_idx._apply_index(tquery)
            if intersection(path_result, tags_result):
                result.append(tag)
        # result should be sorted, because uniqueValues are.
        return safe_simplevocabulary_from_values(result)

    def __call__(self, context, query=None):
        section = self.section(context)
        if section is None:
            return self.all_keywords(query)
        return self.keywords_of_section(section, query)

        
# Set all factory hooks and permissions
SeriesTitleVocabularyFactory = KeywordsVocabulary('series_title')
PERMISSIONS['polklibrary.content.viewer.vocabularies.SeriesTitleVocabularyFactory'] = 'View'

SubjectGroupVocabularyFactory = KeywordsVocabulary('subject_group')
PERMISSIONS['polklibrary.content.viewer.vocabularies.SubjectGroupVocabularyFactory'] = 'View'

AssociatedEntityVocabularyFactory = KeywordsVocabulary('associated_entity')
PERMISSIONS['polklibrary.content.viewer.vocabularies.AssociatedEntityVocabularyFactory'] = 'View'

GeographyVocabularyFactory = KeywordsVocabulary('geography')
PERMISSIONS['polklibrary.content.viewer.vocabularies.GeographyVocabularyFactory'] = 'View'

GenreVocabularyFactory = KeywordsVocabulary('genre')
PERMISSIONS['polklibrary.content.viewer.vocabularies.GenreVocabularyFactory'] = 'View'




























