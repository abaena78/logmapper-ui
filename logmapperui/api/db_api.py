# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 13:09:21 2018

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************
    
import os
import logging
import datetime

import pandas as pd

    
import logmappercommon.utils.postgres_util as db
import logmappermaster.dao.master_dao as masterdao
from logmapperui.api.base import LogMapperApi

#%%
"""
Global Initialization. Constants definitions.
"""

logger = logging.getLogger(__name__)



#%%
class LogMapperApiDb(LogMapperApi):
    
    def __init__(self):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        #self.conn = db.connectDbFullName(dbfilepath) 
        self.conn = db.connectDb()
        self.cursor = self.conn.cursor()
        
    def close(self):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        self.cursor.close()
        self.conn.close()        
        
    
    def findHosts(self):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        return masterdao.findHosts(self.cursor)
        
    

    def findComponentsByHostId(self, hostId):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        #TODO AGENTiD O hOSTiD
        return masterdao.findComponentsByHostId(self.cursor, hostId)
    
    
    def findSourcesByComponentId(self, componentId):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        #TODO AGENTiD O hOSTiD
        return masterdao.findSourcesByComponentId(self.cursor, componentId)     
    
    
    
    
 
    
    def getNetworkGraphData(self, start, end):
        """
        ***********************************************************************
        
        ***********************************************************************
        """
        nodesData = []
        edgesData = []
 
#        limit = 10       
#        hosts = masterdao.findHosts(self.cursor)
#        for host in hosts:
#            components = masterdao.findComponentsByHostId(self.cursor, host['id'])
#            for component in components:
#                nodesComponent = []
#                paths = masterdao.findlogPathsForNetwork(self.cursor, component['componentId'], start, end, limit) 
#                for path in paths:
#                    pathId = path[2]
#                    rowperformance = masterdao.findlogPathPerformance(self.cursor, pathId, start, end)
#                    rowdetail = masterdao.findlogPathDetail(self.cursor, pathId)
#                    
#                    nodesComponent.append({
#                            'node' : path[0] ,
#                            'key' : rowdetail[0]
#                            })
#                    nodesComponent.append({
#                            'node' : path[1], 
#                            'key' : rowdetail[1]
#                            })    
#                   
#                    edgesData.append({
#                            'n1' : path[0],
#                            'n2' : path[1],
#                            'ref' : rowdetail[2],
#                            'performance' : rowperformance[0]
#                            })
#    
#                remoteCalls = masterdao.findRemoteCallsByComponentId(self.cursor,reader['componentId'])
#                for remoteCallrow in remoteCalls:
#                    if remoteCallrow[0] == reader['componentId']:
#                        nodesComponent.append({
#                            'node' : remoteCallrow[1], 
#                            'key' : remoteCallrow[2]
#                        })
#                    if remoteCallrow[3] == reader['componentId']:
#                        nodesComponent.append({
#                            'node' : remoteCallrow[4], 
#                            'key' : remoteCallrow[5]
#                        })    
#                    
#                        
#                nodesData.append({
#                        'nodes' : nodesComponent,
#                        'component' : reader['componentKey']
#                        })
        
        
        components = masterdao.findComponents(self.cursor)
        for component in components:
            row = masterdao.findPerformanceAvgMeasures(self.cursor, component['id'], start, end)
            nodesData.append({
                            'name' : component['name'] ,
                            'key' : component['key'],
                            'x' : component['x'],
                            'y' : component['y'],
                            'performanceMin' : row[1]
                            })
                       
        remoteCalls = masterdao.findRemoteCalls(self.cursor)
        for rc in remoteCalls:
            edgesData.append({
                                'n1' : rc[0],
                                'n2' : rc[1],
                                'ref' : 0,
                                'performance' : 0
                                })
    
        

        return {
                'start' : start,
                'end' : end,
                'nodesData' : nodesData,
                'edgesData' : edgesData 
                }
        
    
    def getPerformanceData(self, start, end):
        """
        ***********************************************************************
        
        ***********************************************************************
        """   
        performanceData = []
        
        hosts = masterdao.findHosts(self.cursor)
        for host in hosts:
            components = masterdao.findComponentsByHostId(self.cursor, host['id'])
            for component in components:
                results = masterdao.findPerformanceMeasures(self.cursor, component['id'], start, end)
                performanceData.append({
                            'instance' : component['name'],
                            'results' : results
                        })

        return {
                'start' : start,
                'end' : end,
                'performanceData' : performanceData 
                }     


    def getHostData(self, hostId, start, end):
        """
        ***********************************************************************
        
        ***********************************************************************
        """
        logger.debug("getHostData:"+str(start)+" - "+str(end))
        results = masterdao.findHostData(self.cursor, hostId, start, end)
        return {
                'start' : start,
                'end' : end,
                'results' : results 
                }  

    def getComponentData(self, componentId, start, end):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        logger.debug("getComponentData:"+str(start)+" - "+str(end))
        results = masterdao.findPerformanceMeasures(self.cursor, componentId, start, end)

        return {
                'start' : start,
                'end' : end,
                'performance' : results 
                } 
        
    def getSourceData(self, sourceId, start, end):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        logger.debug("getSourceData:"+str(start)+" - "+str(end))
        
        data = {
                'start' : start,
                'end' : end
                }         
        
        types = masterdao.findMeasuresTypesBySourceId(self.cursor, sourceId)
        
        for t in types:
            m = masterdao.findMeasuresBySourceIdAndTypeId(self.cursor, t['typeId'], sourceId, start, end)
            data[t['name']] = m
            
        return data
    
    
    def getComponentState(self, componentId, start, end):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        logger.debug("getComponentData:"+str(start)+" - "+str(end))
        results = masterdao.findPerformanceAvgMeasures(self.cursor, componentId, start, end)

        return {
                'start' : start,
                'end' : end,
                'performance' : results[0], 
                'performanceMin' : results[1],
                'predicted' : results[2],
                'anomaly' : results[3],
                }    
        
        

    def getLowPerformancePaths(self, componentId, start, end):         
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        logger.debug("getComponentData:"+str(start)+" - "+str(end))
        r = masterdao.findLogPathsOrderByLowPerformance(self.cursor, componentId, start, end)

#        return {
#                'start' : start,
#                'end' : end,
#                'results' : data 
#                } 
        
        logger.debug(r['columns'])
        
        df = pd.DataFrame(r['data'])
        df.columns = r['columns']
        return df
               
        
           

#%%

if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')  

#    cfg.createDefaultConfigfile()
#    config=cfg.loadConfig()   
    
#==============================================================================
    start = datetime.datetime(2018,5, 3, 10, 0, 0)
    end = datetime.datetime(2018, 5, 3, 11, 5, 0)    

    
    logMapperApi = LogMapperApiDb()
    
#    agents = logMapperApi.findHosts()
#    
#    for agent in agents:
#        readers = logMapperApi.findComponentsByHostId(agent['id'])
#        for reader in readers:
#            print(str(reader))
    
#    response = logMapperApi.getNetworkGraphData(start, end)
#    logger.debug(str(response))
 
    response = logMapperApi.getPerformanceData(start, end)
    logger.debug(str(response))   
#    
    hostId = 1
    componentId = 4
    
#    response = logMapperApi.getInstancePerformanceData(hostId, componentId, start, end)
#    logger.debug(str(response)) 
#
#    response = logMapperApi.getInstanceData(hostId, componentId, start, end)
#    logger.debug(str(response)) 
    
    df = logMapperApi.getLowPerformancePaths( componentId, start, end)
    logger.debug(str(df))     
    
    
    logMapperApi.close()
    
    print("End module execution")    