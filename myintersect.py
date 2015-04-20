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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant,QPyNullVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
# Initialize Qt resources from file resources.py
import resources_rc
from qgis.core import *
from qgis.gui import *
# Import the code for the dialog
from myintersect_dialog import MyIntersectDialog
import os.path
import os
import re, shutil

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

        self.initMy()
        self.initTest()
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
        #layerList = self.iface.mapCanvas().layers()
##        for layer in layerList:
##            if (layer.type() == layer.VectorLayer ) and ( layer.geometryType() == QGis.Polygon ):
##                self.dlg.budynkiComboBox.addItem(layer.name())
##                self.dlg.dzialkiComboBox.addItem(layer.name())

        self.budynkiButton = self.dlg.budynkiButton.clicked.connect(self.setBudynki)
        self.dzialkiButton = self.dlg.dzialkiButton.clicked.connect(self.setDzialki)
        self.budynkiPath = None
        self.dzialkiPath = None
        self.raw_number = 'NR_RAW'
        self.idFiledName = 'id_raw'
    def initTest(self):

        self.testButton =  self.dlg.testButton.clicked.connect(self.testtest)
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
        """intersect"""


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
        #fields = fieldList1
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






    def addAndCopy(self, filePath, oldFileName, newFieldName):
        """pobiera plik i dodaje nowe pole RAW i kopiuje z NUMER do RAW"""


        layer_path = filePath
        layer = self.setLayer(layer_path)
        provider = layer.dataProvider()
        fieldsList = provider.fields()
        #print fieldsList
        #fieldsCount=  len(fieldsList)
        #field_index = 0

        provider.addAttributes([QgsField(newFieldName, QVariant.String)])
        #
        layer.updateFields()
        #layer = QgsVectorLayer(filePath ,os.path.splitext(filePath)[0], 'ogr')
        #provider = layer.dataProvider()

        index_newFieldName=0
        index_oldFileName = 0
        fieldsList = provider.fields()
        index_newFieldName = self.getIndex(provider, newFieldName)
        index_oldFileName = self.getIndex(provider, oldFileName)
        for feature in provider.getFeatures():
            fid = feature.id()
            atr = {index_newFieldName: str(feature[index_oldFileName])}
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


















        self.iface.addVectorLayer(filePath, 'temLayer', 'ogr')



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
        """ustawia sciezke do budynkow"""
        if self.dzialkiPath:
            self.workDirPath = os.path.dirname(self.dzialkiPath)
        else:
            self.workDirPath= "d:/tempdata/"
        self.budynkiPath = QFileDialog.getOpenFileName(self.dlg, 'Open file', self.workDirPath, "*.shp")
        self.dlg.budynki_label.setText(os.path.basename(self.budynkiPath))
        self.temDirPath = self.workDirPath+"/temp/"
    def setDzialki(self):
        """ustawia sciezke do dzialek"""
        if self.budynkiPath:
             self.workDirPath = os.path.dirname(self.budynkiPath)
        else:
            self.workDirPath= ""

        self.dzialkiPath = QFileDialog.getOpenFileName(self.dlg, 'Open file', self.workDirPath, "*.shp")
        self.dlg.dzialki_label.setText(os.path.basename(self.dzialkiPath))
        self.temDirPath = self.workDirPath+"/temp/"

    def polygon_centroids(self, filePath, outfile):
        """tworzy warstwe sentroidow z podanej warstwy"""

        layer = self.setLayer(filePath)
        layer.featureCount()
        vprovider = layer.dataProvider()
        self.vproviderCRS = vprovider.crs()
