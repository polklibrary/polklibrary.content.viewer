# from plone import api
# from plone.i18n.normalizer import idnormalizer
# from Products.Five import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from zope.component import getUtility, getMultiAdapter
# from zope.container.interfaces import INameChooser
# import csv, io, re, ast, json
# import pprint, ftfy, logging

# logger = logging.getLogger("Plone")


# def unicode_csv_reader(utf8_data, delimiter=',', quotechar='"', dialect=csv.excel):
    # csv_reader = csv.reader(utf8_data, delimiter=delimiter, quotechar=quotechar, dialect=dialect)
    # for row in csv_reader:
        # yield [unicode(cell, 'utf-8') for cell in row]
        


# class ImporterView(BrowserView):

    # template = ViewPageTemplateFile("templates/importer.pt")
    
    # SUBDELIMITER = u';'
    # required_add_update_headings = ['filmID', 
                                    # 'creator', 
                                    # 'title', 
                                    # 'date_of_publication', 
                                    # 'runtime', 
                                    # 'series_title', 
                                    # 'summary', 
                                    # 'format_type',
                                    # 'associated_entity', 
                                    # 'geography', 
                                    # 'subject_group', 
                                    # 'genre']
                                    
    # required_delete_headings  = ['filmID']  
    # required_activation_headings  = ['filmID']  
    
    # def __call__(self):
                 
        # self.error = ''
        # self.records_created = 0
        # self.records_created_failed = []
        # self.records_updated = 0
        # self.records_updated_failed = []
        # self.records_deleted = 0
        # self.records_deleted_failed = []
        # self.records_activated = 0
        # self.records_activated_failed = []
        
        # target_container = self.request.get('form.container.type', '%%%')
        # containers = api.content.find(self.portal, portal_type='Folder', id=target_container)
        # self.file = self.request.get('form.file.upload', None)
            
        # if self.file and containers:
            # self.container = containers[0].getObject()
            # if self.request.get('form.file.submit', None):
                # self.handle_add_update()
            # if self.request.get('form.file.delete', None):
                # self.handle_delete()
            # if self.request.get('form.file.activate', None):
                # self.handle_activations('on')
            # if self.request.get('form.file.deactivate', None):
                # self.handle_activations('off')
            
        # return self.template()

        
        
    # def handle_activations(self, workflow):
        # keys = []
        # sio = io.StringIO(self.file.read().decode("utf-8"))
        # reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel_tab)
        # for row in reader:
            # if not keys:
                # keys = [x.strip() for x in row]
                # if keys != self.required_activation_headings:
                    # self.error = 'Mismatch header in Activate/Deactivate CSV'
                    # return
            # else:
                # for rawcontent in row:
                    # id = idnormalizer.normalize(self.universal_string_cleanup(rawcontent))
                    # try:
                        # state = api.content.get_state(obj=self.container[id])
                        # if workflow == 'on' and state != 'published':
                            # api.content.transition(obj=self.container[id], transition='publish')
                        # if workflow == 'off' and state == 'published':
                            # api.content.transition(obj=self.container[id], transition='retract')
                        # self.records_activated += 1
                    # except Exception as e:
                       # self.error = str(e)
                       # self.records_activated_failed.append(id)
    

        
    # def handle_add_update(self):
        # keys = []
        # sio = io.StringIO(self.file.read().decode("utf-8"))
        # reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel)
        # #reader = unicode_csv_reader(sio, delimiter=',', quotechar='"', dialect=csv.excel)
        # for row in reader:
            # if not keys:
                # for key in row:
                    # key = key.strip()
                    # if key in self.required_add_update_headings:
                        # keys.append(key)
                    # else:
                        # self.error = 'Mismatch header in Add/Update CSV on key: ' + key
                        # return
            # else:
                # index = 0
                # entry = { }
                # for rawcontent in row:
                    # entry[keys[index]] = self.clean_empty(rawcontent)
                    # index+=1
                # entry = self.purify_record(entry)
                # self.process_create_or_update(entry)
    
    
    # def purify_record(self, entry):
        # entry['filmID'] = self.universal_string_cleanup(entry['filmID'])
        # entry['creator'] = self.universal_string_cleanup(entry['creator'], cleanup_regex=u'[\.]$')
        
        # #entry['title'] = entry['title'].replace(u'[electronic resource]', u'').split(u'/')[0]
        # #entry['title'] = entry['title'].replace(u' : ',u': ').replace(u' :', u': ')
        # entry['title'] = self.universal_string_cleanup(entry['title'], cleanup_regex=u'[\.\:]$')   
        
        # entry['date_of_publication'] = self.universal_string_cleanup(entry['date_of_publication'])
        # entry['runtime'] = self.universal_string_cleanup(entry['runtime'])
        # entry['summary'] = self.universal_string_cleanup(entry['summary'])
        # entry['format_type'] = self.universal_string_cleanup(entry['format_type'])
        
        # entry['series_title'] = self.universal_list_to_tuple_cleanup(entry['series_title'], cleanup_regex=u'[\.]$')
        # entry['associated_entity'] = self.universal_list_to_tuple_cleanup(entry['associated_entity'], cleanup_regex=u'[\.\,]$')
        # entry['geography'] = self.universal_list_to_tuple_cleanup(entry['geography'], cleanup_regex=u'[\.]$')
        
        
        # entry['subject_group'] = self.universal_list_to_tuple_cleanup(entry['subject_group'], cleanup_regex=u'[\.]$')
        
        # entry['genre'] = self.universal_list_to_tuple_cleanup(entry['genre'], cleanup_regex=u'[\.]$')
        
        # return entry
    
    # def universal_list_to_tuple_cleanup(self, entry, cleanup_regex=u'', cleanup_replace=u''):
        # entry = entry.strip()
        
        # if entry.startswith(u'[') and entry.endswith(u']'): # it is a list
            # items = ast.literal_eval(entry.replace(u' ; ',u',').replace(u'; ',u','))
        # else: # it is a string
            # items = entry.split(self.SUBDELIMITER)
            
        # cleaned_items = set()
        # for item in items:
            # if item and item.lower() != u'none':
                # cleaned_items.add(self.universal_string_cleanup(item, cleanup_regex, cleanup_replace))
        # return tuple(cleaned_items)
        
    # def universal_string_cleanup(self, entry, cleanup_regex=u'', cleanup_replace=u''):
        # entry = entry.strip()
        # regex = re.compile(cleanup_regex)
        # try:
            # #if type(entry) != unicode:
            # #entry = entry.decode('utf-8')
            # return ftfy.fix_text(regex.sub(cleanup_replace, entry))
        # except Exception as e:
            # logger.info("ERROR: " + str(e) + ' ' + entry)
            # print("ERROR: " + str(e) + ' ' + entry)
            # return regex.sub(cleanup_replace, entry)
    
    # def clean_empty(self, text):
        # if text == u'' or text.lower() == u'none' or text.lower() == u'[none]':
            # return u''
        # return text
    
    # def process_create_or_update(self, entry):
        # id = idnormalizer.normalize(entry['filmID'])
        # brains = api.content.find(context=self.container, 
                               # portal_type='polklibrary.content.viewer.models.contentrecord',
                               # id=id,
        # )

        # # Update
        # if len(brains) > 0:
            # try:
                # obj = brains[0].getObject()
                # obj.title=entry['title']
                # obj.creator=entry['creator']
                # obj.date_of_publication=entry['date_of_publication']
                # obj.runtime=entry['runtime']
                # obj.series_title=entry['series_title']
                # obj.description=entry['summary']
                # obj.format_type=entry['format_type']
                # obj.associated_entity=entry['associated_entity']
                # obj.geography=entry['geography']
                # obj.subject_group=entry['subject_group']
                # obj.reindexObject()
                
                # self.records_updated += 1
            # except Exception as e:
               # self.error = str(e)
               # self.records_created_failed.append(id)
            
        # # Create
        # else:
            # try:
                # api.content.create(container=self.container, 
                                   # type='polklibrary.content.viewer.models.contentrecord', 
                                   # safe_id=False, 
                                   # id=id, 
                                   # title=entry['title'], 
                                   # creator=entry['creator'], 
                                   # date_of_publication=entry['date_of_publication'], 
                                   # runtime=entry['runtime'], 
                                   # series_title=entry['series_title'], 
                                   # description=entry['summary'], 
                                   # format_type=entry['format_type'], 
                                   # associated_entity=entry['associated_entity'],  
                                   # geography=entry['geography'],  
                                   # subject_group=entry['subject_group'], 
                                   # genre=entry['genre'], 
                                   # image_url="",
                # )
                
                # self.records_created += 1
            # except Exception as e:
               # self.error = str(e)
               # self.records_created_failed.append(id)

               
               
    # def handle_delete(self):
        # keys = [];
        # sio = io.StringIO(self.file.read().decode("utf-8"))
        # reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel_tab)
        # for row in reader:
            # if not keys:
                # keys = [x.strip() for x in row]
                # if keys != self.required_delete_headings:
                    # self.error = 'Mismatch header in Delete CSV'
                    # return
            # else:
                # for rawcontent in row:
                    # id = idnormalizer.normalize(self.universal_string_cleanup(rawcontent))
                    # try:
                        # api.content.delete(self.container[id])
                        # self.records_deleted += 1
                    # except Exception as e:
                       # self.error = str(e)
                       # self.records_deleted_failed.append(id)
    
    # @property
    # def portal(self):
        # return api.portal.get()
    