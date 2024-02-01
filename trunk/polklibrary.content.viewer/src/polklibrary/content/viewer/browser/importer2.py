from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from polklibrary.content.viewer.marc_utility import process_marc
from polklibrary.content.viewer.utility import VendorInfo

import csv, io, re, ast, json
import pprint, logging

logger = logging.getLogger("Plone")


class Importer2View(BrowserView):

    template = ViewPageTemplateFile("templates/importer2.pt")
    
    ALEXANDER_STREET_NAME = VendorInfo.ALEXANDER_STREET_NAME
    KANOPY_NAME = VendorInfo.KANOPY_NAME
    FILMSONDEMAND_NAME = VendorInfo.FILMSONDEMAND_NAME
    SWANK_NAME = VendorInfo.SWANK_NAME
    
    csv_check_listtypes = ['genre','series_title','associated_entity','subject_group','geography']
    csv_required_add_update_headings = ['filmID', 
                                    'creator', 
                                    'title', 
                                    'date_of_publication', 
                                    'runtime', 
                                    'series_title', 
                                    'summary', 
                                    'format_type',
                                    'associated_entity', 
                                    'geography', 
                                    'subject_group', 
                                    'genre',
                                    'image_url',
                                    'direct_url']
                                    
    csv_required_delete_headings  = ['filmID']  
    csv_required_activation_headings  = ['filmID']  
    
    def __call__(self):
        
        self.entries = []
        
        self.error = ''
        self.records_created = 0
        self.records_created_failed = []
        self.records_updated = 0
        self.records_updated_failed = []
        self.records_deleted = 0
        self.records_deleted_failed = []
        self.records_activated = 0
        self.records_deactivated = 0
        self.records_activated_failed = []
        
        target_container = self.request.get('form.container.type', '%%%')
        containers = api.content.find(self.portal, portal_type='Folder', id=target_container)
        self.file = self.request.get('form.file.upload', None)
        
            
        if self.file and containers:
            self.container = containers[0].getObject()
            
            if self.file.filename.endswith('.mrc'):
                self.marc_to_entry()
            elif self.file.filename.endswith('.csv'):
                self.csv_to_entry()
            
            if self.entries:
                if self.request.get('form.file.submit', None):
                    self._process_create_or_update()
                if self.request.get('form.file.delete', None):
                    self._process_deletions()
                if self.request.get('form.file.activate', None):
                    self._process_activations('on')
                if self.request.get('form.file.deactivate', None):
                    self._process_activations('off')
            
        return self.template()



    def marc_to_entry(self):
        headerdata, marcdata = process_marc(self.file.read())
        for row in marcdata: # skip first row which is column names
            entry = self.unify_entry({
                'filmID': row[0],
                'creator': row[1],
                'title': row[2],
                'date_of_publication': row[3],
                'runtime': row[4],
                'series_title': self.marc_list_cleanup(row[5]),
                'summary': row[6],
                'format_type': row[7],
                'associated_entity': self.marc_list_cleanup(row[8]),
                'geography': self.marc_list_cleanup(row[9]),
                'subject_group': self.marc_list_cleanup(row[10]),
                'genre': self.marc_list_cleanup(row[11]),
                'image_url': row[12],
                'direct_url': row[13],
            })
            
            print("---------------------------")
            print(entry)
            
            
            self.entries.append(entry)
            
    def csv_to_entry(self):
    
        req_headings = self.csv_required_add_update_headings # ADD / OVERLAY
        if self.request.get('form.file.delete', None): # DELETE
            req_headings = self.csv_required_delete_headings
        elif self.request.get('form.file.activate', None) or self.request.get('form.file.deactivate', None): # ACTIVATIONS
            req_headings = self.csv_required_activation_headings
    
        keys = []
        sio = io.StringIO(self.file.read().decode("utf-8"))
        reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel)
        for row in reader:
            if not keys:
                for key in row:
                    key = key.strip()
                    if key in req_headings:
                        keys.append(key)
                    else:
                        self.error = 'Mismatch header: ' + key
                        return
                if len(keys) != len(req_headings):
                    self.error = 'Mismatch header: column names not equal amount, make sure one is not missing. Found:' + str(len(keys)) + ' Required:' + str(len(req_headings))
                    return
            else:
                index = 0
                entry = { }
                for info in row:
                    current_key = keys[index]
                    if current_key in self.csv_check_listtypes:
                        entry[current_key] = self.csv_list_cleanup(info) # transform lists
                    else:
                        entry[current_key] = info # standard types
                    index+=1
                self.entries.append(self.unify_entry(entry))
                
    
    def unify_entry(self, entry):
    
        # any clean up of data
        if 'direct_url' in entry and 'remote.uwosh.edu' not in entry['direct_url']:
            entry['direct_url'] = 'https://www.remote.uwosh.edu/login?url=' + entry['direct_url']
            
        # any clean up of data
        if 'image_url' in entry and entry['image_url'] and 'kaltura.com/' in entry['image_url']:
            entry['image_url'] = entry['image_url'].replace('/width/88','/width/320')
             
        
        return entry
    
    def marc_list_cleanup(self, data):
        if not data:
            return []
        if data[0] == None or data[0].replace(' ', '') == '':
            return []
        return data
        
    def csv_list_cleanup(self, data):
        data = data.strip()
        if data.startswith('[') and data.endswith(']'): # it is a list
            return  ast.literal_eval(data)
        return []
        
    def _process_create_or_update(self):
        for entry in self.entries:
        
            id = idnormalizer.normalize(entry['filmID'])
            brains = api.content.find(context=self.container, 
                                   portal_type='polklibrary.content.viewer.models.contentrecord',
                                   id=id,
            )

            # Update
            if len(brains) > 0:
                try:
                    obj = brains[0].getObject()
                    obj.title=entry['title']
                    obj.creator=entry['creator']
                    obj.date_of_publication=entry['date_of_publication']
                    obj.runtime=entry['runtime']
                    obj.series_title=entry['series_title']
                    obj.description=entry['summary']
                    obj.format_type=entry['format_type']
                    obj.associated_entity=entry['associated_entity']
                    obj.geography=entry['geography']
                    obj.subject_group=entry['subject_group']
                    obj.genre=entry['genre']
                    
                    current_img = obj.image_url
                    obj.image_url = entry['image_url'] # set
                    if current_img and current_img.startswith('/@@images'):
                        obj.image_url = current_img # revert it, due to local image

                        
                    obj.getRemoteUrl=entry['direct_url']
                    obj.reindexObject()
                    
                    self.records_updated += 1
                except Exception as e:
                   self.error = str(e)
                   self.records_created_failed.append(id)
                
            # Create
            else:
                try:
                    obj = api.content.create(container=self.container, 
                                       type='polklibrary.content.viewer.models.contentrecord', 
                                       safe_id=False, 
                                       id=id, 
                                       title=entry['title'], 
                                       creator=entry['creator'], 
                                       date_of_publication=entry['date_of_publication'], 
                                       runtime=entry['runtime'], 
                                       series_title=entry['series_title'], 
                                       description=entry['summary'], 
                                       format_type=entry['format_type'], 
                                       associated_entity=entry['associated_entity'],  
                                       geography=entry['geography'],  
                                       subject_group=entry['subject_group'], 
                                       genre=entry['genre'], 
                                       image_url=entry['image_url'],
                                       getRemoteUrl=entry['direct_url'],
                    )
                    
                    if obj:
                        obj.reindexObject()                            
                    
                    self.records_created += 1
                except Exception as e:
                   self.error = str(e)
                   self.records_created_failed.append(id)

        
            if self.request.get('form.autoactivate', None) == 'on':
                try:
                    state = api.content.get_state(obj=self.container[id])
                    if entry['image_url'] and state != 'published':
                        api.content.transition(obj=self.container[id], transition='publish')
                        self.records_activated += 1
                    if not entry['image_url'] and state == 'published':
                        api.content.transition(obj=self.container[id], transition='retract')
                        self.records_deactivated += 1
                except Exception as e:
                   self.error = str(e)
                   self.records_activated_failed.append(id)



    def _process_deletions(self):
        for entry in self.entries:
            id = entry['filmID']
            try:
                api.content.delete(self.container[id])
                self.records_deleted += 1
            except Exception as e:
               self.error = str(e)
               self.records_deleted_failed.append(id)

                
    def _process_activations(self, workflow):
        
        for entry in self.entries:
            id = entry['filmID']
            try:
                state = api.content.get_state(obj=self.container[id])
                if workflow == 'on' and state != 'published':
                    api.content.transition(obj=self.container[id], transition='publish')
                    self.records_activated += 1
                if workflow == 'off' and state == 'published':
                    api.content.transition(obj=self.container[id], transition='retract')
                    self.records_deactivated += 1
            except Exception as e:
               self.error = str(e)
               self.records_activated_failed.append(id)

    
    @property
    def portal(self):
        return api.portal.get()
    