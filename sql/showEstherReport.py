#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6 SQL App for signed Esther Reports
Python version of http://esther.tecnico.ulisboa.pt/esther-php/show_report.php
"""

import sys

from PyQt6.QtCore import QSize  # , Qt

from PyQt6.QtGui import QFont
# from PyQt6 import QtWidgets

from PyQt6.QtSql import (
    QSqlDatabase,
    # QSqlRelation,
    # QSqlRelationalDelegate,
    # QSqlRelationalTableModel,
    QSqlTableModel,
    QSqlQuery,
    QSqlQueryModel,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QTableView,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget,
    QDialog,
    QDialogButtonBox, QPushButton,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QRadioButton,
    QLabel,
    QTableWidget, QTableWidgetItem,
    # QSizePolicy,
    QAbstractScrollArea
)

import config_local as cfg
# from epics import caget  # , caput  # , cainfo

# import os

# os.environ['EPICS_CA_ADDR_LIST'] = '10.10.136.128'
# os.environ['EPICS_CA_ADDR_LIST'] = 'localhost 192.168.1.110'
# os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'

# basedir = os.path.dirname(__file__)

# db = QSqlDatabase("QSQLITE")
#  d b.setDatabaseName(os.path.join(basedir, "chinook.sqlite"))

CENTIG_ZERO = 273.15  # K
BAR_TO_ATM = 1.013

ADJUSTTOCONTENTS_POL = QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents

db = QSqlDatabase("QMARIADB")
db.setHostName(cfg.host)
db.setDatabaseName(cfg.database)
db.setUserName(cfg.username)
db.setPassword(cfg.password)
db.open()


def partial_volume(pBar, tempC, chambVolL):
    tempK = tempC + CENTIG_ZERO
    parVol = pBar / BAR_TO_ATM / tempK * CENTIG_ZERO * chambVolL
    return parVol


class SignDialog(QDialog):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)

        # print("Pare: " + str(parent.shotNo))
        self.setWindowTitle("Sign Line!")

        buttons = (
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Sure you want to sign this Checkline?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.shotNo = 298
        self.signBy = 0
        self.lastSigned = 0
        self.tableReports = QTableView()
        container = QWidget()
        layoutMain = QHBoxLayout()
        layoutTools = QVBoxLayout()
        layoutTables = QVBoxLayout()

        self.search = QLineEdit()

        # add_rec = QPushButton("Add record")
        # add_rec.clicked.connect(self.add_row)

        refreshButt = QPushButton("Refresh")
#        refreshButt.clicked.connect(self.refresh_model)

#        layoutTools.addWidget(add_rec)
#        self.list = QLineEdit()
#        self.list.setPlaceholderText("1")
#        self.list.textChanged.connect(self.update_query)
        shotSpin = QSpinBox()
        shotSpin.setMinimum(10)
        shotSpin.setMaximum(1000)  # May need to change (hopefully)
# Or: widget.setRange(-10,3)
# widget.setPrefix("$")
# widget.setSuffix("c")
        shotSpin.setSingleStep(1)  # Or e.g. 0.5 for QDoubleSpinBox
        shotSpin.setValue(self.shotNo)
        shotSpin.valueChanged.connect(self.shot_changed)
        layoutTools.addWidget(shotSpin)

        tableModelReports = QSqlTableModel(db=db)
        tableModelReports.setTable('esther_reports')
        tableModelReports.setFilter("shot_number > 160")
        tableModelReports.select()

        self.tableViewReports = QTableView()
        self.tableViewReports.setModel(tableModelReports)

        self.tableBottles = QTableWidget(3, 6)
        labels = ('O2 Bottle', 'He I Bottle', 'H2 Bottle',
                  'He II Bottle', 'N2 Bottle', 'N2 Command Bottle',)
        self.tableBottles.setHorizontalHeaderLabels(labels)
        # ("O2 Bottle","He I Bottle","H2 Bottle",'He II Bottle','N2 Bottle', 'N2 Command Bottle'))
        self.tableBottles.resizeColumnToContents(5)
        self.tableBottles.setVerticalHeaderLabels(('Initial', 'Final', 'Delta'))
        self.tableBottles.setSizeAdjustPolicy(ADJUSTTOCONTENTS_POL)

        # QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # self.tableBottles.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding) # ---
        # self.tableBottles.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum) # ---
        self.tableBottles.setAlternatingRowColors(True)
        # self.tableBottles.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)# +++

        self.tablePartial = QTableWidget(1, 6)
        self.tablePartial.setVerticalHeaderLabels(('',))
        self.tablePartial.setHorizontalHeaderLabels((
            'N2/He Purge', 'Oxigen Fill', 'Helium I Fill',
            'Hidrogen Fill', 'Helium II Fill', 'Target'))
        self.tablePartial.resizeColumnsToContents()
        # self.tablePartial.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # self.tablePartial.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.tablePartial.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)

        self.tableVolumes = QTableWidget(4, 6)
        self.tableVolumes.setHorizontalHeaderLabels((
            'Initial', 'Oxigen', 'Helium I', 'Hidrogen', 
            'Helium II', 'Total Helium'))
        self.tableVolumes.setVerticalHeaderLabels((
            'Setting', 'Measured', 'Mol Rat O2', 'Mol Rat H2'))
        # self.tableVolumes.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        layoutTools.addWidget(refreshButt)
#        layoutTools.addWidget(QLabel('Exp. Phase'))
        layoutGrd = QGridLayout()
        # layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()
        self.Date = QLabel('Date 11-10-2021 ')
        layoutV.addWidget(self.Date)
        self.Manager = QLabel('Manager: Mário Lino da Silva')
        layoutV.addWidget(self.Manager)
        self.STime = QLabel('Start Time: 14:21:48')
        layoutV.addWidget(self.STime)
        self.RTime = QLabel('Rest Time 00:34:00')
        layoutV.addWidget(self.RTime)
        self.AmbTemp = QLabel('Amb. Temp')
        layoutV.addWidget(self.AmbTemp)

        layoutGrd.addLayout(layoutV, 0, 0)
        # layoutH.addLayout(layoutV)
        layoutV = QVBoxLayout()
        label = QLabel('Bottle Pressures / Bar')
        label.setFont(QFont('Arial', 16))
        layoutV.addWidget(label)
        self.tableBottles.setSizeAdjustPolicy(ADJUSTTOCONTENTS_POL)
        layoutV.addWidget(self.tableBottles)

        layoutGrd.addLayout(layoutV, 0, 1)
        layoutGrd.setRowStretch(0, 3)

        layoutV = QVBoxLayout()
        self.Ratio = QLabel('He/H2/O2 Ratio:')
        layoutV.addWidget(self.Ratio)
        self.DKistler = QLabel('delta_P_kistler:')
        layoutV.addWidget(self.DKistler)
        layoutGrd.addLayout(layoutV, 1, 0)

        layoutV = QVBoxLayout()
        label = QLabel('Partial Pressures / Bar')
        label.setFont(QFont('Arial', 16))

        layoutV.addWidget(label)
        self.tablePartial.setSizeAdjustPolicy(ADJUSTTOCONTENTS_POL)
        layoutV.addWidget(self.tablePartial)
        # layoutH.addLayout(layoutV)
        layoutGrd.addLayout(layoutV, 1, 1)
        # layoutTables.addWidget(self.tablePartial, stretch=1)
        # layoutGrd.setSizeAdjustPolicy(ADJUSTTOCONTENTS_POL)
        layoutTables.addLayout(layoutGrd, stretch=3)
        # layoutTables.addLayout(layoutH, stretch=1)

        label = QLabel('Partial Volumes / nL')
        label.setFont(QFont('Arial', 20))
        layoutTables.addWidget(label)
        layoutTables.addWidget(self.tableVolumes, stretch=3)

        # QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableVolumes.setSizeAdjustPolicy(ADJUSTTOCONTENTS_POL)
        # QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        layoutTables.addWidget(self.tableViewReports)

        layoutMain.addLayout(layoutTools)
        layoutMain.addLayout(layoutTables)
        container.setLayout(layoutMain)
        self.setMinimumSize(QSize(1200, 700))
        self.setCentralWidget(container)
        self.update_queryReports()
        self.update_Report()

    def setTableCell(self, qR, table, name, lin, col):
        val = qR.value(name)
        item = QTableWidgetItem(f'{val:0.2f}')
        table.setItem(lin, col, item)

    def setBottleCells(self, qR, table, bottle, col):
        name = bottle + '_initial'
        valI = qR.value(name)
        item = QTableWidgetItem(f'{valI:0.2f}')
        table.setItem(0, col, item)
        name = bottle + '_final'
        valF = qR.value(name)
        item = QTableWidgetItem(f'{valF:0.2f}')
        table.setItem(1, col, item)
        item = QTableWidgetItem(f'{valI-valF:0.2f}')
        table.setItem(2, col, item)

    def set_table_val(self, table, val, lin, col):
        item = QTableWidgetItem(f'{val:0.2f}')
        table.setItem(lin, col, item)

    def shot_changed(self, i):
        print('shot is ' + str(i))
        self.shotNo = i
        self.update_queryReports()
        self.update_Report()

    def updateTables(self, shotNo):
        queryTables = QSqlQuery(db=db)
        queryTables.prepare(
            "SELECT *, esther_managers.manager_name "
            "FROM esther_reports "
            "INNER JOIN esther_managers ON esther_reports.manager_id = "
            "esther_managers.manager_id "
            "WHERE shot_number  = :shot_no "
        )

        queryTables.bindValue(":shot_no", shotNo)
        queryTables.exec()
        if queryTables.first():
            # val  = queryReport.value(2)
            self.Date.setText(
                    'Date: ' + queryTables.value('start_time').toString('dd-MM-yyyy'))
            self.Manager.setText('Manager: ' + queryTables.value('manager_name'))
            self.STime.setText('Start Time: ' + queryTables.value('start_time').toString('hh:mm:ss'))
            ratioStr = (
                    f"He/H2/O2 Ratio: {queryTables.value('He_ratio_sp')}/"
                    f"{queryTables.value('H2_ratio_sp')}/"
                    f"{queryTables.value('O2_ratio_sp')}  ")
            self.Ratio.setText(ratioStr)
            dKStr = (
                    u'Δ PKistler/ Range'
                    # "delta_P_kistler / Range: "
                    f"{queryTables.value('delta_P_kistler')} / "
                    f"{queryTables.value('range_kistler')} Bar.")
            self.DKistler.setText(dKStr)
            qRep = queryTables
            tB = self.tableBottles
            self.setBottleCells(qRep, tB, 'O2_bottle', 0)
            # self.setTableCell(qRep, tB, 'O2_bottle_initial', 0, 0)
            # self.setTableCell(qRep, tB, 'O2_bottle_final', 1, 0)
            self.setBottleCells(qRep, tB, 'He1_bottle', 1)
            self.setBottleCells(qRep, tB, 'H_bottle', 2)
            self.setBottleCells(qRep, tB, 'He2_bottle', 3)
            self.setBottleCells(qRep, tB, 'N2_bottle', 4)
            self.setTableCell(qRep, tB, 'N2_command_bottle_initial', 0, 5)
            self.setTableCell(qRep, tB, 'N2_command_bottle_final', 1, 5)
            self.tableBottles.setColumnWidth(5, 100)
#            self.tableBottles.setAlternatingRowColors(True)
            # lastOK      = queryReport.value(1)
            # item = QTableWidgetItem(f'{val:0.2f}')
            # #item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            # self.tableBottles.setItem(0,4, item)
            # self.setTableCell(queryReport, self.tablePartial, 'pt901_end_s1', 0, 0)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_s1', 0, 0)
            tB = self.tablePartial
            pS1 = qRep.value('pt901_end_s1')
            self.set_table_val(tB, pS1, 0, 0)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_o', 0, 1)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_o', 0, 1)
            pO = qRep.value('pt901_end_o')
            self.set_table_val(tB, pO, 0, 1)
            pHe1 = qRep.value('pt901_end_he1')
            self.set_table_val(tB, pHe1, 0, 2)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_he1', 0, 2)
            pH = qRep.value('pt901_end_h')
            self.set_table_val(tB, pH, 0, 3)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_h', 0, 3)
            pHe2 = qRep.value('pt901_end_he2')
            self.set_table_val(tB, pHe2, 0, 4)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_he2', 0, 4)
            self.setTableCell(qRep, tB, 'pt901_target', 0, 5)

            mfcSpHe1 = qRep.value('mfc_601_He1_sp')
            mfcSpHe2 = qRep.value('mfc_601_He2_sp')
            self.setTableCell(qRep, self.tableVolumes, 'bombe_volume', 0, 0)
            self.setTableCell(qRep, self.tableVolumes, 'mfc_201_O_sp', 0, 1)
            # self.set_table_val(self.tableVolumes, mfcSpHe2, 0, 2)
            # self.setTableCell(qRep, self.tableVolumes, 'mfc_601_He1_sp', 0, 2)
            self.set_table_val(self.tableVolumes, mfcSpHe1, 0, 2)
            self.setTableCell(qRep, self.tableVolumes, 'mfc_401_H_sp', 0, 3)
            self.set_table_val(self.tableVolumes, mfcSpHe2, 0, 4)
            chVol = qRep.value('bombe_volume')
            tAmb = qRep.value('ambient_temperature')
            pAmb = qRep.value('ambient_pressure') / 1000.0
            # pS1 = pS1 + pAmb
# def partial_volume(pBar, tempC, chambVolL):
            vHe0 = partial_volume(pS1 + pAmb, tAmb, chVol)
            vO = partial_volume(pO - pS1, tAmb, chVol)
            vHe1 = partial_volume(pHe1 - pO, tAmb, chVol)
            vH = partial_volume(pH - pHe1, tAmb, chVol)
            vHe2 = partial_volume(pHe2 - pH, tAmb, chVol)
            vHeTotal = vHe0 + vHe1 + vHe2
            # vTotal = partial_volume(pHe2 + pAmb, tAmb, chVol)
            self.set_table_val(self.tableVolumes, vHe0, 1, 0)
            self.set_table_val(self.tableVolumes, vO, 1, 1)
            self.set_table_val(self.tableVolumes, vHe1, 1, 2)
            self.set_table_val(self.tableVolumes, vH, 1, 3)
            self.set_table_val(self.tableVolumes, vHe2, 1, 4)

            self.set_table_val(self.tableVolumes, 1.0, 2, 1)
            if vO > 0:
                self.set_table_val(self.tableVolumes, vH / vO, 2, 3)
                self.set_table_val(self.tableVolumes, vHeTotal / vO, 2, 5)
            self.set_table_val(self.tableVolumes, vH / vO, 2, 3)
            self.set_table_val(self.tableVolumes, vHeTotal / vO, 2, 5)
            if vH > 0:
                self.set_table_val(self.tableVolumes, vO / vH * 2.0, 3, 1)
                self.set_table_val(self.tableVolumes, vHeTotal / vH * 2.0, 3, 5)
            self.set_table_val(self.tableVolumes, 2.0, 3, 3)
            # print('PP ' + str(chVol) + ' pAmb:' + str(pAmb))
        else:
            val = 0
            lastLineId = 0
            print('No Report')
        # print(queryReport.lastQuery() + str(val))

    def update_Report(self, s=None):
        self.updateTables(self.shotNo)
        """
        queryReport = QSqlQuery(db=db)
        queryReport.prepare(
            "SELECT *, esther_managers.* "
            "FROM esther_reports "
            "INNER JOIN esther_managers ON esther_reports.manager_id = "
            "esther_managers.manager_id "
            "WHERE shot_number  = :shot_no "
        )
        queryReport.prepare(
            "SELECT shot_number, esther_reports.manager_id, "
            "O2_bottle_initial, O2_bottle_final, He1_bottle_initial, He1_bottle_final, "
            "H_bottle_initial, H_bottle_final, N2_bottle_initial, N2_bottle_final, "
            "pt901_end_s1, pt901_end_o, pt901_end_he1, pt901_end_h, pt901_end_he2, pt901_target, "
            "esther_managers.manager_name, start_time, end_time "
            "FROM esther_reports "
            "INNER JOIN esther_managers ON esther_reports.manager_id = esther_managers.manager_id "
            #"WHERE shot_number  > 160 "
            "WHERE shot_number  = :shot_no "
        )

        queryReport.bindValue(":shot_no", self.shotNo)
        queryReport.exec()
        if queryReport.first():
            # val  = queryReport.value(2)
            qRep = queryReport
            tB = self.tableBottles
            self.setTableCell(qRep, tB, 'O2_bottle_initial', 0, 0)
            self.setTableCell(qRep, tB, 'O2_bottle_final', 1, 0)
            self.setTableCell(qRep, tB, 'He1_bottle_initial', 0, 1)
            self.setTableCell(qRep, tB, 'He1_bottle_final', 1, 1)
            self.setTableCell(qRep, tB, 'H_bottle_initial', 0, 2)
            self.setTableCell(qRep, tB, 'H_bottle_final', 1, 2)
            self.setTableCell(qRep, tB, 'He2_bottle_initial', 0, 3)
            self.setTableCell(qRep, tB, 'He2_bottle_final', 1, 3)
            self.setTableCell(qRep, tB, 'N2_bottle_initial', 0, 4)
            self.setTableCell(qRep, tB, 'N2_bottle_final', 1, 4)
            self.setTableCell(qRep, tB, 'N2_command_bottle_initial', 0, 5)
            self.setTableCell(qRep, tB, 'N2_command_bottle_final', 1, 5)
            self.tableBottles.setColumnWidth(5, 100)
