# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 08:53:35 2018

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************

__author__ = 'andres.baena@udea.edu.co'
__title__= 'Prueba'
__date__ = ''
__version__ = '0.0.1'
__license__ = 'GNU GPLv3'

import logging
import os, sys, webbrowser, datetime
from enum import Enum
import json

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

import pandas as pd

import matplotlib as plt
plt.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import config.config as cfg
import logmappercommon.utils.logging_util as logging_util
import logmappercommon.definitions.logmapperkeys as lmkey
import logmapperui.api.db_api as dbapi
import logmapperui.figures.plots as lmplots
import logmapperui.figures.networks as lmnet


t = None

#%%
#==============================================================================
# Global Initialization. cfgants definitions.
#==============================================================================

logger = logging.getLogger(__name__)


class State(Enum):
    STARTING = 0
    IDLE = 1
    MONITORING = 2
    
MSG_DISTRIBUTED_SYSTEM = 'Distributed System'
MSG_BUTTON_START_MONITOR = 'Start Monitoring'
MSG_BUTTON_PAUSE_MONITOR = 'Pause Monitoring'
MSG_BUTTON_NEXT_PERIOD = 'Next   >>'
MSG_BUTTON_BACK_PERIOD = '<<    Back'

"""
Main window

Layout:

    |    0      |     1     |   2      |     3     |     4     |     5      | 
    =========================================================================
 0  |                       |          |           |           |            |
 -- -------------------------------------------------------------------------    
    |                       |          |           |           |            | 
    |                       |          |           |           |            | 
 1  |                       |          |           |           |            |
    |                       |          |           |           |            | 
    |                       |          |           |           |            |
 -- |                       |-----------------------------------------------|
    |                       |          |           |           |            | 
    |                       |          |           |           |            | 
    |                       |          |           |           |            | 
 2  |                       |          |           |           |            | 
    |                       |          |           |           |            | 
    |                       |          |           |           |            |
 -- |                       |-----------------------------------------------|
    |                       |          |           |           |            | 
    |                       |          |           |           |            |
    |                       |          |           |           |            | 
 3  |                       |          |           |           |            | 
    |                       |          |           |           |            | 
    |                       |          |           |           |            | 
    |                       |          |           |           |            |
 -- -------------------------------------------------------------------------
    |                       |                                               |
 4  |                       |                                               |
    |                       |                                               |    
 -- -------------------------------------------------------------------------
 5  |           |           |          |           |           |            |
    |           |           |          |           |    COMBO1   |   BUT1     | 
 -- -------------------------------------------------------------------------
 6  |           |           |          |           |           |            |
    |           |           |          |           |    BUT2   |   BUT1     | 
 -- -------------------------------------------------------------------------
 7  |                            state bar colspan=6                        |
    =========================================================================      


"""



class GuiApplication():
    
    #TODO pasar como config
    EVENT_REFRESH_PERIOD = 60000
        
    def __init__(self, config): 

        self.state = State.STARTING             
        self.logMapperApi = None                
        self.nodeType = None
        self.nodeDetail = None
                       
        #TODO pasar como config, TAMBIEN NOMBRE DE ARCHIVO
        self.period = 1
        self.step = 5
#        start = datetime.datetime(2018,4,22, 18, 0, 0)
        
        start = datetime.datetime(2018, 4, 25, 8, 0, 0)       
        start = datetime.datetime(2018, 4, 25, 18, 0, 0)
        
        start = datetime.datetime(2018, 4, 24, 10, 0, 0)
        
#        start = datetime.datetime(2018,5, 3, 9, 0, 0)
        self.initStartEnd(start)        
                            
        self.root = tk.Tk()

        self.init_main_window()               
        self.init_menu()        
        self.init_contextmenu()
        self.init_statebar()       
        self.init_quickkeys()        
        self.init_buttons()
        self.init_combos()
        self.init_treenode()       
        self.init_infoview()       
        self.init_plots()
        
        #periodic event
        self.event_refresh()
        
        self.state = State.IDLE
        
        #carga db
        self.logMapperApi = None
        try:
            self.logMapperApi = dbapi.LogMapperApiDb()
        except Exception as exc:
            logger.exception("Error connecting to data source")
            messagebox.showerror("Error connecting to data source", str(exc))
            
        self.loadTree()
        self.refreshControls()        
        
        self.root.mainloop()
        
        
    def init_main_window(self):
        
        width = 1100
        height = 740
        
        logger.debug("width="+str(self.root.winfo_screenwidth()))
        logger.debug("height="+str(self.root.winfo_screenheight()))
        
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2) - 50
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        self.root.resizable(width=False, height=False)
        self.root.title("Logmapper UI - "+__version__)
        self.root.focus_force()
        self.root.after(1, lambda: self.root.focus_force())
        
