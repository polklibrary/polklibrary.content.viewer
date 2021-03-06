from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from polklibrary.content.viewer.utility import BrainsToCSV, text_to_tuple
import random, time, re, datetime, operator


class FakeCollection:
    
    def __init__(self, 
                 url, 
                 title, 
                 query='series_title[OR] OR subject_heading[OR] OR associated_entity[OR] OR geography[OR] OR genre[OR]', 
                 series_title=(),
                 subject_heading=(), 
                 associated_entity=(), 
                 geography=(), 
                 genre=(),
                 by_id=""):
                 
        self.url = url
        self.Title = title
        self.query_logic = query
        self.series_title = series_title
        self.subject_heading = subject_heading
        self.associated_entity = associated_entity
        self.geography = geography
        self.genre = genre        
        self.by_id = text_to_tuple(by_id)
        
    def absolute_url(self):
        return self.url
        

class CollectionObject:
    
    def __init__(self, title, url, items, total, start, limit):
        self.title = title
        self.url = url.split('start=')[0].rstrip('&').rstrip('?')
        self.items = items
        self.total = total
        self.start = start
        self.limit = limit
    
        delimiter = '?'
        if '?' in self.url:
            delimiter = '&'
    
        index = 1
        self.pages = []
        if total > 0:
            for i in range(0, total, limit):
                self.pages.append({
                    'purl' :  self.url + delimiter + 'start=' + str(i) + '&limit=' + str(limit),
                    'start' : i,
                    'limit' : limit,
                    'number' : index,
                })
                index+=1
    

def AdvancedCollectionQuery(collection, limit=10, start=0, sort_by='created', sort_direction='ascending'):

    try:
        catalog = api.portal.get_tool(name='portal_catalog')
                
        results = None
        if collection.by_id or collection.series_title or collection.subject_heading or collection.associated_entity or collection.geography or collection.genre: # IF SET, LIMIT RESULTS
        
            query = re.sub( '\s+', ' ', collection.query_logic.lower()).strip()
            byid_andor = 'or'
            series_andor = 'or'
            subject_andor = 'or'
            associated_entity_andor = 'or'
            geography_andor = 'or'
            genre_andor = 'or'
            
            if 'by_id[and]' in query:
                byid_andor = 'and'
            if 'series_title[and]' in query:
                series_andor = 'and'
            if 'subject_heading[and]' in query:
                subject_andor = 'and'
            if 'associated_entity[and]' in query:
                associated_entity_andor = 'and'
            if 'geography[and]' in query:
                geography_andor = 'and'
            if 'genre[and]' in query:
                genre_andor = 'and'
                
                
            byid_brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                id={
                    "query":  text_to_tuple(collection.by_id),
                    "operator" : 'or',
                },
            )
                
            series_title_brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                series_title={
                    "query": collection.series_title,
                    "operator" : series_andor,
                },
            )
            
            subject_heading_brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                subject_heading={
                    "query": collection.subject_heading,
                    "operator" : subject_andor,
                },
            )

            associated_entity_brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                associated_entity={
                    "query": collection.associated_entity,
                    "operator" : associated_entity_andor,
                },
            )

            geography_brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                geography={
                    "query": collection.geography,
                    "operator" : geography_andor,
                },
            )
            
            genre_brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                genre={
                    "query": collection.genre,
                    "operator" : genre_andor,
                },
            )

            query_parts = query.split(' ')
            result_query = ''
            result_op = ''

            # Set First Result
            if 'by_id' in query_parts[0]:
                results = byid_brains
            elif 'series_title' in query_parts[0]:
                results = series_title_brains
            elif 'subject_heading' in query_parts[0]:
                results = subject_heading_brains
            elif 'associated_entity' in query_parts[0]:
                results = associated_entity_brains
            elif 'geography' in query_parts[0]:
                results = geography_brains
            elif 'genre' in query_parts[0]:
                results = genre_brains
                
                
            
            # Skip First Result and Start Merging Queries, Second result should be 'or' or 'and'
            for q in query_parts[1:]:
                cq = q.strip()
                if cq == 'and':
                    result_op = 'and'
                elif cq == 'or':
                    result_op = 'or'
                else:
                    result = None
                    if 'by_id' in cq:
                        result = byid_brains
                    elif 'series_title' in cq:
                        result = series_title_brains
                    elif 'subject_heading' in cq:
                        result = subject_heading_brains
                    elif 'associated_entity' in cq:
                        result = associated_entity_brains
                    elif 'geography' in cq:
                        result = geography_brains
                    elif 'genre' in cq:
                        result = genre_brains
                        
                    if result_op == 'and':
                        results = AndFilter(results, result)
                    else: # or
                        results = OrFilter(results, result)
        
        
        
        else:  # GET ALL RESULTS
        
            results = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
            )


        # Sort them
        if sort_direction.lower() == 'ascending':
            reverse=False
        else:
            reverse=True
            
        results = list(results)
        if sort_by == 'random':
            random.seed(datetime.datetime.today().day)
            random.shuffle(results)
        else:
            results = sorted(results, key=lambda x: x[sort_by], reverse=reverse)
        
        # Set and limit them
        try:
            url = collection.getURL()
        except:
            url = collection.absolute_url()
        
        return CollectionObject(collection.Title, url, results[start:start+limit], len(results), start, limit)
    except Exception as e:
        print "AdvancedCollectionQuery ERROR: " + str(e)
        
    return CollectionObject(collection.Title, collection.absolute_url(), [], 0, 0, 0) # catch all

    