#            self.tableBottles.setAlternatingRowColors(True)
            # lastOK      = queryReport.value(1)
            # item = QTableWidgetItem(f'{val:0.2f}')
            # #item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            # self.tableBottles.setItem(0,4, item)
            # self.setTableCell(queryReport, self.tablePartial, 'pt901_end_s1', 0, 0)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_s1', 0, 0)
            tB = self.tablePartial
            pS1 = qRep.value('pt901_end_s1')
            self.set_table_val(tB, pS1, 0, 0)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_o', 0, 1)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_o', 0, 1)
            pO = qRep.value('pt901_end_o')
            self.set_table_val(tB, pO, 0, 1)
            pHe1 = qRep.value('pt901_end_he1')
            self.set_table_val(tB, pHe1, 0, 2)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_he1', 0, 2)
            pH = qRep.value('pt901_end_h')
            self.set_table_val(tB, pH, 0, 3)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_h', 0, 3)
            pHe2 = qRep.value('pt901_end_he2')
            self.set_table_val(tB, pHe2, 0, 4)
            # self.setTableCell(qRep, self.tablePartial, 'pt901_end_he2', 0, 4)
            self.setTableCell(qRep, tB, 'pt901_target', 0, 5)

            self.setTableCell(qRep, self.tableVolumes, 'bombe_volume', 0, 0)
            chVol = qRep.value('bombe_volume')
            tAmb = qRep.value('ambient_temperature')
            pAmb = qRep.value('ambient_pressure') / 1000.0
            # pS1 = pS1 + pAmb
