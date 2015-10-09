# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SearchPlus - A QGIS plugin Toponomastic searcherdefault
                              -------------------
        begin                : 2015-06-19
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli
        email                : luipir@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# 2To3 python compatibility
from __future__ import unicode_literals, division, print_function

from qgis.utils import active_plugins
from qgis.gui import QgsMessageBar, QgsTextAnnotationItem
from qgis.core import QgsCredentials, QgsDataSourceURI, QgsGeometry, QgsPoint, QgsLogger, QgsMessageLog, QgsExpression, QgsFeatureRequest, QgsVectorLayer, QgsFeature, QgsMapLayerRegistry, QgsField, QgsProject, QgsLayerTreeLayer
from PyQt4.QtCore import QObject, QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSignal
from PyQt4.QtGui import QAction, QIcon, QDockWidget, QTextDocument, QIntValidator

# PostGIS import
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from search_plus_dockwidget import SearchPlusDockWidget
import os.path

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')


class SearchPlus(QObject):
    """QGIS Plugin Implementation."""

    connectionEstablished = pyqtSignal()

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        super(SearchPlus, self).__init__()
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.pluginName = os.path.basename(self.plugin_dir)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'SearchPlus_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
        # load local settings of the plugin
        settingFile = os.path.join(self.plugin_dir, 'config', 'searchplus.config')
        self.settings = QSettings(settingFile, QSettings.IniFormat)
        self.settings.setIniCodec(sys.stdout.encoding)
        self.stylesFolder = self.plugin_dir+"/styles/"
        
        # load plugin settings
        self.loadPluginSettings()      
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&searchplus')
        self.connection = None
        self.annotations = []
        self.placenameMemLayer = None    
        self.cadastreMemLayer = None  
        self.equipmentMemLayer = None  
        self.portalMemLayer = None   
        
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SearchPlus')
        self.toolbar.setObjectName(u'SearchPlus')
        
        # establish connection when all is completly running 
        self.iface.initializationCompleted.connect(self.initConnection)
        
        # when connection is established, then set all GUI values
        self.connectionEstablished.connect(self.populateGui)    
    
    
    def loadPluginSettings(self):
        ''' Load plugin settings
        '''                   
        # get db credentials
        self.CONNECTION_NAME = self.settings.value('db/CONNECTION_NAME', '')
        self.CONNECTION_HOST = self.settings.value('db/CONNECTION_HOST', '')
        self.CONNECTION_PORT = self.settings.value('db/CONNECTION_PORT', '5432')        
        self.CONNECTION_DB = self.settings.value('db/CONNECTION_DB', '')
        self.CONNECTION_USER = self.settings.value('db/CONNECTION_USER', '')
        self.CONNECTION_PWD = self.settings.value('db/CONNECTION_PWD', '')        

        # get all db configuration table/columns to load to populate the GUI
        self.STREET_SCHEMA= self.settings.value('db/STREET_SCHEMA', '')
        self.STREET_LAYER= self.settings.value('db/STREET_LAYER', '')
        self.STREET_FIELD_CODE= self.settings.value('db/STREET_FIELD_CODE', '')
        self.STREET_FIELD_NAME= self.settings.value('db/STREET_FIELD_NAME', '')
        
        self.PORTAL_SCHEMA= self.settings.value('db/PORTAL_SCHEMA', '')
        self.PORTAL_LAYER= self.settings.value('db/PORTAL_LAYER', '')
        self.PORTAL_FIELD_CODE= self.settings.value('db/PORTAL_FIELD_CODE', '')
        self.PORTAL_FIELD_NUMBER= self.settings.value('db/PORTAL_FIELD_NUMBER', '')
        
        self.PLACENAME_SCHEMA= self.settings.value('db/PLACENAME_SCHEMA', '')
        self.PLACENAME_LAYER= self.settings.value('db/PLACENAME_LAYER', '')
        self.PLACENAME_FIELD= self.settings.value('db/PLACENAME_FIELD', '')
        
        self.EQUIPMENT_SCHEMA= self.settings.value('db/EQUIPMENT_SCHEMA', '')
        self.EQUIPMENT_LAYER= self.settings.value('db/EQUIPMENT_LAYER', '')
        self.EQUIPMENT_FIELD_TYPE= self.settings.value('db/EQUIPMENT_FIELD_TYPE', '')
        self.EQUIPMENT_FIELD_NAME= self.settings.value('db/EQUIPMENT_FIELD_NAME', '')
        
        self.CADASTRE_SCHEMA= self.settings.value('db/CADASTRE_SCHEMA', '')
        self.CADASTRE_LAYER= self.settings.value('db/CADASTRE_LAYER', '')
        self.CADASTRE_FIELD_CODE= self.settings.value('db/CADASTRE_FIELD_CODE', '')
        
        # get initial Scale
        self.defaultZoomScale = self.settings.value('status/defaultZoomScale', 2500)
        
        
    def getLayers(self): 
        
        # Iterate over all layers to get the ones set in config file
        layers = self.iface.legendInterface().layers()
        for cur_layer in layers:     
            uri = cur_layer.dataProvider().dataSourceUri()   
            pos_ini = uri.find("table=")
            pos_fi = uri.find("(geom)")  
            if pos_ini <> -1 and pos_fi <> -1:
                uri_table = uri[pos_ini:pos_fi]            
                if self.STREET_LAYER in uri_table:
                    self.streetLayer = cur_layer
                if self.PLACENAME_LAYER in uri_table:
                    self.placenameLayer = cur_layer     
                if self.CADASTRE_LAYER in uri_table:
                    self.cadastreLayer = cur_layer   
                if self.EQUIPMENT_LAYER in uri_table:                
                    self.equipmentLayer = cur_layer  
                if self.PORTAL_LAYER in uri_table:
                    self.portalLayer = cur_layer                     
    
    
    def getFullExtent(self):
               
        # get full extent
        canvas = self.iface.mapCanvas()
        self.xMax = int(canvas.fullExtent().xMaximum())
        self.xMin = int(canvas.fullExtent().xMinimum())
        self.yMax = int(canvas.fullExtent().yMaximum())
        self.yMin = int(canvas.fullExtent().yMinimum())
        try:
            self.xOffset = (self.xMax - self.xMin) * 0.10
            self.yOffset = (self.yMax - self.yMin) * 0.10   
        except:
            self.xOffset = 1000
            self.yOffset = 1000      
            
        # set validators for UTM text edit
        self.xMinVal = int(self.xMin - self.xOffset)
        self.xMaxVal = int(self.xMax + self.xOffset)
        self.yMinVal = int(self.yMin - self.yOffset)
        self.yMaxVal = int(self.yMax + self.yOffset)             
        self.intValidatorX = QIntValidator(self.xMinVal, self.xMaxVal, self.dlg) # assumed that E and W are inserted as - +
        self.intValidatorY = QIntValidator(self.yMinVal, self.yMaxVal, self.dlg) # assumed that S and N are inserted as - +
        self.dlg.txtCoordX.setValidator(self.intValidatorX)
        self.dlg.txtCoordY.setValidator(self.intValidatorY)            
            
            
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SearchPlus', message)


    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SearchPlus/icon_searchplus.png'
        self.add_action(icon_path, text=self.tr(u'Cercador avançat'), callback=self.run, parent=self.iface.mainWindow())

        # Create the dock widget and dock it but hide it waiting the ond of qgis loading
        self.dlg = SearchPlusDockWidget(self.iface.mainWindow())
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea, self.dlg)
        self.dlg.setVisible(False)
        
        # add first level combo box events
        self.dlg.cboStreet.currentIndexChanged.connect(self.resetNumbers)
        self.dlg.cboStreet.currentIndexChanged.connect(self.zoomOnStreet)
        self.dlg.cboType.currentIndexChanged.connect(self.resetEquipments)
        
        # add events to show information o the canvas
        self.dlg.cboNumber.currentIndexChanged.connect(self.displayStreetData)
        self.dlg.cboTopo.currentIndexChanged.connect(self.displayToponym)
        self.dlg.cboEquipment.currentIndexChanged.connect(self.displayEquipment)
        self.dlg.cboCadastre.currentIndexChanged.connect(self.displayCadastre)
        self.dlg.txtCoordX.returnPressed.connect(self.displayUTM)
        self.dlg.txtCoordY.returnPressed.connect(self.displayUTM)
        
    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&searchplus'), action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
        if self.dlg:
            self.dlg.deleteLater()
            del self.dlg

            
    def initConnection(self):
        ''' Establish connection with the default credentials
        Connection name is get from QGIS connection. Will be used the connection
        configured int he plugin settings
        '''          
        if self.dlg and not self.dlg.isVisible():
            return
        
        # eventually close opened connections
        try:
            self.connection.close()
        except:
            pass
        
        # get connection name (only if set in configuration file)    
        SSL_MODE = 0        
        if self.CONNECTION_NAME != '':
            # look for connection data in QGIS configuration (if exists)
            qgisSettings = QSettings()     
            root_conn = "/PostgreSQL/connections/"          
            qgisSettings.beginGroup(root_conn);           
            groups = qgisSettings.childGroups();                                
            if self.CONNECTION_NAME in groups:      
                root = self.CONNECTION_NAME+"/"  
                self.CONNECTION_HOST = qgisSettings.value(root+"host", '')
                self.CONNECTION_PORT = qgisSettings.value(root+"port", '')            
                self.CONNECTION_DB = qgisSettings.value(root+"database", '')
                self.CONNECTION_USER = qgisSettings.value(root+"username", '')
                self.CONNECTION_PWD = qgisSettings.value(root+"password", '')             
                SSL_MODE = qgisSettings.value(root+"sslmode", QgsDataSourceURI.SSLdisable) 
            #else:
                #self.iface.messageBar().pushMessage("Connection name '"+self.CONNECTION_NAME+"' not found.Please fix it or leave it empty", QgsMessageBar.WARNING, 5)
        
        # get realm of the connection (realm don't have use ry pwd)
        # realm is the connectioInfo from QgsDataSourceURI
        self.uri = QgsDataSourceURI()
        self.uri.setConnection(self.CONNECTION_HOST, self.CONNECTION_PORT, self.CONNECTION_DB, '',  '', int(SSL_MODE))
        connInfo = self.uri.connectionInfo()
        
        # get credentials if at least there's no PWD
        if not self.CONNECTION_PWD:
            # get credentials and mutate cache => need lock
            QgsCredentials.instance().lock()
    
            (ok, self.CONNECTION_USER, self.CONNECTION_PWD) = QgsCredentials.instance().get(connInfo, self.CONNECTION_USER, self.CONNECTION_PWD)
            if not ok:
                QgsCredentials.instance().unlock()
                message = self.tr('Refused or Can not get credentials for realm: {} '.format(connInfo))
                self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
                return
            
            # unlock credentials... but not add to cache
            # wait to verify that connection is ok to add into the cache
            QgsCredentials.instance().unlock()
        
        # add user and password if not set in the previous setConnection 
        self.uri.setConnection(self.CONNECTION_HOST, self.CONNECTION_PORT, self.CONNECTION_DB, self.CONNECTION_USER, self.CONNECTION_PWD, int(SSL_MODE))
        
        # connect          
        try:
            self.connection = psycopg2.connect(self.uri.connectionInfo().encode('utf-8'))
        except Exception as ex:
            message = self.tr("Can not connect to database '{}' for reason: {} ".format(self.CONNECTION_DB, str(ex)))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL, 5)          
            return
        else:
            # last credential were ok, so record them in the cache
            QgsCredentials.instance().lock()
            QgsCredentials.instance().put(connInfo, self.CONNECTION_USER, self.CONNECTION_PWD)
            QgsCredentials.instance().unlock()
                   
        # emit signal that connection is established
        self.connectionEstablished.emit()
    
    
    def checkTable(self, schemaName, tableName):
        
        exists = True
        sql = "SELECT * FROM pg_tables WHERE schemaname = '"+schemaName+"' AND tablename = '"+tableName+"'"
        cursor = self.connection.cursor()        
        rowcount = cursor.execute(sql)         
        if cursor.rowcount == 0:      
            exists = False
        return exists       
        
    
    def populateGui(self):
        ''' Populate the interface with values get from DB
        '''    
        if not self.connection:
            return
            
        # get cursor on wich execute query
        cursor = self.connection.cursor()
        
        # tab cadastre
        sqlquery = 'SELECT id, "{}" FROM "{}"."{}" ORDER BY "{}"'.format(self.CADASTRE_FIELD_CODE, self.CADASTRE_SCHEMA, self.CADASTRE_LAYER, self.CADASTRE_FIELD_CODE)
        exists = self.checkTable(self.CADASTRE_SCHEMA, self.CADASTRE_LAYER)        
        if exists:        
            cursor.execute(sqlquery)
            records = [(-1, '')]
            records.extend([x for x in cursor.fetchall() if x[1]]) # remove None values
            self.dlg.cboCadastre.blockSignals(True)
            self.dlg.cboCadastre.clear()
            for record in records:
                self.dlg.cboCadastre.addItem(record[1], record[0])
            self.dlg.cboCadastre.blockSignals(False)
        else:
            self.dlg.searchPlusTabMain.removeTab(3)  
                    
        # tab equipments
        exists = self.checkTable(self.EQUIPMENT_SCHEMA, self.EQUIPMENT_LAYER)        
        if exists:
            sqlquery = 'SELECT "{}" FROM "{}"."{}" GROUP BY "{}" ORDER BY "{}"'.format(self.EQUIPMENT_FIELD_TYPE, self.EQUIPMENT_SCHEMA, self.EQUIPMENT_LAYER, self.EQUIPMENT_FIELD_TYPE, self.EQUIPMENT_FIELD_TYPE)
            cursor.execute(sqlquery)
            records = ['']
            records.extend([x[0] for x in cursor.fetchall() if x[0]]) # remove None values
            self.dlg.cboType.blockSignals(True)
            self.dlg.cboType.clear()
            self.dlg.cboType.addItems(records)
            self.dlg.cboType.blockSignals(False)
        else:
            self.dlg.searchPlusTabMain.removeTab(2)  
        
        # tab Toponyms
        exists = self.checkTable(self.PLACENAME_SCHEMA, self.PLACENAME_LAYER)
        if exists:
            sqlquery = 'SELECT id, "{}" FROM "{}"."{}" ORDER BY "{}"'.format(self.PLACENAME_FIELD, self.PLACENAME_SCHEMA, self.PLACENAME_LAYER, self.PLACENAME_FIELD)
            cursor.execute(sqlquery)
            records = [(-1, '')]
            records.extend([x for x in cursor.fetchall() if x[1]]) # remove None values
            self.dlg.cboTopo.blockSignals(True)
            self.dlg.cboTopo.clear()
            for record in records:
                self.dlg.cboTopo.addItem(record[1], record[0])
            self.dlg.cboTopo.blockSignals(False)
        else:
            self.dlg.searchPlusTabMain.removeTab(1)                  
            
        # tab Carrerer
        existsStreet = self.checkTable(self.STREET_SCHEMA, self.STREET_LAYER)
        existsPortal = self.checkTable(self.PORTAL_SCHEMA, self.PORTAL_LAYER)        
        if existsStreet and existsPortal:        
            sqlquery = 'SELECT id, "{}", "{}", ST_AsText(geom) FROM "{}"."{}" ORDER BY "{}"'.format(self.STREET_FIELD_NAME, self.STREET_FIELD_CODE, self.STREET_SCHEMA, self.STREET_LAYER, self.STREET_FIELD_NAME)
            cursor.execute(sqlquery)
            records = [(-1, '', '', '')]
            recs = cursor.fetchall()
            records.extend(recs)
            # records.extend([x for x in cursor.fetchall() if x[1]]) # remove None values
            self.dlg.cboStreet.blockSignals(True)
            self.dlg.cboStreet.clear()
            for record in records:
                self.dlg.cboStreet.addItem(record[1], record)
            self.dlg.cboStreet.blockSignals(False)
        else:
            self.dlg.searchPlusTabMain.removeTab(0)          
    
    
    def zoomOnStreet(self):
        ''' Zoom on the street with the prefined scale
        '''
        # get selected street
        selected = self.dlg.cboStreet.currentText()
        if selected == '':
            return
        
        # get code
        data = self.dlg.cboStreet.itemData(self.dlg.cboStreet.currentIndex())
        wkt = data[3] # to know the index see the query that populate the combo
        
        geom = QgsGeometry.fromWkt(wkt)
        if not geom:
            message = self.tr('Can not correctly get geometry')
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return
        
        # zoom on it's centroid
        centroid = geom.centroid()
        self.iface.mapCanvas().setCenter(centroid.asPoint())
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
    
    
    def resetNumbers(self):
        ''' Populate civic numbers depending on selected street. 
        Available civic numbers are linked with self.STREET_FIELD_CODE column code in self.PORTAL_LAYER
        and self.STREET_LAYER
        '''
        if not self.connection:
            return
        
        # get selected street
        selected = self.dlg.cboStreet.currentText()
        if selected == '':
            return
        
        # get code
        data = self.dlg.cboStreet.itemData( self.dlg.cboStreet.currentIndex() )
        code = data[2] # to know the index see the query that populate the combo
        
        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # now get the list of indexes belonging to the current code
        sqlquery = 'SELECT id, "{}" FROM "{}"."{}" WHERE "{}" = %s ORDER BY "{}"; '.format(self.PORTAL_FIELD_NUMBER, self.STREET_SCHEMA, self.PORTAL_LAYER, self.PORTAL_FIELD_CODE, self.PORTAL_FIELD_NUMBER)
        params = [code]
        cursor.execute(sqlquery, params)
        records = [(-1, '')]
        records.extend( [x for x in cursor.fetchall() if x[1]] ) # remove None values
        self.dlg.cboNumber.blockSignals(True)
        self.dlg.cboNumber.clear()
        for record in records:
            self.dlg.cboNumber.addItem(record[1], record[0])
        self.dlg.cboNumber.blockSignals(False)        
    
    
    def resetEquipments(self):
        ''' Populate equipments combo depending on selected type. 
        Available equipments EQUIPMENT_FIELD_NAME belonging to the same EQUIPMENT_FIELD_TYPE of 
        the same layer EQUIPMENT_LAYER
        '''
        if not self.connection:
            return
        
        # get selected street
        selectedCode = self.dlg.cboType.currentText()
        if selectedCode == '':
            return
        
        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # now get the list of names belonging to the current type
        sqlquery = 'SELECT id, "{}" FROM "{}"."{}" WHERE "{}" = %s ORDER BY "{}"; '.format(self.EQUIPMENT_FIELD_NAME, self.EQUIPMENT_SCHEMA, self.EQUIPMENT_LAYER, self.EQUIPMENT_FIELD_TYPE, self.EQUIPMENT_FIELD_NAME)
        params = [selectedCode]
        cursor.execute(sqlquery, params)
        records = [(-1, '')]
        records.extend( [x for x in cursor.fetchall() if x[1]] ) # remove None values
        self.dlg.cboEquipment.blockSignals(True)
        self.dlg.cboEquipment.clear()
        for record in records:
            self.dlg.cboEquipment.addItem(record[1], record[0])
        self.dlg.cboEquipment.blockSignals(False) 
    
    
    def validateX(self):   
        X = int(self.dlg.txtCoordX.text())
        if X > self.xMinVal and X < self.xMaxVal:
            return True
        else:
            return False
            
            
    def validateY(self):       
        Y = int(self.dlg.txtCoordY.text())
        if Y > self.yMinVal and Y < self.yMaxVal:
            return True
        else:
            return False      
            
    
    def deleteFeatures(self, layer):
    
        if layer is not None:
            it = layer.getFeatures()
            ids = [i.id() for i in it]
            layer.dataProvider().deleteFeatures(ids)    
            layer.commitChanges()            

            
    # Copy from selected layer to memory layer
    def copySelected(self, layer, mem_layer, geom_type):
            
        # Create memory layer if not already set
        if mem_layer is None: 
            uri = geom_type+"?crs=epsg:25831" 
            mem_layer = QgsVectorLayer(uri, "selected_"+layer.name(), "memory")                     
         
            # Copy attributes from main layer to memory layer
            attrib_names = layer.dataProvider().fields()
            names_list = attrib_names.toList()
            newattributeList = []
            for attrib in names_list:
                aux = mem_layer.fieldNameIndex(attrib.name())
                if aux == -1:
                    newattributeList.append(QgsField(attrib.name(), attrib.type()))
            mem_layer.dataProvider().addAttributes(newattributeList)
            mem_layer.updateFields()
            
            # Insert layer in the top of the TOC           
            root = QgsProject.instance().layerTreeRoot()           
            QgsMapLayerRegistry.instance().addMapLayer(mem_layer, False)
            node_layer = QgsLayerTreeLayer(mem_layer)
            root.insertChildNode(0, node_layer)                 
     
        # Prepare memory layer for editing
        mem_layer.startEditing()

        # Delete previous features
        self.deleteFeatures(mem_layer)
        
        # Iterate over selected features   
        cfeatures = []
        for sel_feature in layer.selectedFeatures():
            attributes = []
            attributes.extend(sel_feature.attributes())
            cfeature = QgsFeature()    
            cfeature.setGeometry(sel_feature.geometry())
            cfeature.setAttributes(attributes)
            cfeatures.append(cfeature)
                     
        # Add features, commit changes and refresh canvas
        mem_layer.dataProvider().addFeatures(cfeatures)             
        mem_layer.commitChanges()
        self.iface.mapCanvas().refresh() 
        self.iface.mapCanvas().zoomToSelected(layer)
        
        # Make sure layer is always visible 
        self.iface.legendInterface().setLayerVisible(mem_layer, True)
                    
        return mem_layer
        
        
    def loadStyle(self, layer, qml):
    
        path_qml = self.stylesFolder+qml      
        if os.path.exists(path_qml): 
            layer.loadNamedStyle(path_qml)          

        
    def displayUTM(self):
        ''' Show UTM location on the canvas when set it in the relative tab
        '''                     
        X = self.dlg.txtCoordX.text()
        if not X:
            message = "Coordinate X not specified"
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return
        Y = self.dlg.txtCoordY.text()  
        if not Y:
            message = "Coordinate Y not specified"
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)           
            return
        
        # check if coordinates are within the interval
        valX = self.validateX()
        if not valX:
            message = "Coordinate X is out of the valid interval. It should be between "+str(self.xMinVal)+" and "+str(self.xMaxVal)
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return
        valY = self.validateY()
        if not valY:
            message = "Coordinate Y is out of the valid interval, It should be between "+str(self.yMinVal)+" and "+str(self.yMaxVal)
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return            
            
        geom = QgsGeometry.fromPoint(QgsPoint(float(X), float(Y)))
        message = 'X: {}\nY: {}'.format(X,Y)
        
        # display annotation with message at a specified position
        self.displayAnnotation(geom, message)
    
    
    def displayCadastre(self):
        ''' Show cadastre data on the canvas when selected it in the relative tab
        '''
        # preconditions
        if not self.connection:
            return
        
        cadastre = self.dlg.cboCadastre.currentText()
        if cadastre == '':
            return
        
        # get the id of the selected item
        id = self.dlg.cboCadastre.itemData(self.dlg.cboCadastre.currentIndex())
        if not id:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(cadastre))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return

        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # tab Cadastre
        sqlquery = 'SELECT ST_AsText(geom) FROM "{}"."{}" WHERE id = %s'.format(self.CADASTRE_SCHEMA, self.CADASTRE_LAYER)
        params = [id] 
        cursor.execute(sqlquery, params)
        row = cursor.fetchone()
        if not row:  
            return
        
        # select this feature in order to copy to memory layer        
        aux = "id = "+str(id) 
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, "searchplus", QgsMessageBar.WARNING, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained             
        it = self.cadastreLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.cadastreLayer.setSelectedFeatures(ids)    
                
        # Copy selected features to memory layer          
        self.cadastreMemLayer = self.copySelected(self.cadastreLayer, self.cadastreMemLayer, "Polygon")         
         
        # Load style
        self.loadStyle(self.cadastreMemLayer, "cadastre.qml")  

        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))             
        
         
    def displayEquipment(self):
        ''' Show equipment data on the canvas when selected it in the relative tab
        '''
        # preconditions
        if not self.connection:
            return

        typ = self.dlg.cboType.currentText()
        if typ == '':
            return
        
        equipment = self.dlg.cboEquipment.currentText()
        if equipment == '':
            return
        
        # get the id of the selected item
        id = self.dlg.cboEquipment.itemData(self.dlg.cboEquipment.currentIndex())
        if not id:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(equipment))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return

        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # tab Equipments
        sqlquery = 'SELECT ST_AsText(geom) FROM "{}"."{}" WHERE id = %s'.format(self.EQUIPMENT_SCHEMA, self.EQUIPMENT_LAYER)
        params = [id]           
        cursor.execute(sqlquery, params)
        row = cursor.fetchone()
        if not row:  
            return
        
        # select this feature in order to copy to memory layer        
        aux = "id = "+str(id) 
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, "searchplus", QgsMessageBar.WARNING, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained             
        it = self.equipmentLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.equipmentLayer.setSelectedFeatures(ids)
        
        # Copy selected features to memory layer          
        self.equipmentMemLayer = self.copySelected(self.equipmentLayer, self.equipmentMemLayer, "Point")       

        # Zoom to point layer
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
        
        # Load style
        self.loadStyle(self.equipmentMemLayer, "equipment.qml")          

        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))        
         
         
    def displayToponym(self):
        ''' Show toponym data on the canvas when selected it in the relative tab
        '''
        # preconditions
        if not self.connection:
            return

        toponym = self.dlg.cboTopo.currentText()   
        if toponym == '':
            return
        
        # get the id of the selected toponym
        id = self.dlg.cboTopo.itemData(self.dlg.cboTopo.currentIndex())
        if not id:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(toponym))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return

        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # tab Toponyms
        sqlquery = 'SELECT ST_AsText(geom) FROM "{}"."{}" WHERE id = %s'.format(self.PLACENAME_SCHEMA, self.PLACENAME_LAYER)        
        params = [id]
        cursor.execute(sqlquery, params)
        row = cursor.fetchone()
        if not row:   
            return

        # select this feature in order to copy to memory layer        
        aux = "id = "+str(id)         
        expr = QgsExpression(aux)            
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, "searchplus", QgsMessageBar.WARNING, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained       
        it = self.placenameLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.placenameLayer.setSelectedFeatures(ids)    
                
        # Copy selected features to memory layer
        self.placenameMemLayer = self.copySelected(self.placenameLayer, self.placenameMemLayer, "Linestring")
        
        # Load style
        self.loadStyle(self.placenameMemLayer, "toponym.qml")        
        
        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))        
         
         
    def displayStreetData(self):
        ''' Show street data on the canvas when selected street and number in street tab
        '''          
        # preconditions
        if not self.connection:
            return

        street = self.dlg.cboStreet.currentText()
        if street == '':
            return
        
        civic = self.dlg.cboNumber.currentText()
        if civic == '':
            return
        
        # get the id of the selected portal
        id = self.dlg.cboNumber.itemData(self.dlg.cboNumber.currentIndex())
        if not id:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(civic))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 5)
            return

        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # now get the list of indexes belonging to the current code
        sqlquery = 'SELECT ST_AsText(geom) FROM "{}"."{}" WHERE id = %s; '.format(self.PORTAL_SCHEMA, self.PORTAL_LAYER)    
        params = [id]     
        cursor.execute(sqlquery, params)
        row = cursor.fetchone()
        if not row:  
            return
        
        # select this feature in order to copy to memory layer        
        aux = "id = "+str(id) 
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, "searchplus", QgsMessageBar.WARNING, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select featureswith the ids obtained             
        it = self.portalLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.portalLayer.setSelectedFeatures(ids)
        
        # Copy selected features to memory layer          
        self.portalMemLayer = self.copySelected(self.portalLayer, self.portalMemLayer, "Point")       

        # Zoom to point layer
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
        
        # Load style
        self.loadStyle(self.portalMemLayer, "portal.qml")         
        
        
    def displayAnnotation(self, geom, message):
        ''' Display a specific message in the centroid of a specific geometry
        '''
        centroid = geom.centroid()
        
        # clean previous annotations:
        for annotation in self.annotations:
            try:
                scene = annotation.scene()
                if scene:
                    scene.removeItem(annotation)
            except:
                # annotation can be erased by QGIS interface
                pass
        self.annotations = []
        
        # build annotation
        textDoc = QTextDocument(message)
        item = QgsTextAnnotationItem(self.iface.mapCanvas())
        item.setMapPosition(centroid.asPoint())
        item.setFrameSize(textDoc.size())
        item.setDocument(textDoc)
        item.update()
        
        # add to annotations
        self.annotations.append(item)
        
        # center in the centroid
        self.iface.mapCanvas().setCenter(centroid.asPoint())
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
        self.iface.mapCanvas().refresh()
    
    
    def run(self):
        """Run method activated byt the toolbar action button"""         
        if self.dlg and not self.dlg.isVisible():
            # check if the plugin is active
            if not self.pluginName in active_plugins:
                return
            self.getLayers()
            self.getFullExtent()            
            self.dlg.show()
        
        # if not, setup connection               
        if not self.connection:
            self.initConnection()      
            

