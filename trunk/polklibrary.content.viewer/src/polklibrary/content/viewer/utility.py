from plone import api
from plone.memoize import ram
from plone.i18n.normalizer import idnormalizer
import re, time, csv, io

# used elsewhere to target


class VendorInfo:

    ALEXANDER_STREET_NAME = 'Alexander Street'
    KANOPY_NAME = 'Kanopy'
    FILMSONDEMAND_NAME = 'Films on Demand'
    SWANK_NAME = 'Swank'
    DOCUSEEK_NAME = 'Docuseek'
    ALMA_NAME = 'Catalog'
    OTHER_NAME = 'Other'

    ALEXANDER_STREET_TARGET = 'asp'
    KANOPY_TARGET = 'kan'
    FILMSONDEMAND_TARGET = 'fod'
    SWANK_TARGET = 'swa'
    DOCUSEEK_TARGET = 'doc'
    ALMA_TARGET = 'uwi'
    OTHER_TARGET = 'oth'



class Tools(object):

    def get_image_by_obj(self, o=None):
        if not o:
            o = self.context
        if o.image_url:
            if '@@images' in o.image_url:
                return o.absolute_url() + o.image_url
            return o.image_url
        return o.absolute_url() + '/++resource++polklibrary.content.viewer/missing-thumb.png'
        
    def get_image_by_brain(self, o):
        if o.image_url:
            if '@@images' in o.image_url:
                return o.getURL() + o.image_url
            return o.image_url
        return o.getURL() + '/++resource++polklibrary.content.viewer/missing-thumb.png'
        
    def get_vender_name(self, o=None):
        if not o:
            o = self.context
        if VendorInfo.ALEXANDER_STREET_TARGET in o.id.lower():   
            return VendorInfo.ALEXANDER_STREET_NAME
        elif VendorInfo.FILMSONDEMAND_TARGET in o.id.lower():   
            return VendorInfo.FILMSONDEMAND_NAME
        elif VendorInfo.KANOPY_TARGET in o.id.lower():   
            return VendorInfo.KANOPY_NAME
        elif VendorInfo.SWANK_TARGET in o.id.lower():   
            return VendorInfo.SWANK_NAME
        elif VendorInfo.ALMA_TARGET in o.id.lower():   
            return VendorInfo.ALMA_NAME
        elif VendorInfo.DOCUSEEK_TARGET in o.id.lower():   
            return VendorInfo.DOCUSEEK_NAME
        else:
            return VendorInfo.OTHER_NAME
        
    # try:
        # obj = o.getObject()
    # except:
        # pass
    # obj.absolute_url()
        
    #https://www.uwosh.edu/streaming-videos/streams/kan5693865-4693866/@@images/image
    
def BrainsToCSV(brains):
    output = io.StringIO()
    
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    
    #filmID,content_type,creator,title,date_of_publication,runtime,series_title,summary,associated_entity,geography,subject,genre
    writer.writerow(['filmID','creator','title','date_of_publication','runtime','series_title','summary','format_type','associated_entity','geography','subject_group','genre','image_url','direct_url'])
    
    for brain in brains:
        row = []
        row.append(brain.getId)
        row.append(brain.creator)
        row.append(brain.Title)
        row.append(brain.date_of_publication)
        row.append(brain.runtime)
        row.append(list(brain.series_title))
        row.append(brain.Description)
        row.append(brain.format_type)
        row.append(list(brain.associated_entity))
        row.append(list(brain.geography))
        row.append(list(brain.subject_group))
        row.append(list(brain.genre))
        # row.append([ remove_non_ascii(x) for x in brain.series_title])
        # row.append(brain.Description)
        # row.append([ remove_non_ascii(x) for x in brain.associated_entity])
        # row.append([ remove_non_ascii(x) for x in brain.geography])
        # row.append([ remove_non_ascii(x) for x in brain.subject_group])
        # row.append([ remove_non_ascii(x) for x in brain.genre])
        row.append(brain.image_url)
        row.append(brain.getRemoteUrl)
        writer.writerow(row)
        
    contents = output.getvalue()
    output.close()
    return contents
        
    
    
def text_to_tuple(text):
    if type(text) is tuple:
        return text
    lines = text.replace(u'\r', u'').split(u'\n')
    if len(lines) == 0 or lines[0] == u'':
        return ()
    return tuple(lines)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        