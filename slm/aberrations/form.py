# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created: Wed Feb 26 17:06:59 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(348, 189)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayoutWidget = QtGui.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 329, 171))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.astigCheck = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.astigCheck.setObjectName(_fromUtf8("astigCheck"))
        self.gridLayout.addWidget(self.astigCheck, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.defocusCheck = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.defocusCheck.setObjectName(_fromUtf8("defocusCheck"))
        self.gridLayout.addWidget(self.defocusCheck, 0, 1, 1, 1)
        self.defocusAmpl = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.defocusAmpl.setObjectName(_fromUtf8("defocusAmpl"))
        self.gridLayout.addWidget(self.defocusAmpl, 0, 2, 1, 1)
        self.astigAmpl = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.astigAmpl.setObjectName(_fromUtf8("astigAmpl"))
        self.gridLayout.addWidget(self.astigAmpl, 1, 2, 1, 1)
        self.astigAngle = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.astigAngle.setObjectName(_fromUtf8("astigAngle"))
        self.gridLayout.addWidget(self.astigAngle, 1, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.fitButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.fitButton.setObjectName(_fromUtf8("fitButton"))
        self.horizontalLayout_2.addWidget(self.fitButton)
        self.applyButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.applyButton.setObjectName(_fromUtf8("applyButton"))
        self.horizontalLayout_2.addWidget(self.applyButton)
        self.saveButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout_2.addWidget(self.saveButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Defocus", None, QtGui.QApplication.UnicodeUTF8))
        self.astigCheck.setToolTip(QtGui.QApplication.translate("Form", "fit", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Astigmatism", None, QtGui.QApplication.UnicodeUTF8))
        self.defocusCheck.setToolTip(QtGui.QApplication.translate("Form", "fit", None, QtGui.QApplication.UnicodeUTF8))
        self.defocusAmpl.setToolTip(QtGui.QApplication.translate("Form", "amplitude", None, QtGui.QApplication.UnicodeUTF8))
        self.astigAmpl.setToolTip(QtGui.QApplication.translate("Form", "amplitude", None, QtGui.QApplication.UnicodeUTF8))
        self.astigAngle.setToolTip(QtGui.QApplication.translate("Form", "angle", None, QtGui.QApplication.UnicodeUTF8))
        self.fitButton.setText(QtGui.QApplication.translate("Form", "Fit", None, QtGui.QApplication.UnicodeUTF8))
        self.applyButton.setText(QtGui.QApplication.translate("Form", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("Form", "Save", None, QtGui.QApplication.UnicodeUTF8))