#        self.root.iconphoto(self.root, self.icono1)  # Asigna icono app 
        self.root.option_add("*Font", "Helvetica 12")  # Fuente predeterminada        
#        self.root.option_add('*tearOff', False)  # Deshabilita submenús flotantes
#        self.root.attributes('-fullscreen', True)  # Maximiza ventana completa        
#        self.root.minsize(900,800)  # Establece tamaño minimo ventana
        

        self.frameTree  = tk.Frame(self.root, width=300, height=680, bg="cyan")        
        self.framePlot1 = tk.Frame(self.root, width=400, height=175, bg="blue") 
        self.framePlot2 = tk.Frame(self.root, width=400, height=175, bg="blue") 
        self.framePlot3 = tk.Frame(self.root, width=400, height=175, bg="red") 
        self.framePlot4 = tk.Frame(self.root, width=400, height=175, bg="red") 
        self.framePlot5 = tk.Frame(self.root, width=400, height=175, bg="cyan")
        self.framePlot6 = tk.Frame(self.root, width=400, height=175, bg="cyan")
        self.frameInfo  = tk.Frame(self.root, width=800, height=75, bg="blue")
        
        self.frameTree.grid(row=1, column=0, columnspan=2, rowspan=6, padx=5, pady =5)       
        self.framePlot1.grid(row=1, column=2, columnspan=2)
        self.framePlot2.grid(row=1, column=4, columnspan=2)
        self.framePlot3.grid(row=2, column=2, columnspan=2)
        self.framePlot4.grid(row=2, column=4, columnspan=2)
        self.framePlot5.grid(row=3, column=2, columnspan=2)
        self.framePlot6.grid(row=3, column=4, columnspan=2)
        self.frameInfo.grid(row=4, column=2, columnspan=4)  
        
        self.framePlotMain = tk.Frame(self.root, width=800, height=350, bg="blue")
        self.framePlotMain.grid(row=1, column=2, columnspan=4, rowspan=2)

        self.frameTree.pack_propagate(0)
        self.framePlot1.pack_propagate(0)
        self.framePlot2.pack_propagate(0)
        self.framePlot3.pack_propagate(0)
        self.framePlot4.pack_propagate(0)
        self.framePlot5.pack_propagate(0)
        self.framePlot6.pack_propagate(0)
        self.framePlotMain.pack_propagate(0)
        self.frameInfo.pack_propagate(0)       
        
        
    def init_menu(self):
        barramenu = tk.Menu(self.root)
        self.root['menu'] = barramenu

        menu1 = tk.Menu(barramenu)
        menu2 = tk.Menu(barramenu)
        menu3 = tk.Menu(barramenu)
        barramenu.add_cascade(menu=menu1, label='Main')
        barramenu.add_cascade(menu=menu2, label='Settings')
        barramenu.add_cascade(menu=menu3, label='Help')
        
        #TODO add settings menu
