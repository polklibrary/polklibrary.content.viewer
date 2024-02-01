from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
import random, time, transaction

class CacheView(BrowserView):

    template = ViewPageTemplateFile("templates/cache.pt")
    
    def __call__(self):
    
        if self.request.form.get('cache.rebuild', ''):
            data = {
                'series_title' : {},
                'subject_group' : {},
                'associated_entity' : {},
                'geography' : {},
                'genre' : {},
            }
            
            catalog = api.portal.get_tool(name='portal_catalog')
            
            for key,value in data.items():
                index = catalog._catalog.indexes[key]
                
                for k in index.uniqueValues():
                
                    t = index._index.get(k)
                    if type(t) is not int:
                        data[key][k] = len(t)
                    else:
                        data[key][k] = 1
        
            self.context.cache = data
    
        return self.template()

    
    @property
    def portal(self):
        return api.portal.get()
        
        