###################################################3

        buildings = os.path.basename(filePath)[:-4]
        writer = QgsVectorFileWriter( outfile,'CP1250', vprovider.fields(),
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

##
##    def getVectorLayerByName( self, myName ):
##        layermap = QgsMapLayerRegistry.instance().mapLayers()
##        for name, layer in layermap.iteritems():
##            if layer.type() == QgsMapLayer.VectorLayer and layer.name() == myName:
##                if layer.isValid():
##                    return layer
##                else:
##                    return None

    def cleanFields(self, filePath, filedName):
        print 'in cleanFields'

        layer = self.setLayer(filePath)
        provider = layer.dataProvider()
        field_index = self.getIndex(provider, filedName)
        caps = provider.capabilities()
        field_list =  provider.fields()
        for field in range(len(field_list)):
            if caps and QgsVectorDataProvider.DeleteAttributes:
                if field <> field_index:
                    provider.deleteAttributes([field])

        layer.updateFields()




    def setLayer(self, filePath):
        print 'in setLayer'
        return QgsVectorLayer(filePath,os.path.splitext(filePath)[0], 'ogr')

    def getIndex(self, dataProvider, fieldName):
        print 'in getIndex'
        fieldList = dataProvider.fields()
        field_index = 0
        i = 0
        for field in fieldList:
            if field.name()== fieldName:
                field_index = i
            i+=1
        return field_index

    def addToMap(self, filePath):
        file_name = os.path.basename(filePath)[:-4]
        self.iface.addVectorLayer(filePath, file_name, 'ogr')

    def onlyOneField(self, filePath, outFilePath, fieldName):

        raw_layer = self.setLayer(filePath)
        raw_provider = raw_layer.dataProvider()
        fields = [ QgsField(fieldName, QVariant.String), QgsField(self.idFiledName, QVariant.Int)]
        seq = range(0, len(fields))
        fieldList1 = dict(zip(seq, fields))
        fields = QgsFields()
        for f in fieldList1.values():
          fields.append(f)
        sRs = raw_provider.crs()
        writer = QgsVectorFileWriter(outFilePath, 'CP1250', fields, raw_provider.geometryType(),sRs )


        fet = QgsFeature()
        feature = QgsFeature()
        index_num = self.getIndex(raw_provider, fieldName)
        index_id = self.getIndex(raw_provider, self.idFiledName)
        for feature in raw_provider.getFeatures():
            #print 'w petli waznej'
            fet.setGeometry(feature.geometry())
            fet.setAttributes([feature.attributes()[index_num], feature.attributes()[index_id]])
            writer.addFeature(fet)
        del writer


    def addField(self, filePath, fieldName):
        """dodaje pole a nastepnie ID"""
##    def addField(self):
##        filePath = 'd:/tempdata/temp/bud_cen_is_dz.shp'
##        fieldName = 'raw_id'
        layer = self.setLayer(filePath)
        provider = layer.dataProvider()
        field = [QgsField(self.idFiledName, QVariant.Int)]
        provider.addAttributes(field)
        layer.updateFields()
        index =  self.getIndex(provider, fieldName)
        i=0
        for feature in provider.getFeatures():
            fid = feature.id()
            #print fid
            atr = {index:i}
            #print(atr)

            provider.changeAttributeValues({fid: atr})
            i+=1
        layer.updateFields()





        #self.addToMap(filePath)





    def selectByAtr(self, filePath, outFile):
    #def selectByAtr(self):
        #filePath = 'd:/tempdata/temp/dzialki_wezly_buffer06.shp'
        #outFile = 'd:/tempdata/temp/dzialki_wezly_buffer06_sel.shp'
        layer = self.setLayer(filePath)
        provider = layer.dataProvider()
        featuers = provider.getFeatures()
        index_raw = self.getIndex(provider, self.raw_number)
        index_new = self.getIndex(provider, 'NUMER')
        index_id =  self.getIndex(provider, self.idFiledName)
        fields = [ QgsField("NUMER", QVariant.String),QgsField(self.raw_number, QVariant.String), QgsField(self.idFiledName, QVariant.Int)]


        seq = range(0, len(fields))
        fieldList1 = dict(zip(seq, fields))
        fields = QgsFields()
        for f in fieldList1.values():
          fields.append(f)
        sRs = provider.crs()
        writer = QgsVectorFileWriter(outFile, 'CP1250', fields, provider.geometryType(),sRs )









        fet = QgsFeature()

        for reat in featuers:
            if reat.attributes()[index_raw]<> reat.attributes()[index_new]:
                #print reat.attributes()[index_raw], reat.attributes()[index_new]
                fet.setGeometry(reat.geometry())
                fet.setAttributes([reat.attributes()[index_new], reat.attributes()[index_raw], reat.attributes()[index_id]])
                writer.addFeature(fet)




        print 'end'
        del writer
        #self.addToMap(outFile)



    def polygons_to_lines( self, filePath, outFilePath ):
    #def polygons_to_lines( self ):
        #filePath= 'D:/tempdata/BUDYNKI_OLIMPOWO.shp'
        #outFilePath ='d:/tempdata/temp/dzialki_olimpowD_line.shp'
        vlayer = self.setLayer(filePath)
        vprovider = vlayer.dataProvider()


        fields = vprovider.fields()
        seq = range(0, len(fields))
        fieldList1 = dict(zip(seq, fields))
        fields = QgsFields()
        for f in fieldList1.values():
          fields.append(f)



        writer = QgsVectorFileWriter( outFilePath, "CP1250", fields,
                                  QGis.WKBLineString, vprovider.crs() )
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()
        nFeat = vprovider.featureCount()
        nElement = 0
        #self.emit( SIGNAL( "runStatus( PyQt_PyObject )" ), 0)
        #self.emit( SIGNAL( "runRange( PyQt_PyObject )" ), ( 0, nFeat ) )

        fit = vprovider.getFeatures()
        while fit.nextFeature( inFeat ):
          multi = False
          nElement += 1
          #self.emit( SIGNAL( "runStatus( PyQt_PyObject )" ),  nElement )
          inGeom = inFeat.geometry()
          if inGeom.isMultipart():
            multi = True
          atMap = inFeat.attributes()
          lineList = self.extractAsLine( inGeom )
          outFeat.setAttributes( atMap )
          for h in lineList:
            outFeat.setGeometry( outGeom.fromPolyline( h ) )
            writer.addFeature( outFeat )
        del writer
        #self.addToMap(outFilePath)
        return True








    def extractAsLine( self, geom ):
        multi_geom = QgsGeometry()
        temp_geom = []
        if geom.type() == 2:
          if geom.isMultipart():
            multi_geom = geom.asMultiPolygon()
            for i in multi_geom:
              temp_geom.extend( i )
          else:
            multi_geom = geom.asPolygon()
            temp_geom = multi_geom
          return temp_geom
        else:
          return []




    def getFinallAtr(self, filePath):
    #def getFinallAtr(self):
        #filePath = 'd:/tempdata/temp/wezly_buff_sel_IS_dzi_lines.shp'
        layer = self.setLayer(filePath)
        provider = layer.dataProvider()
        features = provider.getFeatures()
        numer = self.getIndex(provider, "NUMER")
        index_id = self.getIndex(provider, self.idFiledName)
        value =set()
        for featin in features:
            data = featin.attributes()[numer]
            #print data#, QVariant(data)
            if data == None:
                #print featin.attributes()[index_id]
                value.add(featin.attributes()[index_id])
        return value

    def addInfo(self, valueSet, filePath):
        """dodaje tak lub nie dla dzialek ze wzgledu na to czy sa na liscie"""

        layer = self.setLayer(filePath)
        provider = layer.dataProvider()
        index_id = self.getIndex(provider, self.idFiledName)
        features = provider.getFeatures()


        provider.addAttributes([QgsField("_info_", QVariant.String)])
        layer.updateFields()
        index_info = self.getIndex(provider, '_info_')


        for featin in features:
            data = featin.attributes()[index_id]
            fid = featin.id()
            if data in valueSet:

                atr = {index_info: 'tak'}
                print data
            else:
                atr = {index_info: 'nie'}
            provider.changeAttributeValues({fid: atr})
        layer.updateFields()
        #self.addToMap(filePath)





    def runApp(self):

#   0 utworzyc tempdir
        self.temDirPath = self.workDirPath+"/temp/"
        if not os.path.exists(self.temDirPath):
            os.mkdir(self.temDirPath)
#
#   1 dzialki -> nowe dzialki
        flayer = self.dzialkiPath
        olayer = self.temDirPath+os.path.basename(flayer)
        self.dzialkiJednaKoluna(flayer, olayer)
        self.dzialkiPath = olayer

#   2 budynki -> centroids
        flayer = self.budynkiPath
        olayer = self.temDirPath+os.path.basename(flayer)+'_centroid.shp'
        self.polygon_centroids(flayer, olayer)
#   3 intersect centroidy i dzialki
        flayer = olayer
        slayer = self.dzialkiPath
        olayer = self.temDirPath+'bud_cen_is_dz.shp'
        self.run_intersect(flayer, slayer, olayer)
#   4 mieszanie z polami

        self.addAndCopy(olayer, 'NUMER', self.raw_number)

        flayer = olayer
        self.addField(flayer, self.idFiledName)
        olayer = self.temDirPath+'bud_cen_is_dz_1col.shp'
        self.onlyOneField(flayer, olayer, self.raw_number)

#   5 intersect budynki_raw i budynki centroid -> budynki_poligony maja id i raw_numer
        flayer = self.budynkiPath
        slayer = olayer
        olayer = self.temDirPath +"budynki_update_raw_num.shp"
        bud_update_path = olayer #to musi byc tu, bo pozniej jest potrzebne
        self.run_intersect(flayer, slayer, olayer)

#   6 tworzy wezly
        flayer= olayer
        olayer = self.temDirPath+'budynki_wezly.shp'
        self.extract_nodes(flayer, olayer)

#   7 intersect wezly i dzialki -> wezly z numerem dzialki - tu juz widac roznice
        flayer = olayer
        slayer = self.dzialkiPath
        olayer = self.temDirPath+'budynki_wezly_intersec_dzialki.shp'
        self.run_intersect(flayer, slayer, olayer)

#   8 buffer wezlow i nic wicej
        flayer = olayer
        olayer = self.temDirPath+'dzialki_wezly_buffer06.shp'
        self.nodeBuffer(flayer,olayer)

#   9 wybor tylko tych wezlo_buffer, ktore maja rozne NUMER i RAW_NUMER
        flayer = olayer
        olayer = self.temDirPath+'dzialki_wezly_buff06_sel.shp'
        self.selectByAtr(flayer, olayer)
#   10 linie z poligonow
        flayer = self.dzialkiPath
        olayer = self.temDirPath+"dzialki_poly_2_line.shp"
        self.polygons_to_lines(self.dzialkiPath, olayer)
#   11 usuwa pola z wezlow buffor, zostawia tylko ID
        inlayer =self.temDirPath+'dzialki_wezly_buff06_sel.shp'
        self.deleteNumFields(inlayer)



#   12 intersect dzialki wezly buffer sel i linie
#    - otrzymamy info czy nasze buffory sie przecinaja z liniami dzialek
        flayer = self.temDirPath+'dzialki_wezly_buff06_sel.shp'
        slayer = olayer
        olayer = self.temDirPath +'wezly_buff_sel_IS_dzi_lines.shp'
        self.run_intersect(flayer, slayer, olayer)


# tam gdzie null w kolumnie NUMER tzn. tam jest budynek na 2 działkach

#   13 tworzy set z lista tych o roznym raw_numer i NUMER
#    -  budykom raw dodaje tak lub nie
        flayer = olayer
        slayer = bud_update_path
        self.update_budynki(flayer, slayer)
        self.addToMap(slayer)
#   14 kopije pliki i zwraca nazwe nowego pliku + laduje go do mapy
##        flayer = bud_update_path
##        slayer = self.temDirPath
##        newName = os.path.basename(self.budynkiPath)[:-4]+'_nowe.shp'
##        finalFile = self.copyFile(flayer, slayer, newName)



#########################################################
#########################################################
#########################################################

        def cos(self):
# cos slabego
            flayer = self.budynkiPath
            slayer = olayer
            olayer = self.temDirPath +"budynki_update_raw_num.shp"
            bud_update_path = olayer

            self.run_intersect(flayer, slayer, olayer)
# end cos slaboego
            #self.addField(olayer, self.idFiledName)


# cos slabego
            flayer= olayer
            olayer = self.temDirPath+'budynki_wezly.shp'
            self.extract_nodes(flayer, olayer)
# end cos slaboego
# cos slabego
            flayer = olayer
            slayer = self.dzialkiPath
            olayer = self.temDirPath+'budynki_wezly_intersec_dzialki.shp'
            self.run_intersect(flayer, slayer, olayer)

# end cos slaboego












            #kopiuje w














        QMessageBox.about(self.dlg, "info", 'Zakonoczo')
        #
        self.addToMap(olayer)
        #






    def testtest(self):
        filePath = 'd:/tempdata/temp/budynki_update_raw_num.shp'
        old_file =  os.path.basename(filePath)[:-4]
        dirPath = 'd:/tempdata/temp/'



        newName = 'Budynki_wynik.shp'
        print old_file
        os.chdir(dirPath)
        os.chdir('..')
        destDir = os.getcwd()+'/'
        os.chdir(dirPath)
        print destDir
        fileList= os.listdir( os.getcwd())
        copyList = []
        for obj in fileList:
            if re.search(old_file, obj):
                print obj
                ext = obj[-4:]
                print ext
                shutil.copy(obj, destDir+newName+ext)

        return destDir+newName+'.shp'






    def update_budynki(self, filePath, budPat):
        """tworzy zbior z numerami dzialek (my ID) """

        set_value_list = self.getFinallAtr(filePath)


        self.addInfo(set_value_list, budPat)
    def copyFile(self, filePath, dirPath, newName):
        #filePath = 'd:/tempdata/temp/budynki_update_raw_num.shp'
        old_file =  os.path.basename(filePath)[:-4]
        #dirPath = 'd:/tempdata/temp/'




        print old_file
        os.chdir(dirPath)
        os.chdir('..')
        destDir = os.getcwd()+'/'
        os.chdir(dirPath)
        print destDir
        fileList= os.listdir( os.getcwd())
        copyList = []
        for obj in fileList:
            if re.search(old_file, obj):
                print obj
                ext = obj[-4:]
                print ext
                shutil.copy(obj, destDir+newName+ext)
        return destDir+newName+'.shp'

    def dzialkiJednaKoluna(self, dzialkiPath, dzialkiOutputPath):
        """wczytuje warstwe dzialek i wtorzy nowa z tylo jedna kolumna NUMER"""

        layer = self.setLayer(dzialkiPath)
        prvider = layer.dataProvider()
        numer_name = "NUMER"
        fields = [ QgsField(numer_name, QVariant.String)]
        seq = range(0, len(fields))
        fieldList1 = dict(zip(seq, fields))
        fields = QgsFields()
        for f in fieldList1.values():
          fields.append(f)
        sRs = prvider.crs()
        writer = QgsVectorFileWriter(dzialkiOutputPath, 'CP1250', fields, prvider.geometryType(),sRs )
        features = prvider.getFeatures()
        index_numer = self.getIndex(prvider, numer_name)
        print index_numer
        for fil in  prvider.fields():
            print fil.name()
        new_feat= QgsFeature()
        for fet in features:
            geom = fet.geometry()
            atr = fet.attributes()[index_numer]
            new_feat.setGeometry(geom)
            #print atr
            new_feat.setAttributes([fet.attributes()[index_numer]])
            writer.addFeature(new_feat)
        del writer


    def deleteNumFields(self, filePath):
    #def deleteNumFields(self):
        #filePath = 'd:/tempdata/temp/dzialki_wezly_buff06_sel.shp'
        layer = self.setLayer(filePath)
        provider = layer.dataProvider()
        index_numer = self.getIndex(provider, "NUMER")
        provider.deleteAttributes([index_numer])
        layer.updateFields()
        index_raw_numer =self.getIndex(provider, self.raw_number)
        provider.deleteAttributes([index_raw_numer])
        layer.updateFields()
        #self.addToMap(filePath)





