from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from polklibrary.content.viewer.marc_utility import process_marc

import io, re, ast, json
import pprint, logging, csv

logger = logging.getLogger("Plone")


def unicode_csv_reader(utf8_data, delimiter=',', quotechar='"', dialect=csv.excel):
    csv_reader = csv.reader(utf8_data, delimiter=delimiter, quotechar=quotechar, dialect=dialect)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]
        


class TransformerView(BrowserView):

    template = ViewPageTemplateFile("templates/transformer.pt")
    error = None

    def __call__(self):
        self.file = self.request.get('form.file.upload', None)
        if self.file:
            new_filename = self.file.filename.replace('.mrc','') + '.csv'
            if self.request.get('form.file.allcsv', None):
                csv_data = self.transform_marc_to_csv(False)
                self.request.response.setHeader("Content-type", "application/csv")
                self.request.response.setHeader("Content-Disposition", "attachment;filename=" + new_filename);
                self.request.response.setBody(csv_data, lock=True)
            if self.request.get('form.file.idcsv', None):
                csv_data = self.transform_marc_to_csv(True)
                self.request.response.setHeader("Content-type", "application/csv")
                self.request.response.setHeader("Content-Disposition", "attachment;filename=" + new_filename);
                self.request.response.setBody(csv_data, lock=True)
            
        return self.template()


    def transform_marc_to_csv(self, id_only):
        #input_stream = io.StringIO(self.file.read())
        #input_stream = io.StringIO(self.file.read().decode("utf-8"))
        header, data = process_marc(self.file.read())
        name = 'done.csv'
        #with open(name, mode='wb') as f:
        #outputstream = io.StringIO(self.file.read())
        
        outputstream = io.StringIO()
        w = csv.writer(outputstream)
        
        
        if len(header) > 0:
            if id_only:
                w.writerow([header[0]]) 
            else:
                w.writerow(header)
                    
        for row in data:
            if len(row) > 0:
                if id_only:
                    w.writerow([row[0]]) 
                else:
                    w.writerow(self.purify(row))
        return outputstream.getvalue()
    
    
    def purify(self, row):
        
        # list fixing
        row[5] = self.marc_list_cleanup(row[5])
        row[8] = self.marc_list_cleanup(row[8])
        row[9] = self.marc_list_cleanup(row[9])
        row[10] = self.marc_list_cleanup(row[10])
        row[11] = self.marc_list_cleanup(row[11])
        
        return row #done
             
    def marc_list_cleanup(self, data):
        if not data:
            return []
        if data[0] == None or data[0].replace(' ', '') == '':
            return []
        return data
    
    @property
    def portal(self):
        return api.portal.get()
    