def OrFilter(listone, listtwo):
    if not listone:
        return listtwo # nothing in list one, return two
    if not listtwo:
        return listone # nothing in list two, return one
    
    # merge into dict for dedup
    results = {} # dedup
    for o in listone:
        results[o.getId] = o
    for t in listtwo:
        results[t.getId] = t
        
    return results.values()
    
def AndFilter(listone, listtwo):
    if not listone:
        return listtwo # nothing in list one, return two
    if not listtwo:
        return listone # nothing in list two, return one
    
    # otherwise cross check items in each
    results = {} # dedup
    for o in listone:
        for t in listtwo:
            if o.getId == t.getId:
                results[o.getId] = o
                
    return results.values()


def RelatedContent(label, data, url, limit=10, start=0, sort_by='created', sort_direction='descending', show_query=True):
    subject_query = ()
    associated_query = ()
    geography_query = ()
    genre_query = ()
    series_query = ()

    subject_data = data.get('subject_heading', ())
    associated_data = data.get('associated_entity', ())
    geography_data = data.get('geography', ())
    genre_data = data.get('genre', ())
    series_data = data.get('series_title', ())
    
    if subject_data:
        subject_query = tuple(subject_data.split('|'))
    if associated_data:
        associated_query = tuple(associated_data.split('|'))
    if geography_data:
        geography_query = tuple(geography_data.split('|'))
    if genre_data:
        genre_query = tuple(genre_data.split('|'))
    if series_data:
        series_query = tuple(series_data.split('|'))

    
    title = label
    if show_query:
        query = subject_query + associated_query + geography_query + genre_query + series_query
        title = label  + ': ' + ', '.join([t.capitalize() for t in query])
    
    fc = FakeCollection(
        url,
        title,
        series_title=series_query,
        subject_heading=subject_query,
        associated_entity=associated_query,
        geography=geography_query,
        genre=genre_query
    )

    return AdvancedCollectionQuery(fc, limit=limit, start=start, sort_by=sort_by, sort_direction=sort_direction)

    
    
class BrowseView(BrowserView):
    """ View collection by GET parameters """

    shareable = False
    template = ViewPageTemplateFile("templates/collection.pt")
    
    def __call__(self):
        if self.request.form.get('csv', None):
            self.request.response.setHeader("Content-Disposition", "attachment;filename=collection.csv")
            return BrainsToCSV(self.get_collection().items)
        return self.template()
        
    def has_editor_permission(self):
        membership = api.portal.get_tool('portal_membership')
        return bool(membership.checkPermission('Portlets: Manage portlets', self.context))
        
    def get_collection(self):
        start = int(self.request.form.get("start", 0))
        limit = int(self.request.form.get("limit", 20))
        
        return RelatedContent("Browsing", self.request.form, self.request['URL'] + '?' + self.request["QUERY_STRING"], limit=limit, start=start, sort_by='created', sort_direction='descending')
            
    @property
    def portal(self):
        return api.portal.get()
        
    
