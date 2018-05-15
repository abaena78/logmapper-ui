# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 09:10:10 2018

@author: abaena
"""

"""
https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.html

"""


#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************

import logging
import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#%%
"""
Global Initialization. Constants definitions.
"""

logger = logging.getLogger(__name__)

#%%
def getLineExample(ax, vmax = 10):
    x = np.arange(0, vmax, 0.2)
    y = np.sin(x)
    ax.plot(x, y)
    
def getBarExample(ax):
    x = ['device', 'entity', 'dddf']
    ind = np.arange(3)  # the x locations for the groups
    width = 0.35       # the width of the bars
    y1 = [2, 3, 5]
    y2 = [2, 5, 1]
    ax.bar(ind-width/2, y1, width=width,color='b',align='center', label='Actual')  
    ax.bar(ind+width/2, y2, width=width,color='r',align='center', label='Predicted')
    ax.set_xticks(ind)
    ax.set_xticklabels(x)
    ax.legend(loc='upper center', shadow=True, fontsize='x-large')
    
def getPieExample(ax):
    x = ['device', 'entity', 'dddf']
    y1 = [2, 3, 5]
    ax.pie(y1, labels=x, autopct='%1.1f%%', shadow=False, startangle=90)
    ax.axis('equal') 


def showPlot(function):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    function(ax)
    
    
class PerformancePlotMaker():
    
    def __init__(self, performanceData):

        components=[]
        averages = []
        df = pd.DataFrame()
        for data in performanceData:
            name = data['instance']
            components.append(name)
            tdf = pd.DataFrame(data['results'], columns=['date', 'performance_'+name, 'performance_min_'+name, 'predicted_'+name, 'anomaly_'+name] )
            tdf.date = pd.to_datetime(tdf.date)
            tdf.set_index('date', inplace=True)
            averages.append(tdf.mean().tolist())
            df = pd.concat([df, tdf], axis='columns')   
            
        self.components = components
        self.averages = averages
        self.df = df
        
    def getPlotPerformance(self, ax):  
        limit = len(self.components)
        tdf = self.df.iloc[:,range(0, limit, 3)]     
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line',ylim=(0, 1.2))
        ax.grid()

    def getPlotAverages(self, ax):  
        tdf=pd.DataFrame(self.averages, columns=['perf', 'perf_min', 'pred', 'anom']) 
        tdf['components'] = pd.Series(self.components, name='components')
        tdf.set_index('components', inplace=True)
        tdf.plot.bar(ax = ax)
#        ax.grid()
        

class HostPlotMaker():
    
    def __init__(self, hostData):
        
        columns=[
          'date',
          'cpu',
          'cpu_user',
          'cpu_sys',
          'cpu_idle',          
          'mem',
          'swap',
          'diskusage',
          'pids',
          'cnxs',
          'users',         
          'openfiles', 
          'openfiles_rate',         
          'disk_io_rate_w',
          'disk_io_rate_r',         
          'net_io_rate_in',
          'net_io_rate_out',
          'net_err_rate_in',
          'net_err_rate_out',
          'net_drop_rate_in',
          'net_drop_rate_out',                
                ]
        tdf = pd.DataFrame(hostData, columns=columns)
        tdf.date = pd.to_datetime(tdf.date)
        tdf.set_index('date', inplace=True)
        self.dfData = tdf 
        
    def getPlotCpu(self, ax):
        tdf = self.dfData.iloc[:,0:4]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line', ylim=(0, 100))
        ax.grid()

    def getPlotMem(self, ax):
        tdf = self.dfData.iloc[:,4:6]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line', ylim=(0, 100))        
        ax.grid()  
        
    def getPlotNet(self, ax):
        tdf = self.dfData.iloc[:,14:16]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line')        
        ax.grid()   
        
    def getPlotDisk(self, ax):
        tdf = self.dfData.iloc[:,12:14]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line')        
        ax.grid()    
        
    def getPlotNetError(self, ax):
        tdf = self.dfData.iloc[:,16:20]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line')        
        ax.grid() 
        
    def getPlotCountersFiles(self, ax):
        c=self.dfData.columns
        columnIndexList=[
                c.get_loc('openfiles')
                ]
        tdf = self.dfData.iloc[:,columnIndexList]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line')        
        ax.grid() 
        
    
class ComponentPlotMaker():
    
    def __init__(self, componentData):
        
        df = pd.DataFrame(componentData['performance'], columns=['date', 'performance_avg', 'performance_min', 'predicted', 'anomaly'] )
        df.date = pd.to_datetime(df.date)
        df.set_index('date', inplace=True)
        self.dfPerformance = df
        
        
    def getPlotPerformance(self, ax):
        tdf = self.dfPerformance.iloc[:,0:3]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line', ylim=(0, 1.2))
        ax.grid() 
        
    def getPlotPerformanceMean(self, ax):
        self.dfPerformance.mean().plot.bar(ax=ax)
        ax.grid()         
        
    def getPlotAnomaly(self, ax):
        tdf = self.dfPerformance.iloc[:,3:4]
        if len(tdf) > 0:
            tdf.plot(ax=ax, kind='line', linewidth=5, marker='o', ylim=(-1, 1))
        
        ax.grid()        
        
    def getPlotAnomalyPie(self, ax):
        typical = self.dfPerformance['anomaly'][self.dfPerformance['anomaly']==1].count()
        anomaly = self.dfPerformance['anomaly'][self.dfPerformance['anomaly']==-1].count()
        x = ['typical', 'anomaly']
        y1 = [typical, anomaly]
        ax.pie(y1, labels=x, autopct='%1.1f%%', shadow=False, startangle=90)
        ax.axis('equal')  
        

#    def getPlotMem(self, ax):
#        tdf = self.dfData.iloc[:,4:6]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid()  
#        
#    def getPlotNet(self, ax):
#        tdf = self.dfData.iloc[:,14:16]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid()   
#        
#    def getPlotDisk(self, ax):
#        tdf = self.dfData.iloc[:,12:14]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid()    
#        
#    def getPlotNetError(self, ax):
#        tdf = self.dfData.iloc[:,16:20]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid() 
#
#    def getPlotCounters(self, ax):
#        c=self.dfData.columns
#        columnIndexList=[
#                c.get_loc('pids_avg'),
#                c.get_loc('cnxs_avg'),
#                ]
#        tdf = self.dfData.iloc[:,columnIndexList]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid() 
#        
#    def getPlotCountersFiles(self, ax):
#        c=self.dfData.columns
#        columnIndexList=[
#                c.get_loc('openfiles_avg')
#                ]
#        tdf = self.dfData.iloc[:,columnIndexList]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid() 
#        
#    def getPlotEventsLog(self, ax):
#        c=self.dfData.columns
#        columnIndexList=[
#                c.get_loc('LOGEVENT-CRITICAL'),
#                c.get_loc('LOGEVENT-ERROR'),
#                c.get_loc('LOGEVENT-WARNING'),
#                ]
#        tdf = self.dfData.iloc[:,columnIndexList]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid()    
#        
#    def getPlotEventsLogBar(self, ax):
#        c=self.dfData.columns
#        columnIndexList=[
#                c.get_loc('LOGEVENT-CRITICAL'),
#                c.get_loc('LOGEVENT-ERROR'),
#                c.get_loc('LOGEVENT-WARNING'),
#                ]
#        tdf = self.dfData.iloc[:,columnIndexList].sum()
#        if len(tdf) > 0:
#            tdf.plot.bar()        
#        ax.grid()         
#        
#    def getPlotEventsComponent(self, ax):
#        c=self.dfData.columns
#        columnIndexList=[
#                c.get_loc('COMPONENTEVENT-LOGRECORDS'),
#                c.get_loc('COMPONENTEVENT-THREADS')
#                ]
#        tdf = self.dfData.iloc[:,columnIndexList]
#        if len(tdf) > 0:
#            tdf.plot(ax=ax, kind='line')        
#        ax.grid()
        
class SourceMeasuresPlotMaker():
    
    def __init__(self, componentData):
        
        self.dataframes = {} 
        for name in componentData.keys():
            if name == 'start' or name == 'end':
                continue
            self.__createDataFrame(componentData, name)
        
    def __createDataFrame(self, componentData, name):
        df = pd.DataFrame(componentData[name], columns=['date', name] )
        df.date = pd.to_datetime(df.date)
        df.set_index('date', inplace=True)
        self.dataframes[name]=df        
        
    def getLinePlot(self, ax, name):
        df = self.dataframes[name]
        if len(df) > 0:
            df.plot(ax=ax, kind='line')
        ax.grid()  
        
    def getBarPlot(self, ax, name):
        df = self.dataframes[name]
        if len(df) > 0:
            df.plot(ax=ax, kind='bar')
        ax.grid()

    def getScatterPlot(self, ax, name):
        df = self.dataframes[name]
        if len(df) > 0:
            df.plot(ax=ax, kind='scatter')
        ax.grid()        
         

if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')     

#    showPlot(getLineExample)
#    showPlot(getBarExample)
#    showPlot(getPieExample)
    
    
    import logmapperui.api.dbfile_api as dbapi
    
    logMapperApi = dbapi.LogMapperApiDb()
    
    start = datetime.datetime(2018,3, 11, 8, 0, 0)
    end = datetime.datetime(2018, 3, 12, 23, 0, 0)
    
    start = datetime.datetime(2018,3, 18, 12, 0, 0)
    end = datetime.datetime(2018, 3, 19, 8, 0, 0)    
    
    start = datetime.datetime(2018,3, 26, 16, 30, 0)
    end = datetime.datetime(2018, 3, 26, 22, 0, 0) 
    
    start = datetime.datetime(2018,4, 22, 19, 0, 0)
    end = datetime.datetime(2018, 4, 22, 21, 0, 0)    

    start = datetime.datetime(2018, 4, 28, 14, 30, 0)
    end =   datetime.datetime(2018, 4, 28, 15, 30, 0) 
    
    
    hostId = 4
    componentId = 4   
    sourceId = 13
    
    fig = plt.figure()
    ax = fig.add_subplot(111)       
    
    response = logMapperApi.getPerformanceData(start, end)
    performanceData = response['performanceData']     
    performancePlotMaker = PerformancePlotMaker(performanceData)  
#    performancePlotMaker.getPlotPerformance(ax)
    performancePlotMaker.getPlotAverages(ax)
    
    fig = plt.figure()
    ax = fig.add_subplot(111) 
    
    response = logMapperApi.getHostData(hostId, start, end)
    hostData = response['results']      
    hostPlotMaker = HostPlotMaker(hostData) 
    hostPlotMaker.getPlotCpu(ax)
#    hostPlotMaker.getPlotMem(ax)
#    hostPlotMaker.getPlotDisk(ax)
#    hostPlotMaker.getPlotNet(ax)
#    hostPlotMaker.getPlotNetError(ax)
#    hostPlotMaker.getPlotCountersFiles(ax)

  
    fig = plt.figure()
    ax = fig.add_subplot(111)    
    
    componentData = logMapperApi.getComponentData(componentId, start, end)
    componentPlotMaker = ComponentPlotMaker(componentData)
    componentPlotMaker.getPlotPerformance(ax)
#    componentPlotMaker.getPlotPerformanceMean(ax)
#    componentPlotMaker.getPlotAnomaly(ax)
#    componentPlotMaker.getPlotAnomalyPie(ax)


    fig = plt.figure()
    ax = fig.add_subplot(111)    
    
    sourceData = logMapperApi.getSourceData(sourceId, start, end)
    sourceMeasuresPlotMaker = SourceMeasuresPlotMaker(sourceData)
    sourceMeasuresPlotMaker.getLinePlot(ax, 'MAX(threads)')
 

    
#    df = instancePlotMaker.dfData
 

    

   