# def partial_volume(pBar, tempC, chambVolL):
            vHe0 = partial_volume(pS1 + pAmb, tAmb, chVol)
            vO = partial_volume(pO - pS1, tAmb, chVol)
            vHe1 = partial_volume(pHe1 - pO, tAmb, chVol)
            vH = partial_volume(pH - pHe1, tAmb, chVol)
            vHe2 = partial_volume(pHe2 - pH, tAmb, chVol)
            vHeTotal = vHe0 + vHe1 + vHe2
            vTotal = partial_volume(pHe2 + pAmb, tAmb, chVol)
            self.set_table_val(self.tableVolumes, vHe0, 1, 0)
            self.set_table_val(self.tableVolumes, vO, 1, 1)
            self.set_table_val(self.tableVolumes, vHe1, 1, 2)
            self.set_table_val(self.tableVolumes, vH, 1, 3)
            self.set_table_val(self.tableVolumes, vHe2, 1, 4)

            self.set_table_val(self.tableVolumes, 1.0, 2, 1)
            self.set_table_val(self.tableVolumes, vH / vO, 2, 3)
            self.set_table_val(self.tableVolumes, vHeTotal / vO, 2, 5)
            self.set_table_val(self.tableVolumes, vO / vH * 2.0, 3, 1)
            self.set_table_val(self.tableVolumes, 2.0, 3, 3)
            self.set_table_val(self.tableVolumes, vHeTotal / vH * 2.0, 3, 5)
            # print('PP ' + str(chVol) + ' pAmb:' + str(pAmb))
        else:
            val = 0
            lastLineId = 0
            print('No Report')
        # print(queryReport.lastQuery() + str(val))
        """

    def update_queryReports(self, s=None):
        # print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        # print(s)
        queryReports = QSqlQuery(db=db)
        queryReports.prepare(
            "SELECT shot_number, esther_reports.manager_id, "
            "esther_managers.manager_name, start_time, end_time "
            "FROM esther_reports "
            "INNER JOIN esther_managers ON esther_reports.manager_id = esther_managers.manager_id "
            #"WHERE =shot_number :list_id AND DayPlan = :plan_id "
            "WHERE shot_number  > 160 "
            #"WHERE shot_number  = :shot_no "
            #"ORDER BY LineOrder ASC"
        )
        #query = QSqlQuery("SELECT * FROM 'ChecklistLines' ORDER BY 'ChecklistLines'.'LineOrder' ASC", db=db)
        #query = QSqlQuery("SELECT * FROM ChecklistLines", db=db)

        queryReports.bindValue(":shot_no", self.shotNo)
        queryReports.exec()
        #print(queryReports.lastQuery()) #  + "; Line Before: " + str(lineBefore))
        model = QSqlQueryModel()
        model.setQuery(queryReports)
        self.tableReports.setModel(model)
        self.tableReports.setColumnWidth(0,60)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# vim: syntax=python ts=4 sw=4 sts=4 sr et
