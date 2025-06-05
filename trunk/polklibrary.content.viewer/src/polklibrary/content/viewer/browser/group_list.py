from plone import api
from plone.memoize import ram
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from polklibrary.content.viewer.utility import Tools
import random, time, transaction

from polklibrary.content.viewer.browser.collection import AdvancedCollectionQuery

class GroupList(BrowserView, Tools):

    template = ViewPageTemplateFile("templates/group_list.pt")
    
    def __call__(self):
        return self.template()

    def is_local_ip(self):
        return self.get_ip().startswith('141.233.')

    def load_collections(self):
        self.group_collections = self.get_collections()

    @ram.cache(lambda *args: time.time() // 60 * 10)
    def get_collections(self):
    
        catalog = api.portal.get_tool(name='portal_catalog')
        ordered_brains = []
        for collection in self.context.collections:
            brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.collection',
                review_state='published',
                id=collection,
            )
            if brains:
                ordered_brains.append(brains[0])
        
        collections = []
        for brain in ordered_brains:
            collections.append(AdvancedCollectionQuery(brain, limit=15, start=0, sort_by=brain.sort_type, sort_direction=brain.sort_direction))
    
        return collections
        
        
    @property
    def portal(self):
        return api.portal.get()
        
        