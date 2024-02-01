# from plone import api
# from plone.protect.interfaces import IDisableCSRFProtection
# from Products.Five import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from zope.interface import alsoProvides
# from plone.namedfile import NamedBlobImage
# import requests, re, json

# from polklibrary.content.viewer.utility import ResourceEnhancer, ALEXANDER_STREET_NAME, KANOPY_NAME, FILMSONDEMAND_NAME, SWANK_NAME
# #from BeautifulSoup import BeautifulSoup
# from bs4 import BeautifulSoup
# import logging,transaction,re

# logger = logging.getLogger("Plone")

# class ThumbnailProcess(BrowserView):

    # logger_on = False

    # def __call__(self):
        # loginfo = ''
        # alsoProvides(self.request, IDisableCSRFProtection)
        # title = 'No results'
        # error_msg = ''    
        # catalog = api.portal.get_tool(name='portal_catalog')
        
        
        # with api.env.adopt_roles(roles=['Manager']):
            # recheck = self.request.form.get('recheck', '0')
            # if recheck == '1':
                # brains = catalog.searchResults(portal_type='polklibrary.content.viewer.models.contentrecord', image_url = '/++resource++polklibrary.content.viewer/missing-thumb.png') # bypass security
            # else:
                # brains = catalog.searchResults(portal_type='polklibrary.content.viewer.models.contentrecord', image_url="")
                # #brains = api.content.find(portal_type='polklibrary.content.viewer.models.contentrecord', image_url="")
                # print("else")
                
            # print("Brains: " + str(len(brains)))
            # if brains:
                # brain = brains[0]
                # obj = brain.getObject()
                # title = obj.Title()
                # obj.image_url = '/++resource++polklibrary.content.viewer/missing-thumb.png'
                
                # thumburl = ''
                # try:
                    # # Get Thumbnail
                    # if obj.image == None:
                        # enchanced_data = ResourceEnhancer(obj.id, obj.title)
                        
                        # print("Get Thumbnail")
                        
                        # # add plugin option?
                        # #req = requests.get(enchanced_data['base_url'], verify=False, timeout=15)
                        # #html = req.text
                        
                        # if enchanced_data['name'] == ALEXANDER_STREET_NAME:
                            # thumburl = self.get_alexander_thumbnail_url(enchanced_data)
                        # elif enchanced_data['name'] == KANOPY_NAME:
                            # thumburl = self.get_kanopy_thumbnail_url(enchanced_data)
                        # elif enchanced_data['name'] == FILMSONDEMAND_NAME:
                            # thumburl = self.get_fod_thumbnail_url(enchanced_data)
                        # elif enchanced_data['name'] == SWANK_NAME:
                            # thumburl = self.get_swank_thumbnail_url(enchanced_data)
                        
                        # print ("target thumburl: " + thumburl)
                        
                        # loginfo += " -- Thumbnail: " + thumburl
                        # #return; # stop execution for testing
                        
                        # if thumburl:
                            # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

                            # reqthumb = requests.get(thumburl, headers=headers, timeout=15, allow_redirects=True)
                            
                            
                            
                            
                            # binary = reqthumb.content
                            # loginfo += " -- BINARY: " + str(len(binary))
                            # if len(binary) > 5000:
                                # obj.image = NamedBlobImage(data=reqthumb.content, filename=u'thumb.jpg')
                                # obj.image_url = '/@@download/image/thumb.jpg'
                            # else:
                                # obj.image_url = '/++resource++polklibrary.content.viewer/missing-thumb.png'
                        # else:
                            # obj.image_url = '/++resource++polklibrary.content.viewer/missing-thumb.png'
                            
                                    
                            
                # except Exception as e:
                    # error_msg = '!! RETRIEVE ERROR: ' + str(e) + ' - ' + brains[0].getPath() + '   URL:' + thumburl
                 
                # try:
                    # if brain.review_state != 'published' and obj.image != None:
                        # with api.env.adopt_roles(roles=['Manager']):
                            # api.content.transition(obj=obj, transition='publish')
                            
                # except Exception as e:
                    # error_msg = '!! PUBLISH ERROR: ' + str(e) + ' - ' + brains[0].getPath()  + '   URL:' + thumburl
                        
                # # Reindex catalog    
                # with api.env.adopt_roles(roles=['Manager']):
                    # obj.reindexObject()
            
            # if self.logger_on:
                # logger.info(loginfo)
                # logger.info(error_msg)
                
        # return 'Processed Thumbnail: ' + title + ' Remaining: ' + str((len(brains)-1)) + '  INFO: ' + error_msg

        
    # def get_kanopy_thumbnail_url(self, enchanced_data):
        # print("KANOPY PROCESS - function last checked 6/21/2021")
        # url = 'https://uwosh.kanopy.com/node/' + enchanced_data['id'] + '/preview'
        # req = requests.get(url, verify=False, timeout=15)
        # html = req.text
        
        # soup = BeautifulSoup(html)
        # element = soup.select_one('span.image.fluid img')
        
        # try:
            # return element.get('src')
        # except Exception as e:
            # print("ERROR: " + str(e))
        # return ''
        
    # def get_fod_thumbnail_url(self, enchanced_data):
        # print("FOD PROCESS - function last checked 6/21/2021")
        # return 'https://fod.infobase.com/image/' + str(enchanced_data['id'])
        
                
    # def get_swank_thumbnail_url(self, enchanced_data):
        # print('SWANK PROCESS')
        
        # return ''

        
        
    # def get_alexander_thumbnail_url(self, enchanced_data):
        # print("ASP PROCESS - function last checked 6/21/2021")
        
        # url = 'https://search.alexanderstreet.com/view/work/bibliographic_entity|video_work|' + enchanced_data['id']
        # req = requests.get(url, verify=False, timeout=15)
        # html = req.text
        
        # soup = BeautifulSoup(html)
        # scripts = soup.findAll(lambda tag: (tag.name == 'script' and len(tag.attrs) == 0) and 'original.jpg' in tag.text)
        # if scripts:
            # try:
                # text = scripts[0].getText().lstrip('jQuery.extend(Drupal.settings,').rstrip(');')
                # data = json.loads(text)
                # return data['ASP']['Lazr']['Uniplayer']['timeline']['chunkData']['infoPanelFullSizeImageUrl']
            # except:
                # pass
        # else:
            # try:
                # scripts = soup.findAll('script', {'type':'application/ld+json'})
                # if scripts:
                    # data = json.loads(scripts[0].getText())
                    # return data['thumbnail']['contentUrl'].replace('fit-140x140.jpg', 'fit-140x140.jpg')
            # except:
                # pass
        # return ''
        
        
    # @property
    # def portal(self):
        # return api.portal.get()
        
        