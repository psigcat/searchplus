# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/search_plus_dialog_base.ui'
#
# Created: Wed Jun 24 13:02:43 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_searchPlusDockWidget(object):
    def setupUi(self, searchPlusDockWidget):
        searchPlusDockWidget.setObjectName(_fromUtf8("searchPlusDockWidget"))
        searchPlusDockWidget.resize(347, 209)
        searchPlusDockWidget.setLocale(QtCore.QLocale(QtCore.QLocale.Catalan, QtCore.QLocale.Spain))
        searchPlusDockWidget.setFloating(True)
        searchPlusDockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        searchPlusDockWidget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.contents = QtGui.QWidget()
        self.contents.setObjectName(_fromUtf8("contents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.contents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.searchPlusTabMain = QtGui.QTabWidget(self.contents)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.searchPlusTabMain.setFont(font)
        self.searchPlusTabMain.setLocale(QtCore.QLocale(QtCore.QLocale.Catalan, QtCore.QLocale.Spain))
        self.searchPlusTabMain.setObjectName(_fromUtf8("searchPlusTabMain"))
        self.searchPlusStreetsTab = QtGui.QWidget()
        self.searchPlusStreetsTab.setObjectName(_fromUtf8("searchPlusStreetsTab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.searchPlusStreetsTab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblStreet = QtGui.QLabel(self.searchPlusStreetsTab)
        self.lblStreet.setObjectName(_fromUtf8("lblStreet"))
        self.horizontalLayout_2.addWidget(self.lblStreet)
        self.cboStreet = SearchableComboBox(self.searchPlusStreetsTab)
        self.cboStreet.setEditable(True)
        self.cboStreet.setObjectName(_fromUtf8("cboStreet"))
        self.horizontalLayout_2.addWidget(self.cboStreet)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblNumber = QtGui.QLabel(self.searchPlusStreetsTab)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.horizontalLayout_3.addWidget(self.lblNumber)
        self.cboNumber = SearchableComboBox(self.searchPlusStreetsTab)
        self.cboNumber.setEditable(True)
        self.cboNumber.setObjectName(_fromUtf8("cboNumber"))
        self.horizontalLayout_3.addWidget(self.cboNumber)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.searchPlusTabMain.addTab(self.searchPlusStreetsTab, _fromUtf8(""))
        self.searchPlusToponimsTab = QtGui.QWidget()
        self.searchPlusToponimsTab.setObjectName(_fromUtf8("searchPlusToponimsTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.searchPlusToponimsTab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.lblTopo = QtGui.QLabel(self.searchPlusToponimsTab)
        self.lblTopo.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lblTopo.setWordWrap(True)
        self.lblTopo.setObjectName(_fromUtf8("lblTopo"))
        self.verticalLayout_3.addWidget(self.lblTopo)
        self.cboTopo = SearchableComboBox(self.searchPlusToponimsTab)
        self.cboTopo.setEditable(True)
        self.cboTopo.setObjectName(_fromUtf8("cboTopo"))
        self.verticalLayout_3.addWidget(self.cboTopo)
        self.searchPlusTabMain.addTab(self.searchPlusToponimsTab, _fromUtf8(""))
        self.searchPlusEquipmentsTab = QtGui.QWidget()
        self.searchPlusEquipmentsTab.setObjectName(_fromUtf8("searchPlusEquipmentsTab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.searchPlusEquipmentsTab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.lblType = QtGui.QLabel(self.searchPlusEquipmentsTab)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.horizontalLayout_4.addWidget(self.lblType)
        self.cboType = SearchableComboBox(self.searchPlusEquipmentsTab)
        self.cboType.setEditable(True)
        self.cboType.setObjectName(_fromUtf8("cboType"))
        self.horizontalLayout_4.addWidget(self.cboType)
        self.horizontalLayout_4.setStretch(1, 1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.lblEquipment = QtGui.QLabel(self.searchPlusEquipmentsTab)
        self.lblEquipment.setObjectName(_fromUtf8("lblEquipment"))
        self.horizontalLayout_5.addWidget(self.lblEquipment)
        self.cboEquipment = SearchableComboBox(self.searchPlusEquipmentsTab)
        self.cboEquipment.setEditable(True)
        self.cboEquipment.setObjectName(_fromUtf8("cboEquipment"))
        self.horizontalLayout_5.addWidget(self.cboEquipment)
        self.horizontalLayout_5.setStretch(1, 1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.searchPlusTabMain.addTab(self.searchPlusEquipmentsTab, _fromUtf8(""))
        self.searchPlusCadastreTab = QtGui.QWidget()
        self.searchPlusCadastreTab.setObjectName(_fromUtf8("searchPlusCadastreTab"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.searchPlusCadastreTab)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.lblCadastre = QtGui.QLabel(self.searchPlusCadastreTab)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lblCadastre.setFont(font)
        self.lblCadastre.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lblCadastre.setWordWrap(True)
        self.lblCadastre.setObjectName(_fromUtf8("lblCadastre"))
        self.verticalLayout_5.addWidget(self.lblCadastre)
        self.txtCadastre = QtGui.QLineEdit(self.searchPlusCadastreTab)
        self.txtCadastre.setObjectName(_fromUtf8("txtCadastre"))
        self.verticalLayout_5.addWidget(self.txtCadastre)
        self.searchPlusTabMain.addTab(self.searchPlusCadastreTab, _fromUtf8(""))
        self.searchPlusUTMTab = QtGui.QWidget()
        self.searchPlusUTMTab.setObjectName(_fromUtf8("searchPlusUTMTab"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.searchPlusUTMTab)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.lblUTM = QtGui.QLabel(self.searchPlusUTMTab)
        self.lblUTM.setWordWrap(True)
        self.lblUTM.setObjectName(_fromUtf8("lblUTM"))
        self.verticalLayout_6.addWidget(self.lblUTM)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_8 = QtGui.QLabel(self.searchPlusUTMTab)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_6.addWidget(self.label_8)
        self.txtCoordX = QtGui.QLineEdit(self.searchPlusUTMTab)
        self.txtCoordX.setObjectName(_fromUtf8("txtCoordX"))
        self.horizontalLayout_6.addWidget(self.txtCoordX)
        self.horizontalLayout_6.setStretch(1, 1)
        self.verticalLayout_6.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.label_9 = QtGui.QLabel(self.searchPlusUTMTab)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_7.addWidget(self.label_9)
        self.txtCoordY = QtGui.QLineEdit(self.searchPlusUTMTab)
        self.txtCoordY.setObjectName(_fromUtf8("txtCoordY"))
        self.horizontalLayout_7.addWidget(self.txtCoordY)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.searchPlusTabMain.addTab(self.searchPlusUTMTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.searchPlusTabMain)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(self.contents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        searchPlusDockWidget.setWidget(self.contents)

        self.retranslateUi(searchPlusDockWidget)
        self.searchPlusTabMain.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(searchPlusDockWidget)

    def retranslateUi(self, searchPlusDockWidget):
        searchPlusDockWidget.setWindowTitle(_translate("searchPlusDockWidget", "Cercadors", None))
        self.lblStreet.setText(_translate("searchPlusDockWidget", "    Carrer:", None))
        self.lblNumber.setText(_translate("searchPlusDockWidget", "Número:", None))
        self.searchPlusTabMain.setTabText(self.searchPlusTabMain.indexOf(self.searchPlusStreetsTab), _translate("searchPlusDockWidget", "Carrerer", None))
        self.lblTopo.setText(_translate("searchPlusDockWidget", "Desplegueu per seleccionar un topònim; escriviu per constrènyer la cerca (per exemple, \"can\"):", None))
        self.searchPlusTabMain.setTabText(self.searchPlusTabMain.indexOf(self.searchPlusToponimsTab), _translate("searchPlusDockWidget", "Topònims", None))
        self.lblType.setText(_translate("searchPlusDockWidget", "             Tipus:", None))
        self.lblEquipment.setText(_translate("searchPlusDockWidget", "Equipament:", None))
        self.searchPlusTabMain.setTabText(self.searchPlusTabMain.indexOf(self.searchPlusEquipmentsTab), _translate("searchPlusDockWidget", "Equipaments", None))
        self.lblCadastre.setText(_translate("searchPlusDockWidget", "Introduïu la referència cadastral i premeu Acceptar (exemple: \'5123501DF1952S\'):", None))
        self.searchPlusTabMain.setTabText(self.searchPlusTabMain.indexOf(self.searchPlusCadastreTab), _translate("searchPlusDockWidget", "Cadastre", None))
        self.lblUTM.setText(_translate("searchPlusDockWidget", "Introduïu el parell de coordenades i premeu Acceptar (exemple: X \'415165\', Y \'4592355\'):", None))
        self.label_8.setText(_translate("searchPlusDockWidget", "X:", None))
        self.label_9.setText(_translate("searchPlusDockWidget", "Y:", None))
        self.searchPlusTabMain.setTabText(self.searchPlusTabMain.indexOf(self.searchPlusUTMTab), _translate("searchPlusDockWidget", "UTM", None))
        self.pushButton.setText(_translate("searchPlusDockWidget", "Recerca", None))

from custom_widgets.searchable_combobox import SearchableComboBox
