from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from plone.i18n.normalizer import idnormalizer
from plone.memoize import ram
from Products.Five import BrowserView

import json, transaction, logging

logger = logging.getLogger("Plone")

class WSView(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        
        execute = self.request.get('execute','0')
        sw = self.request.get('startswith','&$%#*')
        replacewith = self.request.get('replace','')
        stopat = int(self.request.get('stop','500'))
        commitat = int(self.request.get('commit','500'))
    
        found = 0
        
        portal_catalog = api.portal.get_tool('portal_catalog')
        allbrains = portal_catalog()
        
        brains = list(filter(lambda x: x.getId.startswith(sw), allbrains))
        logger.info("WS Patcher Found Brains: " + str(len(brains)))
        
        if execute == '1' and replacewith:
        
            for brain in brains:
        
                newid = brain.getId.replace(sw, replacewith)
                api.content.rename(obj=brain.getObject(), new_id=newid)
                found+=1
                #logger.info("Renamed: " + str(found) + ' ' + brain.getId)
                
                if found % commitat == 0:        
                    logger.info("Commit: " + str(found))            
                    transaction.commit()
                
                if found > stopat:
                    logger.info("Commit: " + str(found))
                    transaction.commit()
                    break
                
        return 'Found: ' + str(found) + ' Stop at: ' + str(stopat)
            

    @property
    def portal(self):
        return api.portal.get()
        