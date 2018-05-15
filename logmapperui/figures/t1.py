# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 22:16:06 2018

@author: abaena
"""

import matplotlib.pyplot as plt
import networkx as nx

G = nx.house_graph()
# explicitly set positions
pos = {0: (0, 0),
       1: (10, 0),
       2: (0, 10),
       3: (10, 10),
       4: (5, 30.0)}

nx.draw_networkx_nodes(G, pos, node_size=200, nodelist=[4])
nx.draw_networkx_nodes(G, pos, node_size=300, nodelist=[0, 1, 2, 3], node_color='b')
nx.draw_networkx_edges(G, pos, alpha=0.5, width=6)
plt.axis('off')
plt.show()