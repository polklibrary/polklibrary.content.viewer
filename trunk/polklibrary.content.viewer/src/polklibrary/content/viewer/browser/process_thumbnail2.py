from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
from plone.namedfile import NamedBlobImage
import requests, re, json

from polklibrary.content.viewer.utility import VendorInfo
from bs4 import BeautifulSoup
import logging,re,time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger("Plone")

import random

class ThumbnailProcess2(BrowserView):

    logger_on = False
    GET_WAIT = 20

    def __call__(self):
        output = '\n'
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.response.setHeader('Cache-Control', 'no-cache, no-store')
        catalog = api.portal.get_tool(name='portal_catalog')
        options = webdriver.FirefoxOptions()
        options.headless = True
        options.add_argument("window-size=1920,1200")
        #user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
        #options.add_argument('user-agent={0}'.format(user_agent))
        
        profile = webdriver.FirefoxProfile()
        #profile.set_preference("general.useragent.override", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0')
        profile.set_preference("general.useragent.override", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0')


        #options.add_argument("--headless")
        
        
        if 'localhost:8080' in self.context.absolute_url(): # local testing server only
            driver = webdriver.Firefox(executable_path=r'/home/vagrant/Plone/zinstance/geckodriver', firefox_profile=profile, options=options)
        else:
            driver = webdriver.Firefox(executable_path=r'/opt/plone5.2/zeocluster/geckodriver', firefox_profile=profile, options=options)
            
        with api.env.adopt_roles(roles=['Manager']):
        
            process_index = 1
            process_limit = int(self.request.get('process_limit', '3'))
            brains = catalog.unrestrictedSearchResults(portal_type='polklibrary.content.viewer.models.contentrecord', image_url="")
            if not brains:
                brains = catalog.unrestrictedSearchResults(portal_type='polklibrary.content.viewer.models.contentrecord', image_url=None)
            
            if self.request.get('random', '1') == '1':
                brains = list(brains)
                random.shuffle(brains)
            
            logger.info('Thumbnail Process Left: ' + str(len(brains)))
            for brain in brains:
                if process_index > process_limit:
                    break;
                process_index += 1
                    
                if VendorInfo.ALEXANDER_STREET_TARGET in brain.getId:
                    output += self.process_aso(driver, brain)
                if VendorInfo.FILMSONDEMAND_TARGET in brain.getId:
                    output += self.process_fod(driver, brain)
                if VendorInfo.KANOPY_TARGET in brain.getId:
                    output += self.process_kan(driver, brain)
                if VendorInfo.DOCUSEEK_TARGET in brain.getId:
                    output += self.process_doc(driver, brain)
                time.sleep(2)
                
            output += '\n\n Thumbnails Left: ' + str(len(brains)) + '\n'
            output += ' Deletion Option: ' + self.request.get('deletes', '0') + '\n\n'
            
        time.sleep(5)
        driver.quit()
                
        return output
        
        
        
    def process_aso(self, driver, brain):
        do_deletes = self.request.get('deletes', '0')
        output = 'Process ASO: ' + brain.getURL()
       
        withoutproxy = brain.getRemoteUrl.replace('https://www.remote.uwosh.edu/login?url=', '')
        driver.set_window_size(1920, 1080)
        driver.get(withoutproxy)
        output += ' -- Retreive: ' + withoutproxy
        time.sleep(int(self.request.get('wait', '10')))
        obj = brain.getObject()  
        
        
        try:
            player_element = None
            
            try:
                player_element = driver.find_element_by_css_selector(".nuvo-player")
            except:
                player_element = driver.find_element_by_css_selector(".nvplyr-video-splash__screenshot")
                
            thumbnail_attr = player_element.get_attribute("style")
            thumbnail_url = re.search("(?P<url>https?://[^\\s'\"]+)", thumbnail_attr).group("url")
            if thumbnail_url:
                obj.image_url = thumbnail_url
                obj.reindexObject()
                output += ' Thumbnail saved ' + thumbnail_url
            
                if brain.review_state != 'published' and obj.image_url != None and obj.image_url != '':
                    with api.env.adopt_roles(roles=['Manager']):
                        api.content.transition(obj=obj, transition='publish')
                    output += ' -- Published'
            
        except Exception as e:
            if do_deletes == '1':
                api.content.delete(obj=obj)
                output += ' -- Deleting'
            output += ' -- Error: ' + str(e)

        return output + '\n'
        
    def process_fod(self, driver, brain):
        do_deletes = self.request.get('deletes', '0')
        output = 'Process FOD: ' + brain.getURL()       
        withoutproxy = brain.getRemoteUrl.replace('https://www.remote.uwosh.edu/login?url=', '')
        driver.set_window_size(1920, 1080)
        driver.get(withoutproxy)
        output += ' -- Retreive: ' + withoutproxy
        time.sleep(int(self.request.get('wait', '10')))
        
        try:
            #v1 attempt
            try:
                driver.switch_to.frame(driver.find_element_by_css_selector("iframe.mwEmbedKalturaIframe"))
                time.sleep(5)
                player_element = driver.find_element_by_css_selector("img.playerPoster")
            except:
                #v2 attempt
                player_element = driver.find_element_by_css_selector("#ctl00_BodyContent_fpImg")
                
            thumbnail_url = player_element.get_attribute("src")
            
            if thumbnail_url:
                obj = brain.getObject()  
                obj.image_url = thumbnail_url
                obj.reindexObject()
                output += ' Thumbnail saved ' + thumbnail_url
            
                if brain.review_state != 'published' and obj.image_url != None and obj.image_url != '':
                    with api.env.adopt_roles(roles=['Manager']):
                        api.content.transition(obj=obj, transition='publish')
                    output += ' -- Published'
            
        except Exception as e:
            if do_deletes == '1':
                api.content.delete(obj=obj)
                output += ' -- Deleting'
            output += ' -- Error: ' + str(e)
        
        return output + '\n'
        
    def process_kan(self, driver, brain):
        return brain.getURL() + ' KAN not setup \n'
          
          
    def process_doc(self, driver, brain):
        do_deletes = self.request.get('deletes', '0')
        output = 'Process DOC: ' + brain.getURL()
       
        withoutproxy = brain.getRemoteUrl.replace('https://www.remote.uwosh.edu/login?url=', '')
        driver.set_window_size(1920, 1080)
        driver.get(withoutproxy)
        output += ' -- Retreive: ' + withoutproxy
        time.sleep(int(self.request.get('wait', '10')))
        obj = brain.getObject()  
        
        try:
            time.sleep(5)
            picture_element = driver.find_element_by_css_selector("picture.vjs-poster > img")
            print('picture element')
            print(picture_element)
            thumbnail_url = picture_element.get_attribute("src")
            print(thumbnail_url)
            
            if thumbnail_url:
                obj.image_url = thumbnail_url
                obj.reindexObject()
                output += ' Thumbnail saved ' + thumbnail_url
            
                if brain.review_state != 'published' and obj.image_url != None and obj.image_url != '':
                    with api.env.adopt_roles(roles=['Manager']):
                        api.content.transition(obj=obj, transition='publish')
                    output += ' -- Published'
            
        except Exception as e:
            output += ' -- Failed first attempt: ' + str(e)

            try:
                time.sleep(5)
                player_element = driver.find_element_by_css_selector("video[poster]")
                print('player element')
                print(player_element)
                thumbnail_url = player_element.get_attribute("poster")
                print(thumbnail_url)
                
                if thumbnail_url:
                    obj.image_url = thumbnail_url
                    obj.reindexObject()
                    output += ' Thumbnail saved ' + thumbnail_url
                
                    if brain.review_state != 'published' and obj.image_url != None and obj.image_url != '':
                        with api.env.adopt_roles(roles=['Manager']):
                            api.content.transition(obj=obj, transition='publish')
                        output += ' -- Published'
                
            except Exception as ee:
                if do_deletes == '1':
                    api.content.delete(obj=obj)
                    output += ' -- Deleting'
                output += ' -- Error: ' + str(ee)

        return output + '\n'
          
        
        
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
        
        
    @property
    def portal(self):
        return api.portal.get()
        
        