#        menu1.add_command(label='Open file', command=self.option_openfile)
#        menu1.add_separator()  # Agrega un separador
#        menu1.add_command(label='Salir', command=self.option_exit, 
#                          underline=0, accelerator="Ctrl+q",
#                          compound=tk.LEFT) 
#        
#        menu2.add_command(label='Settings', command=self.option_settings)

        menu3.add_command(label='Web', command=self.option_help)      
        menu3.add_command(label="About", 
                          command=self.option_about,
                          compound=tk.LEFT) 
        
    def init_contextmenu(self):
        # DEFINIR MENU CONTEXTUAL
        self.menucontext = tk.Menu(self.root, tearoff=0)
        self.menucontext.add_command(label="Refresh", command=self.refreshData)  
        self.menucontext.add_command(label="Detail", command=self.option_showinfo)
        self.menucontext.add_command(label="Show Data", command=self.option_showData)
           
        

    def init_statebar(self):
        # DEFINIR BARRA DE ESTADO:
        # Muestra información del equipo
        
        self.statebartext1 = tk.Label(self.root, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statebartext1.grid(row=7,column=5, columnspan=1, sticky=tk.W+tk.E+tk.S, pady=0, padx=0)
        self.statebartext1['text']=str(self.state)        

        self.statebartext2 = tk.Label(self.root, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statebartext2.grid(row=7,column=4, columnspan=1, sticky=tk.W+tk.E+tk.S, pady=0, padx=0)
        
        self.statebartext3 = tk.Label(self.root, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statebartext3.grid(row=7,column=2, columnspan=2, sticky=tk.W+tk.E+tk.S, pady=0, padx=0)

        self.statebartext4 = tk.Label(self.root, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statebartext4.grid(row=7,column=0, columnspan=2, sticky=tk.W+tk.E+tk.S, pady=0, padx=0)

    def init_quickkeys(self):
        # DECLARAR TECLAS DE ACCESO RAPIDO:     
        self.root.bind("<Control-q>", lambda event: self.option_exit())
           
        
    def init_buttons(self):
        self.buttonControl = ttk.Button(self.root, text=MSG_BUTTON_START_MONITOR, command=self.option_button_controlmonitor)  
        self.buttonControl.grid(row=6,column=5, sticky=tk.W+tk.E+tk.N+tk.S, pady=10, padx=20)  
        
        self.buttonNext = ttk.Button(self.root, text=MSG_BUTTON_NEXT_PERIOD, command=self.option_button_next)  
        self.buttonNext.grid(row=6,column=4, sticky=tk.W+tk.E+tk.N+tk.S, pady=10, padx=10)  

        self.buttonBack = ttk.Button(self.root, text=MSG_BUTTON_BACK_PERIOD, command=self.option_button_back)  
        self.buttonBack.grid(row=6,column=3, sticky=tk.W+tk.E+tk.N+tk.S, pady=10, padx=10)  
    
    def init_combos(self): 
        self.comboPeriod = ttk.Combobox(self.root)
#        self.comboPeriod.grid(row=5,column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=10, padx=10)
        self.comboPeriod.grid(row=5,column=3, sticky=tk.W+tk.E+tk.N+tk.S, pady=10, padx=10)
        self.comboPeriod.bind("<<ComboboxSelected>>", self.event_combo_period_select)         
        self.comboPeriod["values"] = ['1 h (Period)', '3 h (Period)', '6 h (Period)', '24 h (Period)', '48 h (Period)']
        self.comboPeriod.current(0)
        self.comboPeriod.pack_propagate(0)
        
        self.comboStep = ttk.Combobox(self.root)
        self.comboStep.grid(row=5,column=4, sticky=tk.W+tk.E+tk.N+tk.S, pady=10, padx=10)
        self.comboStep.bind("<<ComboboxSelected>>", self.event_combo_step_select)         
        self.comboStep["values"] = ['5 m (Step)', '15 m (Step)', '60 m (Step)', '180 m (Step)']
        self.comboStep.current(0)
        self.comboPeriod.pack_propagate(0)
                
        
        
    def init_treenode(self):
        self.tree = ttk.Treeview(self.frameTree)
        self.tree.pack(fill=tk.Y, expand=tk.YES)

        self.tree["columns"]=("performance", "type", "detail")
        self.tree.column("performance", width=100 )
        self.tree.heading("#0", text="Host.Reader")
        self.tree.heading("performance", text="Performance")
        
        self.treeRoot = self.tree.insert("" , tk.END,  text=MSG_DISTRIBUTED_SYSTEM, values=("", "root", ), open=True)

        self.tree.bind("<Button-1>", self.event_treenode_select)
        self.tree.bind("<Button-3>", self.event_treecontextmenu)            
        
    def init_infoview(self):
        ttk.Label(self.root, text='Nodos').grid(row=0,column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, pady=0, padx=0)
        ttk.Label(self.root, text='Tablero de Control').grid(row=0,column=2, columnspan=4, pady=0, padx=0)       
        self.infoText = tk.Text(self.frameInfo)
        self.infoText.pack(fill=tk.BOTH, expand=tk.YES) 

    def init_plots(self):
        self.canvas1, self.ax1  = self.createFigure(self.framePlot1, 1)
        self.canvas2, self.ax2  = self.createFigure(self.framePlot2, 2)
        self.canvas3, self.ax3  = self.createFigure(self.framePlot3, 3)
        self.canvas4, self.ax4  = self.createFigure(self.framePlot4, 4)
        self.canvas5, self.ax5  = self.createFigure(self.framePlot5, 5)
        self.canvas6, self.ax6  = self.createFigure(self.framePlot6, 6)
        self.canvasMain, self.axMain  = self.createFigure(self.framePlotMain, 7) 

        
    def initStartEnd(self, now = datetime.datetime.now()):        
        mod = now.hour % self.period
        self.start = datetime.datetime(now.year, now.month, now.day, now.hour-mod, 0, 0)
        self.end  = self.start + datetime.timedelta(hours = self.period)         
        
        
    def event_treenode_select(self, event):
        item = self.tree.identify_row(event.y)
        self.selectedItem = self.tree.item(item, "text")
        self.selectedInfo = str(self.tree.set(self.tree.identify_row(event.y)))
        logger.debug("event_treenode_select:" + str(self.selectedItem))
        logger.debug(str(self.selectedInfo))
        
        
        self.nodeType = None
        self.nodeDetail = None
        if self.selectedItem == MSG_DISTRIBUTED_SYSTEM or self.selectedItem == 'agent-1':
            self.select_layout_all_components()         
        else:           
#            s = self.selectedInfo.replace("'", '"').replace('"{', '{').replace('}"', '}')
#            j = json.loads(s)
            j = stringDict2Json(self.selectedInfo)
            
            self.nodeType = j['type']
            self.nodeDetail = j['detail']
            
            self.select_layout_component() 
            
        self.refreshData()        
        
        
        
  
    def event_treecontextmenu(self, event):
        self.menucontext.post(event.x_root, event.y_root)      
       
    def event_combo_period_select(self, event):
        option = self.comboPeriod.get()
        logger.debug("event_combo_period_select:"+option )
        
        option =  option[0:option.find(' ')]
        self.period = int(option)
        
        mod = self.start.hour % self.period
        
        self.start = datetime.datetime(self.start.year, self.start.month, self.start.day, self.start.hour-mod, 0, 0)      
        self.end  = self.start + datetime.timedelta(hours = self.period)
        self.refreshData()
        
    def event_combo_step_select(self, event):
        option = self.comboStep.get()
        logger.debug("event_combo_step_select:"+option )
        
        option =  option[0:option.find(' ')]
        self.step = int(option)
        
        mod = self.start.minute % self.step
            
        self.start = self.start - datetime.timedelta(minutes = mod)
        self.end  = self.start + datetime.timedelta(minutes = self.period)
        self.refreshData()        
        
        

    def event_detailplot(self, plotId):
        ''' Construye una ventana de diálogo '''
        logger.debug("option_detailplot:"+str(plotId))
        self.detailedplot = tk.Toplevel()
        
        pad = 50
        width = self.root.winfo_screenwidth()-2*pad
        height = self.root.winfo_screenheight()-2*pad 
        
        self.detailedplot.geometry('{}x{}+{}+{}'.format(width, height, pad, 0))
        self.detailedplot.resizable(width=True, height=True)
        self.detailedplot.title('Detail')
        
        self.canvasDetail, self.axDetail  = self.createFigure(self.detailedplot)
               
        self.refreshPlotDetail(plotId)
      
        toolbar = NavigationToolbar2TkAgg(self.canvasDetail, self.detailedplot)
        toolbar.update()
        self.canvasDetail._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)          
        
        buttonClose = ttk.Button(self.detailedplot, text='Close', command=self.detailedplot.destroy)   
        buttonClose.pack(side=tk.RIGHT, padx=10, pady=10)
          
        self.detailedplot.grab_set()
        self.detailedplot.transient(master=self.root)
        self.root.wait_window(self.detailedplot)  
          
    def event_refresh(self):  
        self.refreshControls() 
        if self.state == State.MONITORING:
            if datetime.datetime.now() > self.start:
                self.initStartEnd()
            self.refreshData()
        
        self.root.after(self.EVENT_REFRESH_PERIOD, self.event_refresh)           
            
            
    def option_exit(self):
        ''' Salir de la aplicación '''
        self.root.destroy()  

       
    def option_about(self):
        ''' Definir ventana de diálogo 'Acerca de' '''

        window = tk.Toplevel()

        window.geometry('{}x{}+{}+{}'.format(400, 300, 0, 0))
        window.resizable(width=False, height=False)
        window.title('')
                  
        buttonClose = ttk.Button(window, text='Close', command=window.destroy)   
        buttonClose.pack(side=tk.BOTTOM, padx=10, pady=10)
          
        window.grab_set()
        window.transient(master=self.root)
        self.root.wait_window(window)        
       
        
        
    def option_help(self):
        ''' Abrir página web en navegador Internet '''
        
        page = 'http://www.logmapper.org'
        webbrowser.open_new_tab(page) 
 
       
    #TODO    
    def option_settings(self):
        window = tk.Toplevel()

        window.geometry('{}x{}+{}+{}'.format(400, 300, 0, 0))
        window.resizable(width=False, height=False)
        window.title('')
             
        
        buttonClose = ttk.Button(window, text='Close', command=window.destroy)   
        buttonClose.pack(side=tk.RIGHT, padx=10, pady=10)
          
        window.grab_set()
        window.transient(master=self.root)
        self.root.wait_window(window)          

        
    def option_openfile(self):
        self.filename = askopenfilename()
        if self.filename:
#            self.tree.delete(*self.tree.get_children())
            self.logMapperApi = dbapi.LogMapperApiDbfile(self.filename)
            self.state = State.IDLE
            self.loadTree()
            self.refreshControls()
        
    def option_showinfo(self):     
        messagebox.showinfo("Detail", self.selectedInfo)
        
    def option_showData(self):  
        componentId = self.nodeDetail['id']
        df = self.logMapperApi.getLowPerformancePaths(componentId, self.start, self.end)
        self.showDataTable(df.iloc[:, 0:-5])
   
        
    def option_button_controlmonitor(self):
        if not self.logMapperApi:
            return
        
        if self.state == State.IDLE:
            self.state = State.MONITORING
            self.buttonControl['text'] = MSG_BUTTON_PAUSE_MONITOR
        else:
            self.state = State.IDLE
            self.buttonControl['text'] = MSG_BUTTON_START_MONITOR
        self.refreshControls()
        self.refreshData()
        
    def option_button_next(self):
        self.start = self.start + datetime.timedelta(minutes = self.step)
        self.end  = self.start + datetime.timedelta(hours = self.period)
        self.refreshData()
        
    def option_button_back(self):
        self.start = self.start - datetime.timedelta(minutes = self.step)
        self.end  = self.start + datetime.timedelta(hours = self.period)
        self.refreshData()   
        
        
    def createFigure(self, master, plotid=0):
        fig = plt.pyplot.figure()    
        ax = fig.add_subplot(111)  
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.show()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        if plotid != 0:         
            canvas._tkcanvas.bind("<Double-Button-1>", lambda event, plotid=plotid: self.event_detailplot(plotid))
        return canvas, ax
        
        
    def refresh_statebar(self):
        self.statebartext1['text']=str(self.state) 
        self.statebartext2['text']='' 
        self.statebartext3['text']= self.start.strftime("%Y-%m-%d   %H:%M")+" - "+self.end.strftime("%H:%M")
        self.statebartext4['text']= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        
    def hide_view(self):
        self.framePlot1.grid_remove()
        self.framePlot2.grid_remove()
        self.framePlot3.grid_remove()
        self.framePlot4.grid_remove()
        self.framePlot5.grid_remove()
        self.framePlot6.grid_remove()
        self.framePlotMain.grid_remove()  
        
    def select_layout_all_components(self): 
        self.hide_view()
        self.framePlotMain.grid()
        self.framePlot5.grid()
        self.framePlot6.grid()        

        
    def select_layout_component(self):
        self.hide_view()
        
        self.framePlot1.grid()
        self.framePlot2.grid()
        self.framePlot3.grid()
        self.framePlot4.grid()
        self.framePlot5.grid()
        self.framePlot6.grid()
        
    def refreshPlotMain(self):
        self.axMain.cla()
        lmnet.getLogMapperNetGraph(self.axMain, self.nodesData, self.edgesData)
        self.canvasMain.draw()   
        
    def refreshPlot5Mon(self):
        self.ax5.cla()
        self.performancePlotMaker.getPlotPerformance(self.ax5)
        self.canvas5.draw()

    def refreshPlot6Mon(self):
        self.ax6.cla()
        self.performancePlotMaker.getPlotAverages(self.ax6)
        self.canvas6.draw()           
 
        
    def refreshPlot1(self):
        self.ax1.cla()
        self.hostPlotMaker.getPlotCpu(self.ax1)
        self.canvas1.draw()

    def refreshPlot2(self):
        self.ax2.cla()
        self.hostPlotMaker.getPlotMem(self.ax2)
        self.canvas2.draw()

    def refreshPlot3(self):
        self.ax3.cla()
        self.hostPlotMaker.getPlotNet(self.ax3)
        self.canvas3.draw()

    def refreshPlot4(self):
        self.ax4.cla()
        self.hostPlotMaker.getPlotNetError(self.ax4)
        self.canvas4.draw()

    def refreshPlot5(self):
        self.ax5.cla()
        self.hostPlotMaker.getPlotDisk(self.ax5)
        self.canvas5.draw()

    def refreshPlot6(self):
        self.ax6.cla()
        self.hostPlotMaker.getPlotNetError(self.ax6)
        self.canvas6.draw()
        
        
    def refreshPlot1Component(self):
        self.ax1.cla()
        self.hostPlotMaker.getPlotCpu(self.ax1)
        self.canvas1.draw()

    def refreshPlot2Component(self):
        self.ax2.cla()
        self.hostPlotMaker.getPlotMem(self.ax2)
        self.canvas2.draw()

    def refreshPlot3Component(self):
        self.ax3.cla()
        self.componentPlotMaker.getPlotPerformance(self.ax3)
        self.canvas3.draw()

    def refreshPlot4Component(self):
        self.ax4.cla()
        self.componentPlotMaker.getPlotPerformanceMean(self.ax4)
        self.canvas4.draw()

    def refreshPlot5Component(self):
        self.ax5.cla()
        self.componentPlotMaker.getPlotAnomaly(self.ax5)
        self.canvas5.draw()

    def refreshPlot6Component(self):
        self.ax6.cla()
        self.componentPlotMaker.getPlotAnomalyPie(self.ax6)
        self.canvas6.draw()       
        
        
    def refreshPlot1Source(self):
        self.ax1.cla()
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_SPRINGMICROSERVICE:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax1, 'MAX(threads)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_TOMCAT:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax1, 'MAX(threads)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_POSTGRES:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax1, 'MAX(conns)') 
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_READER:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax1, 'logCount')              
        self.canvas1.draw()

    def refreshPlot2Source(self):
        self.ax2.cla()
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_SPRINGMICROSERVICE:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax2, 'MAX(sessions)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_TOMCAT:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax2, 'MAX(threadsBusy)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_POSTGRES:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax2, 'MAX(locks)') 
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_READER:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax2, 'threadsCount')              
        self.canvas2.draw()
        

    def refreshPlot3Source(self):
        self.ax3.cla()
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_SPRINGMICROSERVICE:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax3, 'MAX(memused)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_TOMCAT:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax3, 'MAX(memused)')
#        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_POSTGRES:
#            self.sourceMeasuresPlotMaker.getLinePlot(self.ax3, '') 
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_READER:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax3, 'logEventsCriticalCount')              
        self.canvas3.draw()
       
    def refreshPlot4Source(self):
        self.ax4.cla()
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_SPRINGMICROSERVICE:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax4, 'MAX(heapused)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_TOMCAT:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax4, 'MAX(workers)')
#        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_POSTGRES:
#            self.sourceMeasuresPlotMaker.getLinePlot(self.ax4, '') 
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_READER:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax4, 'logEventsErrorCount')              
        self.canvas4.draw()
        
    def refreshPlot5Source(self):
        self.ax5.cla()
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_SPRINGMICROSERVICE:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax5, 'MAX(nonheapused)')
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_TOMCAT:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax5, 'COUNT(fail)')
#        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_POSTGRES:
#            self.sourceMeasuresPlotMaker.getLinePlot(self.ax5, '') 
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_READER:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax5, 'logEventsWarningCount')              
        self.canvas5.draw()  
        
    def refreshPlot6Source(self):
        self.ax6.cla()
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_SPRINGMICROSERVICE:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax6, 'COUNT(fail)')
#        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_TOMCAT:
#            self.sourceMeasuresPlotMaker.getLinePlot(self.ax6, '')
#        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_POSTGRES:
#            self.sourceMeasuresPlotMaker.getLinePlot(self.ax6, '') 
        if self.nodeDetail['sourcetype'] == lmkey.SOURCE_TYPE_READER:
            self.sourceMeasuresPlotMaker.getLinePlot(self.ax6, 'ERROR')              
        self.canvas6.draw()        

        
    def refreshPlotDetail(self, plotId):        
        self.axDetail.cla()
        if plotId == 7:
            lmnet.getLogMapperNetGraph(self.axDetail, self.nodesData, self.edgesData)
        elif plotId == 5:
            self.performancePlotMaker.getPlotPerformance(self.axDetail)
        elif plotId == 6:
            self.performancePlotMaker.getPlotAverages(self.axDetail)           
        self.canvasDetail.draw()  
        
    def loadTree(self):
        if not self.logMapperApi:
            return
        
        hosts = self.logMapperApi.findHosts()
        for host in hosts:
            hostTreeNode = self.tree.insert(self.treeRoot , tk.END,  text=host['name'], values=("", "host", host), tags = ('',), open=True)
            components = self.logMapperApi.findComponentsByHostId(host['id'])
            for component in components:
                componentTreeNode = self.tree.insert(hostTreeNode, tk.END, text=component['name'], values=("", "component", component), tags = ('',))                 
                sources = self.logMapperApi.findSourcesByComponentId(component['id'])
                for source in sources:
                    label = source['name']+"("+source['sourcetype']+")"
                    self.tree.insert(componentTreeNode, tk.END, text=label, values=("", "source", source), tags = ('',))
                    
        self.tree.tag_configure("major", background='red')
        self.tree.tag_configure("minor", background='yellow')
        
    
    def showDataTable(self, df):
        window = tk.Toplevel() 
        width = self.root.winfo_screenwidth()
        height = 700      
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2) - 50
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))        
        window.resizable(width=True, height=True)
        window.title('Data')
        
        t = tk.Text(window)
        t.pack(fill=tk.BOTH,expand=1)
   