class UserListView(BrowserView):
    """ View collection by user saved playlist """

    shareable = False
    template = ViewPageTemplateFile("templates/collection.pt")
    
    def __call__(self):
        if self.request.form.get('csv', None):
            self.request.response.setHeader("Content-Disposition", "attachment;filename=collection.csv")
            return BrainsToCSV(self.get_collection().items)
        return self.template()
        
    def has_editor_permission(self):
        membership = api.portal.get_tool('portal_membership')
        return bool(membership.checkPermission('Portlets: Manage portlets', self.context))
        
    def get_collection(self):
        if api.user.is_anonymous():
            return CollectionObject("No User", self.portal.absolute_url() + '/playlist', [], 0, 0, 0) # catch all
            
        else:
            
            start = int(self.request.form.get("start", 0))
            limit = int(self.request.form.get("limit", 250))
            
            user = api.user.get_current()
            films = user.saved_films.split('|')
            films.pop()
            catalog = api.portal.get_tool(name='portal_catalog')
            brains = catalog.searchResults(
                portal_type='polklibrary.content.viewer.models.contentrecord',
                review_state='published',
                id={
                    "query": films,
                    "operator" : 'or',
                },
            )
            #results[start:start+limit], len(results), start, limit
            return CollectionObject("Your Playlist", self.portal.absolute_url() + '/playlist', brains[start:start+limit], len(brains), start, limit)
        
                
    def get_image(self):
        return '++resource++polklibrary.content.viewer/missing-thumb.png'
    
    def get_image(self, item):
        if item.image_url == '' or '++resource++' in item.image_url:
            return '++resource++polklibrary.content.viewer/missing-thumb.png'
        return item.getURL + '/@@download/image/thumb.jpg'
        
    @property
    def portal(self):
        return api.portal.get()
        
    

class CollectionView(BrowserView):
    """ View collection by saved criteria """

    shareable = True
    template = ViewPageTemplateFile("templates/collection.pt")
    
    def __call__(self):
        if self.request.form.get('csv', None):
            self.request.response.setHeader("Content-Disposition", "attachment;filename=collection.csv")
            return BrainsToCSV(self.get_collection().items)
        return self.template()
        
    def has_editor_permission(self):
        membership = api.portal.get_tool('portal_membership')
        return bool(membership.checkPermission('Portlets: Manage portlets', self.context))
        
    def get_collection(self):
        start = int(self.request.form.get("start", 0))
        limit = int(self.request.form.get("limit", self.context.limit))
        return AdvancedCollectionQuery(self.context, limit=limit, start=start, sort_by=self.context.sort_type, sort_direction=self.context.sort_direction)
                
    def get_image(self):
        return '++resource++polklibrary.content.viewer/missing-thumb.png'
    
    def get_image(self, item):
        if item.image_url == '' or '++resource++' in item.image_url:
            return '++resource++polklibrary.content.viewer/missing-thumb.png'
        return item.getURL + '/@@download/image/thumb.jpg'
        
    @property
    def portal(self):
        return api.portal.get()
        
        
class ShareView(CollectionView):

    template = ViewPageTemplateFile("templates/share.pt")
    
    def __call__(self):
        self.request.response.setHeader('X-Frame-Options', 'ALLOWALL')
        return self.template()
        
    def has_editor_permission(self):
        membership = api.portal.get_tool('portal_membership')
        return bool(membership.checkPermission('Portlets: Manage portlets', self.context))
        
    def get_collection(self):
        return AdvancedCollectionQuery(self.context, limit=25, sort_by=self.context.sort_type, sort_direction=self.context.sort_direction)
        