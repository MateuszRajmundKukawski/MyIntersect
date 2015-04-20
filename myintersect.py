# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MyIntersect
                                 A QGIS plugin
 MyIntersect
                              -------------------
        begin                : 2015-04-19
        git sha              : $Format:%H$
        copyright            : (C) 2015 by MRK
        email                : mrkukawski@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources_rc
from qgis.core import *
from qgis.gui import *
# Import the code for the dialog
from myintersect_dialog import MyIntersectDialog
import os.path


class MyIntersect:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MyIntersect_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = MyIntersectDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MyIntersect')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'MyIntersect')
        self.toolbar.setObjectName(u'MyIntersect')
        self.basePath = '/home/mati/Dokumenty/wtykadane/'
        self.runButton =  self.dlg.runButton.clicked.connect(self.runApp)
        self.deleteButton =  self.dlg.deleteButton.clicked.connect(self.polygon_centroids)
        self.initMy()
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
        return QCoreApplication.translate('MyIntersect', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MyIntersect/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'MyIntersect'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def initMy(self):
        #self.dlg.budynkiComboBox.addItem('')
        layerList = self.iface.mapCanvas().layers()
        for layer in layerList:
            if (layer.type() == layer.VectorLayer ) and ( layer.geometryType() == QGis.Polygon ):
                self.dlg.budynkiComboBox.addItem(layer.name())
                self.dlg.dzialkiComboBox.addItem(layer.name())
        self.wrokDirButton = self.dlg.wrokDirButton.clicked.connect(self.setWorDir)
        self.budynkiButton = self.dlg.budynkiButton.clicked.connect(self.setBudynki)
        self.dzialkiButton = self.dlg.dzialkiButton.clicked.connect(self.setDzialki)
        self.budynkiPath = None
        self.dzialkiPath = None
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MyIntersect'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass



        pass
    def run_intersect(self, baseLayerPath, infoLayerPath, outLayerPath):


        self.point_file_path = baseLayerPath
        self.polygon_file_path = infoLayerPath
        self.outLayerPath = outLayerPath

        #warstwa uaktualniana
        #self.point_file_path = '/home/mati/Dokumenty/wtykadane/budynki.shp'
        #warstwa z danymi do pobrania
       # self.polygon_file_path = '/home/mati/Dokumenty/wtykadane/wyniki/wynik2.shp'
        self.point_layer = QgsVectorLayer(self.point_file_path,
                                          os.path.splitext(self.point_file_path)[0], 'ogr')
        self.polygon_layer = QgsVectorLayer(self.polygon_file_path,os.path.splitext(self.polygon_file_path)[0], 'ogr')
        self.polygon_provider =  self.polygon_layer.dataProvider()
        self.point_provider =  self.point_layer.dataProvider()
        #print('punktow:', self.point_provider.featureCount(),)
        #print('poligonow:', self.polygon_provider.featureCount())

        #print 'Kliknieto'

        findex = self.getSpatialIndex(self.point_provider)
        #print(type(findex))
        findexlist = self.getInsert(findex, self.polygon_provider)
        #print( findexlist,)
        #fields()
        fieldList1= self.point_provider.fields()
        fieldList2 = self.polygon_provider.fields()
        seq = range(0, len(fieldList1) + len(fieldList2))
        fieldList1.extend(fieldList2)
        fieldList1 = dict(zip(seq, fieldList1))
        fields = QgsFields()
        for f in fieldList1.values():
          fields.append(f)






        index = self.getSpatialIndex(self.polygon_provider)
        sRs = self.point_provider.crs()
        writer1 = QgsVectorFileWriter(self.outLayerPath, 'CP1250', fields, self.point_provider.geometryType(),sRs )
        #writer1 = QgsVectorFileWriter('/home/mati/Dokumenty/wtykadane/wynik2.shp', 'CP1250', fields, self.polygon_provider.geometryType(),sRs )

        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inFeatB = QgsFeature()
        fit1 = self.point_provider.getFeatures()
        while fit1.nextFeature(inFeat): #dla punktow
            #print 'in while'
            inGeom = inFeat.geometry()
            atMap1 = inFeat.attributes()
            outFeat.setGeometry(inGeom)
            none = True
            joinList = []
            if inGeom.type() == QGis.Point:
                #(check, joinList) = layer2.featuresInRectangle(inGeom.buffer(10,2).boundingBox(), True, True)
                #layer2.select(inGeom.buffer(10,2).boundingBox(), False)
                #joinList = layer2.selectedFeatures()
                joinList = index.intersects( inGeom.buffer(10,2).boundingBox() )
                #print 'len(joinList)', len(joinList)
            else:
                joinList = index.intersects( inGeom.boundingBox() )
                'len(joinList)', len(joinList)



            #joinList = index.intersects( inGeom.boundingBox() )
            #raw_input('nacisjin')
            for i in joinList:
               # print 'in joinList for'
                self.polygon_provider.getFeatures( QgsFeatureRequest().setFilterFid( int(i) ) ).nextFeature( inFeatB )
                tempGeom = QgsGeometry( inFeatB.geometry() )
                #print 'in join za self'

                if inGeom.intersects(inFeatB.geometry()):
                    #print 'w if inGeom.intersects(inFeatB.geometry()):'
                    atMap2 = inFeatB.attributes()
                    atMap = atMap1
                    atMap2 = atMap2
                    atMap.extend(atMap2)
                    atMap = dict(zip(seq, atMap))
                    atMap1.extend(atMap2)
                    #print 'in last loop'
                    #break
            outFeat.setAttributes(atMap1)
            writer1.addFeature(outFeat)
            #writer2.addFeature(outFeat)
        del writer1
        #del writer2
        print 'END'
        print 'first:',self.point_file_path, 'type:', type(self.point_layer)
        print 'second', self.polygon_file_path, 'type:', type(self.polygon_layer)






    def addAdnCopy(self, filePath, oldFileName, newFieldName):
        layer_path = filePath
        layer = QgsVectorLayer(filePath ,os.path.splitext(filePath)[0], 'ogr')
        provider = layer.dataProvider()
        fieldsList = provider.fields()
        #print fieldsList
        fieldsCount=  len(fieldsList)
        field_index = 0
        i=0
        layer.dataProvider().addAttributes([QgsField(newFieldName, QVariant.String)])
        #
        layer.updateFields()
        layer = QgsVectorLayer(filePath ,os.path.splitext(filePath)[0], 'ogr')
        provider = layer.dataProvider()

        index_newFieldName=0
        index_oldFileName = 0
        fieldsList = provider.fields()
        for f in fieldsList:
            if f.name() == newFieldName:
                index_newFieldName = i
            elif f.name() == oldFileName:
                index_oldFileName = i
            i+=1


        exp = QgsExpression('99')
        #exp.prepare(layer.pendingFields())
        for feature in provider.getFeatures():
            fid = feature.id()
            #print fid
            atr = {index_newFieldName: str(feature[index_oldFileName])}
            #print(atr)

            provider.changeAttributeValues({fid: atr})
        layer.updateFields()



    def deleteAll(self, filePath, fieldName):
        layer = QgsVectorLayer(filePath ,os.path.splitext(filePath)[0], 'ogr')
        provider = layer.dataProvider()
        fieldList = provider.fields()
        index_fieldName = 0
        i = 0
        for field in fieldList:
            print field.name()
            if field.name()==fieldName:
                index_fieldName = i
            i+=1
        print fieldList[index_fieldName].name(), fieldName, fieldList[-1].name()
        kk = 0
        for kk in range(len(fieldList)):
            if kk<> index_fieldName:
                layer.dataProvider().deleteAttributes([kk])











        # for name, i in zip(provider.fields(), range(len( provider.fields()))):
        #
        #     #print name.name(), type(i), type(index_newFieldName)
        #     if  i <> index_newFieldName:
        #         print name.name(), type(i), type(index_newFieldName)
        #         layer.dataProvider().deleteAttributes([i])
        #
        #
        # layer.updateFields()
        # fieldsList = provider.fields()
        # delIndex = 0
        # kk = 0
        # for f in fieldsList:
        #     if f.name()== newFieldName:
        #         delIndex = kk
        #     kk+=1
        # for name, i in zip(provider.fields(), range(len( provider.fields()))):
        #
        #     #print name.name(), type(i), type(index_newFieldName)
        #     if  i <> delIndex:
        #         print name.name(), type(i), type(delIndex)
        #         layer.dataProvider().deleteAttributes([i])
        #
        #
        #









        self.iface.addVectorLayer(filePath, 'temLayer', 'ogr')
        #self.iface.addVectorLayer(self.budynkiPath, 'buuu', 'ogr')






        # def delete_all(newFieldName):
        #     for field in fieldsList:
        #         print 'w petli'
        #         print field.name()
        #         if field.name()== fieldName:
        #             field_index = i
        #         i+=1
        #     layer.dataProvider().addAttributes([QgsField(newFieldName, QVariant.String)])
        #
        #     print(field_index)
        #     for index in range(fieldsCount):
        #         if index<> field_index:
        #             provider.deleteAttributes([index])
        #
        #
        #     #provider.deleteAttributes([del_index])
        #     layer.updateFields()


    def getSpatialIndex(self, workLayer):
        index = QgsSpatialIndex()
        for feature in workLayer.getFeatures():
            index.insertFeature(feature)
        return index
    def getInsert(self, spatial_index, workLayer):
        index_list = []
        for feature in workLayer.getFeatures():
            #print(feature, type(feature), feature['numer'])
            geom = QgsGeometry(feature.geometry())
            #print(geom.area(),)
            index_list.append(spatial_index.intersects(geom.boundingBox()))
        return index_list


    def extract_nodes( self, plygon_layer_path, output_layer_path):
        layer = QgsVectorLayer(plygon_layer_path,os.path.splitext(plygon_layer_path)[0], 'ogr')


        vprovider = layer.dataProvider()
        writer = QgsVectorFileWriter( output_layer_path, "CP1250", vprovider.fields(),
                                      QGis.WKBPoint, vprovider.crs() )
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()
        nFeat = vprovider.featureCount()
        nElement = 0
        #self.emit( SIGNAL( "runStatus( PyQt_PyObject )" ), 0 )
        #self.emit( SIGNAL( "runRange( PyQt_PyObject )" ), ( 0, nFeat ) )
        fit = vprovider.getFeatures()
        while fit.nextFeature( inFeat ):
          nElement += 1
          #self.emit( SIGNAL( "runStatus( PyQt_PyObject )" ),  nElement )
          inGeom = inFeat.geometry()
          atMap = inFeat.attributes()
          pointList = self.extractPoints( inGeom )
          outFeat.setAttributes( atMap )
          for i in pointList:
            outFeat.setGeometry( outGeom.fromPoint( i ) )
            writer.addFeature( outFeat )
        del writer
        return True
    def extractPoints(self, geom ):
        multi_geom = QgsGeometry()
        temp_geom = []
        if geom.type() == 0: # it's a point
            if geom.isMultipart():
                temp_geom = geom.asMultiPoint()
            else:
                temp_geom.append(geom.asPoint())
        if geom.type() == 1: # it's a line
            if geom.isMultipart():
                multi_geom = geom.asMultiPolyline() #multi_geog is a multiline
                for i in multi_geom: #i is a line
                    temp_geom.extend( i )
            else:
                temp_geom = geom.asPolyline()
        elif geom.type() == 2: # it's a polygon
            if geom.isMultipart():
                multi_geom = geom.asMultiPolygon() #multi_geom is a multipolygon
                for i in multi_geom: #i is a polygon
                    for j in i: #j is a line
                        temp_geom.extend( j )
            else:
                multi_geom = geom.asPolygon() #multi_geom is a polygon
                for i in multi_geom: #i is a line
                    temp_geom.extend( i )
        return temp_geom
    def nodeBuffer(self, node_file_path, out_file_path):
        layer = QgsVectorLayer(node_file_path,os.path.splitext(node_file_path)[0], 'ogr')
        provider = layer.dataProvider()
       #writer = QgsVectorFileWriter(self.outLayerPath, 'CP1250', fields, self.point_provider.geometryType(),sRs )
        fields = provider.fields()
        writer = QgsVectorFileWriter(out_file_path, "CP1250", fields, QGis.WKBMultiPolygon, provider.crs())
        #QGis.WKBMultiPolygon





        features = provider.getFeatures()
        new_features = []
        for feature in features:
            feature.setGeometry(feature.geometry().buffer(0.6, 20))
            new_features.append(features)
            writer.addFeature(feature)

        del writer


    def setWorDir(self):
        pass


    def setBudynki(self):
        if self.dzialkiPath:
            self.workDirPath = os.path.dirname(self.dzialkiPath)
        else:
            self.workDirPath= ""
        self.budynkiPath = QFileDialog.getOpenFileName(self.dlg, 'Open file', self.workDirPath, "*.shp")
        self.dlg.budynki_label.setText(os.path.basename(self.budynkiPath))

    def setDzialki(self):
        if self.budynkiPath:
             self.workDirPath = os.path.dirname(self.budynkiPath)
        else:
            self.workDirPath= ""

        self.dzialkiPath = QFileDialog.getOpenFileName(self.dlg, 'Open file', self.workDirPath, "*.shp")
        self.dlg.dzialki_label.setText(os.path.basename(self.dzialkiPath))


    def polygon_centroids(self):
        # buildings = str(self.dlg.budynkiComboBox.currentText())
        # self.vlayer = buildings
        # mapCanvas = self.iface.mapCanvas()
        #
        # self.buildingsLayer = self.getVectorLayerByName(buildings)
        # layer = self.buildingsLayer
        layer = QgsVectorLayer(self.budynkiPath,os.path.splitext(self.budynkiPath)[0], 'ogr')

        layer.featureCount()
        vprovider = layer.dataProvider()
        #print vprovider
        self.vproviderCRS = vprovider.crs()
        #komuniakt = buildings + ": " + str(layer.featureCount())
        #QMessageBox.about(self.dlg, 'test', komuniakt)
        #outFilePath
###################################################3
        self.temDirPath = self.workDirPath+"/temp/"
        if not os.path.exists(self.temDirPath):
            os.mkdir(self.temDirPath)
        buildings = os.path.basename(self.budynkiPath)[:-4]
        self.centroid_file = self.temDirPath+buildings+'_centroid.shp'
        writer = QgsVectorFileWriter( self.centroid_file,'CP1250', vprovider.fields(),
                                  QGis.WKBPoint, vprovider.crs(),'ESRI Shapefile' )
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        nFeat = vprovider.featureCount()
        nElement = 0
        fit = vprovider.getFeatures()
        while fit.nextFeature( inFeat ):
            nElement += 1
            inGeom = inFeat.geometry()
            atMap = inFeat.attributes()
            outGeom = inGeom.centroid()
            if outGeom is None:
                return "math_error"
            outFeat.setAttributes( atMap )
            outFeat.setGeometry( QgsGeometry( outGeom ) )
            writer.addFeature( outFeat )
        del writer

    # def chuj(self):
    #                 """Run method that performs all the real work"""
    #     # show the dialog
    #     self.dlg.show()
    #     # Run the dialog event loop
    #     result = self.dlg.exec_()
    #     # See if OK was pressed
    #     if result:
    #         # Do something useful here - delete the line containing pass and
    #         # substitute with your code.
    #         distance = self.dlg.distance_buf.value()
    #         new_distance = 0
    #         number = self.dlg.number_buf.value()
    #         layer = self.iface.activeLayer()
    #         selected = layer.selectedFeatures()
    #         crs = layer.crs()
    #         print layer.name()
    #         for i in range(0,number):
    #             new_distance += distance
    #             result = QgsVectorLayer("Polygon?crs=" + str(crs.authid()), "result_" + str(new_distance), "memory")
    #             new_features = []
    #             result_provider = result.dataProvider()
    #             for feature in selected:
    #                 feature.setGeometry(feature.geometry().buffer(new_distance,20))
    #                 new_features.append(feature)
    #             result_provider.addFeatures(new_features)
    #             QgsMapLayerRegistry.instance().addMapLayer(result)
    #         pass
    def getVectorLayerByName( self, myName ):
        layermap = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layermap.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer and layer.name() == myName:
                if layer.isValid():
                    return layer
                else:
                    return None
    def runApp(self):
        # self.basePath = '/home/mati/Dokumenty/wtykadane/'
        # #first intersect
        # flayer =self.basePath+'budynki_centroids.shp'
        # slayer =self.basePath+'dzialki.shp'
        # olayer =self.basePath+'wyniki/bud_cen_is_dz.shp'

        self.polygon_centroids()
        flayer = self.centroid_file
        slayer = self.dzialkiPath
        olayer = self.temDirPath+'bud_cen_is_dz.shp'






        self.run_intersect(flayer, slayer, olayer)

        self.addAdnCopy(olayer, 'NUMER', 'RAW_NUMER')
        #self.deleteAll(olayer, "RAW_NUMER")
        #self.deleteAll(olayer, "RAW_NUMER")
        # flayer = self.basePath+'budynki.shp'
        # slayer = olayer
        # olayer = self.basePath+'wyniki/budynki_id_dzialki.shp'
        # self.run_intersect(flayer, slayer, olayer)
        # flayer = olayer
        # olayer = self.basePath+'wyniki/budynki_id_dzialki_nodes.shp'
        # self.extract_nodes(flayer,olayer )
        # flayer = olayer
        # olayer = self.basePath+"wyniki/buffer_06.shp"
        # self.nodeBuffer(flayer, olayer)