#        intFormatter = lambda x: "{:<7}".format(x)
#        floatFormatter = lambda x: "{:7.2f}".format(x)
#        stringFormatter = lambda x: "{:<60}".format(x.replace("com.ospinternational.", ""))
#        
#        formatters = [
#                floatFormatter,
#                floatFormatter,
#                floatFormatter,
#                intFormatter,
#                stringFormatter,
#                stringFormatter,
#                stringFormatter,
#                stringFormatter
#                ]
#        
#        t.insert(tk.INSERT, df.to_string(header=False,
#                                         justify='left', 
#                                         col_space=10, 
#                                         index=False,
#                                         formatters=formatters,
#                                         float_format='%.3f'
#                                         ))
        
        for index, row in df.iterrows():
            array = [row[0], row[1], row[2], row[3], 
                     row[4].replace("com.ospinternational.", ""), row[5], 
                     row[6].replace("com.ospinternational.", ""), row[7]]
            line = '{:7.2f} {:7.2f} {:7.2f} {:6d} {:80} {:60} -> {:80} {:60} \r\n'.format( *array )
            t.insert(tk.INSERT, line)
        

        buttonClose = ttk.Button(window, text='Close', command=window.destroy)   
        buttonClose.pack(side=tk.BOTTOM, padx=10, pady=10)
          
        window.grab_set()
        window.transient(master=self.root)
        self.root.wait_window(window)        
                

    def refreshTreeData(self):
        print("refreshTreeData")
        if self.treeRoot == None:
            return
        
        root = self.tree.get_children(self.treeRoot)     
        for host in root:
            components = self.tree.get_children(host)
            for component in components:
                #Plots are 1 hour, metrics 5 minutes
                start = self.end - datetime.timedelta(minutes = 5) 
                j = stringDict2Json(self.tree.item(component)['values'][2])
                state = self.logMapperApi.getComponentState(j['id'], start, self.end)
                
                vmin = 1
                perf = 'NA'
                if state['performance'] != None: 
                    perf = "{:.1f}".format(state['performance'])
                    if state['performance'] < vmin: vmin = state['performance']
                perfMin = 'NA'
                if state['performanceMin'] != None: 
                    perfMin = "{:.1f}".format(state['performanceMin'])
                    if state['performanceMin'] < vmin: vmin = state['performanceMin']
                anom = 'NA'
                if state['anomaly'] != None: 
                    anom = "{:.1f}".format(state['anomaly'])
                    if state['anomaly'] < vmin: vmin = state['anomaly']
                stateStr = "{} {} {}".format(perf, perfMin, anom) 
                
                self.tree.set(component, 'performance', stateStr)
                
                if vmin < 0.4:
                    self.tree.item(component, tags='major')
                elif vmin < 0.6:
                    self.tree.item(component, tags='minor') 
                else:
                    self.tree.item(component, tags='')
                
                
       
                
    def refreshControls(self):
        self.refresh_statebar()
        
        
    def refreshInfoText(self):
        self.infoText.delete(1.0, tk.END) #clear
        
        self.infoText.insert(tk.INSERT, str(self.nodeType))
        self.infoText.insert(tk.INSERT, "\n")
        self.infoText.insert(tk.INSERT, str(self.nodeDetail))
        
               
        
    def refreshData(self):
        self.refresh_statebar()
        self.refreshInfoText()
        self.refreshTreeData()

        if self.nodeType == "host":
            response = self.logMapperApi.getHostData(self.nodeDetail['id'], self.start, self.end)
            hostData = response['results']      
            self.hostPlotMaker = lmplots.HostPlotMaker(hostData)            
            self.refreshPlot1()
            self.refreshPlot2()
            self.refreshPlot3()
            self.refreshPlot4()
            self.refreshPlot5()
            self.refreshPlot6()  
        elif self.nodeType == "component":
            
            componentData = self.logMapperApi.getComponentData(self.nodeDetail['id'], self.start, self.end)
            self.componentPlotMaker = lmplots.ComponentPlotMaker(componentData)
            
            response = self.logMapperApi.getHostData(self.nodeDetail['hostId'], self.start, self.end)
            hostData = response['results']      
            self.hostPlotMaker = lmplots.HostPlotMaker(hostData)             

            self.refreshPlot1Component()
            self.refreshPlot2Component()
            self.refreshPlot3Component()
            self.refreshPlot4Component()
            self.refreshPlot5Component()
            self.refreshPlot6Component()
            pass
        elif self.nodeType == "source":
            sourceData = self.logMapperApi.getSourceData(self.nodeDetail['id'], self.start, self.end)
            self.sourceMeasuresPlotMaker = lmplots.SourceMeasuresPlotMaker(sourceData) 
            
            self.refreshPlot1Source()                 
            self.refreshPlot2Source()
            self.refreshPlot3Source()
            self.refreshPlot4Source()
            self.refreshPlot5Source()
            self.refreshPlot6Source()
        else:
            start = self.end - datetime.timedelta(minutes = 5) 
            response = self.logMapperApi.getNetworkGraphData(start, self.end)
            self.nodesData = response['nodesData']
            self.edgesData = response['edgesData']
            
            response = self.logMapperApi.getPerformanceData(self.start, self.end)  
            performanceData = response['performanceData']       
            self.performancePlotMaker = lmplots.PerformancePlotMaker(performanceData) 
            self.refreshPlotMain()
            self.refreshPlot5Mon()
            self.refreshPlot6Mon()             

        
def stringDict2Json(stringDict):
        s = stringDict.replace("'", '"').replace('"{', '{').replace('}"', '}')
        j = json.loads(s) 
        return j
        
        
if __name__ == '__main__':
    print('Start module execution:')
#    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S') 

    logging_util.configureLogger('/logmapper/log/logmapper-ui.log') 
    config=cfg.loadConfig()    
    
    app = GuiApplication(config)  
   
    print("End module execution") 