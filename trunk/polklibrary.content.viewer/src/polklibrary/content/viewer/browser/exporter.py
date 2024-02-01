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


class Exporter2View(BrowserView):

    template = ViewPageTemplateFile("templates/exporter.pt")
    
    def __call__(self):
        brains = api.content.find(portal_type='polklibrary.content.viewer.models.contentrecord')
        self.output = 'No results'

        if 'form.id.submit' in self.request.form:
            self.output = self.filter_out_ids(brains)

        if 'form.private.submit' in self.request.form:
            self.output = self.filter_out_private(brains)

        return self.template()
        
    def filter_out_ids(self, brains):
        query = self.request.form.get('form.id.query','&&&')
        output = ''
        found = 0
        for brain in brains:
            if brain.getId.startswith(query):
                output += brain.getId + ',' + brain.getURL() + '\n'
                found += 1
                
        if found > 0:
            output = 'Results ' + str(found) + ':\n----------------------------------\n' + output
        else:
            output = 'Results 0'

        return output
        
    def filter_out_private(self, brains):
        found = 0
        output = ''
        for brain in brains:
            if brain.review_state == 'private':
                output += brain.getId + ',' + brain.getURL() + '\n'
                found += 1
                
        if found > 0:
            output = 'Results ' + str(found) + ':\n----------------------------------\n' + output
        else:
            output = 'Results 0'

        return output

        
    @property
    def portal(self):
        return api.portal.get()
    