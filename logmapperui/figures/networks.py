# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 09:40:04 2018

@author: abaena
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

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

#%%
"""
Global Initialization. Constants definitions.
"""

logger = logging.getLogger(__name__)



def getGraphExample2(ax):

    gapp = nx.Graph()
    
    gc1 = nx.Graph()
    
    gc1.add_node('a', component='c1', color = 'blue')
    gc1.add_node('b', component='c1')
    gc1.add_node('c', component='c1')
    gc1.add_node('d', component='c1')
    
    gc1.add_edge('a', 'b', duration=0.7)
    gc1.add_edge('a', 'c')
    gc1.add_edge('c', 'b')
    gc1.add_edge('a', 'd')
    
    gapp.add_nodes_from(gc1)
    #app.add_edges_from(c1.edges)
    
    gc2 = nx.Graph()
    gc2.add_nodes_from(['x', 'y', 'z'], component='c2')
    gc2.add_edge('x', 'y')
    gc2.add_edge('y', 'z')
    
    gapp.add_nodes_from(gc2)
    #app.add_edges_from(c2.edges)
    
    gapp.add_edge('b', 'x')
    
    #nx.draw(app, with_labels=True, font_weight='bold')
    #nodesAt5 = filter(lambda (node, d): d['component'] == 'c1', app.nodes(data=True))
    #https://networkx.github.io/documentation/networkx-1.10/reference/drawing.html
    layout = nx.shell_layout(gapp)
    
    #Set the current Axes instance to ax
    plt.sca(ax)  
    
    nx.draw_networkx_nodes(gc1, pos=layout, node_size=200, node_color='r', with_labels=True, font_weight='bold')
    nx.draw_networkx_nodes(gc2, pos=layout, node_size=300, node_color='b')
    nx.draw_networkx_edges(gc1, pos=layout, alpha=0.5, width=3)
    nx.draw_networkx_edges(gc2, pos=layout, alpha=0.5, width=3)
    nx.draw_networkx_edges(gapp, pos=layout, alpha=0.5, width=10)
    
    
def getLogMapperNetGraph(ax, nodesData, edgesData):
    """
    list of nodes and deges
    """
    pos = {}
    poslabels = {}
    labels = {}
    nodes_size = []
    nodes_color = []
    Gmain = nx.DiGraph()
    for node in nodesData:
        Gmain.add_node(node['key'], name=node['name'])
        pos[node['key']] = (node['x'], node['y'])
        labels[node['key']] = node['name']
        poslabels[node['key']] = (node['x'], node['y']-0.1 ) 
                
        if node['performanceMin'] == None:
            nodes_size.append(200) 
            nodes_color.append('k')
        else:
            nodes_size.append((1.2-node['performanceMin'])*1000)
            if node['performanceMin'] < 0.4:
                nodes_color.append('r')
            elif node['performanceMin'] < 0.6:
                nodes_color.append('y')
            else:
                nodes_color.append('g')                   
        
        
    print(str(pos))
        
    for edge in edgesData:
        Gmain.add_edge(edge['n1'], edge['n2'], performance=edge['performance'], ref=edge['ref'])
        
#    layout = nx.spring_layout(Gmain)
        
    nx.draw_networkx_nodes(Gmain, pos=pos, node_size=nodes_size, node_color=nodes_color, with_labels=True)
    nx.draw_networkx_edges(Gmain, pos=pos, ax=ax, alpha=0.5, width=2, arrowstyle='->', arrowsize=20)
    nx.draw_networkx_labels(Gmain, pos=poslabels, ax=ax, labels=labels, font_size=12)
    ax.set_axis_off()
                

    
def getLogMapperNetGraphBack(ax, nodesData, edgesData):
    """
    array of dictionary with nodes [ { nodes component1 } ... { nodes componen tn } ]
    dictipnary {nodes: [ array of nodes]}
    array of tuples with relation and attributes
    """

    Gmain = nx.DiGraph()
    
    nodeList = []
    componentList=[]
    for componentData in nodesData:
        component = componentData['component']
        componentList.append(component)
        for node in componentData['nodes']:
            Gmain.add_node(node['node'], component=component, key=node['key'])
            nodeList.append( (component, node['node'], node['key']))
        
    nodesdf=pd.DataFrame(nodeList, columns=['component', 'id', 'key'])
        
    for edgaData in edgesData:
        Gmain.add_edge(edgaData['n1'], edgaData['n2'], performance=edgaData['performance'], ref=edgaData['ref'])
        
    
#    layout = nx.shell_layout(Gmain)
    layout = nx.spring_layout(Gmain)
    
    
#    val_map = {'device': 1.0,
#               'appcode-web': 0.5714285714285714,
#               'devicetypetok': 0.3,
#               } 
    
    gap = 1/(len(componentList)+1)
    val_map = {}
    scale = gap
    for component in componentList:      
        val_map[component] = scale
        scale += gap
        
#    options = {
#     'with_labels': False,
#     'node_color': 'r',
#     'node_size': 10,
#     'linewidths': 0,
#     'width': 0.1,
#    }
#    nx.draw_circular(Gmain, **options)        

    #nodesAt5 = filter(lambda (node, d): d['component'] == 'c1', app.nodes(data=True))
    #https://networkx.github.io/documentation/networkx-1.10/reference/drawing.html

       
#    color_nodes = [val_map.get(node[1]['component'], 0.25) for node in Gmain.nodes(data=True)]
#    nx.draw(Gmain, pos=layout, ax=ax, node_size=10, cmap=plt.get_cmap('jet'), node_color = color_nodes)
  
    
    for component in componentList:
        nodes = nodesdf[nodesdf['component']==component]['id'].tolist()
        color_node = val_map.get(component, 0.25)
        cmap=plt.get_cmap('jet')
        color_node=[cmap(color_node)]
        
        nx.draw_networkx_nodes(Gmain, pos=layout, ax=ax, nodelist=nodes, node_size=100, node_color=color_node, with_labels=True, font_weight='bold')
        
    nx.draw_networkx_edges(Gmain, pos=layout, ax=ax, alpha=0.5, width=2)
      
#    return Gmain, nodesdf


def showPlot(function):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    function(ax)
          
        
 
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')     

#    showPlot(getGraphExample2)
    
    
    import logmapperui.api.db_api as dbapi
    
    logMapperApi = dbapi.LogMapperApiDb()
    
    start = datetime.datetime(2018,3, 18, 11, 0, 0)
    end = datetime.datetime(2018, 3, 18, 11, 15, 0)
    hostId = 1
    componentId = 4    
    
    response = logMapperApi.getNetworkGraphData(start, end)
    nodesData = response['nodesData']
    edgesData = response['edgesData']

    fig = plt.figure()
    ax = fig.add_subplot(111)
    getLogMapperNetGraph(ax, nodesData, edgesData)
    

    

    

