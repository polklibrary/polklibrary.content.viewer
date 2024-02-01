from plone import api
from plone.memoize import ram
from Products.Five import BrowserView
from zope.interface import alsoProvides
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.protect.interfaces import IDisableCSRFProtection

from polklibrary.content.viewer.browser.collection import RelatedContent
from polklibrary.content.viewer.utility import Tools

import random, datetime, time

class CloseView(BrowserView):
    template = ViewPageTemplateFile("templates/close_view.pt")
    def __call__(self):
        return self.template()



class RecordView(BrowserView, Tools):

    template = ViewPageTemplateFile("templates/record_view.pt")
    
    totals = {}
    
    def __call__(self):
        
        if self.is_login_required():
            return self.request.response.redirect(self.portal.absolute_url() + '/login?came_from=' + self.context.absolute_url())
            
        
        alsoProvides(self.request, IDisableCSRFProtection)
        like = self.request.form.get('like', None)
        if like:
            self.context.likes += 1 
            
        self.context.visits += 1 
        #self.context.reindexObject()
            
        self.load_facet_totals()
        
        return self.template()
        
    def is_login_required(self):
        return api.user.is_anonymous() and self.context.login_required
        
    def load_facet_totals(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.content.viewer.models.tag_cache',
            review_state='published'
        )
        
        if brains:
            obj = brains[0].getObject()
            self.totals = obj.cache
        else:
            self.totals = {}
            
            
    def get_totals(self, type, name):
        try:
            return self.totals.get(type).get(name, 1)
        except Exception as e:
            return 1
        
    # def is_oncampus(self):
        # dev_restriction = '10.0.2.2'
        # ip_restriction = '141.233.'
        # ip = ''
        # if 'HTTP_X_FORWARDED_FOR' in self.request.environ:
            # ip = self.request.environ['HTTP_X_FORWARDED_FOR'] # Virtual host
        # elif 'HTTP_HOST' in self.request.environ:
            # ip = self.request.environ['REMOTE_ADDR'] # Non-virtualhost
        # ipl = ip.split(',')
        
        # print("IP: " + ipl[0])
        # return ipl[0].strip().startswith(ip_restriction) or ipl[0].strip().startswith(dev_restriction)
        
    def get_related(self):
        type = 'subject_group'
        subject_groups = []
        if self.context.subject_group:
            subject_groups = list(self.context.subject_group)
        random.seed(datetime.datetime.today().day)
        random.shuffle(subject_groups)
        subject_group = '|'.join(subject_groups[:2])
        series_title = '|'.join(self.context.series_title)
        data = {
            'series_title' : series_title,
            'subject_group' : subject_group,
        }
        
        suburl = 'subject_group=' + subject_group + '&series_title=' + series_title
        related = RelatedContent("Similar Films", data, self.portal.absolute_url(), limit=15, sort_by='random', show_query=False)
        related.items = list(filter(lambda x: x.getId != self.context.getId(), related.items))
        
        return suburl,related
        
        
    # @ram.cache(lambda *args: time.time() // (60 * 60 * 24 * 7)) # 1 week
    # def Totals(self): 
        # data = {
            # 'series_title' : {},
            # 'subject_group' : {},
            # 'associated_entity' : {},
            # 'geography' : {},
            # 'genre' : {},
        # }
        
        # catalog = api.portal.get_tool(name='portal_catalog')
        
        # for key,value in data.items():
            # index = catalog._catalog.indexes[key]
            
            # for k in index.uniqueValues():
            
                # t = index._index.get(k)
                # if type(t) is not int:
                    # data[key][k] = len(t)
                # else:
                    # data[key][k] = 1
        
        # return data
            
        
    @property
    def portal(self):
        return api.portal.get()
        
        