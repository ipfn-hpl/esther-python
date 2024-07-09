#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyQt6 SQL App for signing Esther Checklists
author:  B. Carvalho
email: bernardo.carvalho@tecnico.
"""

import sys

# from reportlab.pdfgen import canvas

from PyQt6.QtCore import QSize, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QFont
from PyQt6.QtSql import (
    QSqlDatabase,
    # QSqlRelation,
    # QSqlRelationalDelegate,
    # QSqlRelationalTableModel,
    # QSqlTableModel,
    QSqlQuery,
    QSqlQueryModel,
)
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    # QLineEdit,
    QMainWindow,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QDialogButtonBox,
    # QCheckBox,
    QComboBox,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QRadioButton,
    QTabWidget,
    QLabel,
)
# Local module with DB configuration
import config

from makeReportSql import report_pdf

CHECK_LIST_QUERY = (
        "SELECT item.id, subsystem.name, "
        "role.name AS Resp, "
        "item.seq_order, item.name AS Action FROM item "
        "INNER JOIN day_phase ON day_phase_id = day_phase.id "
        "INNER JOIN subsystem ON item.subsystem_id = subsystem.id "
        "INNER JOIN role ON role_id = role.id "
        "WHERE subsystem_id = :list_id AND day_phase_id = :plan_id "
        "ORDER BY seq_order ASC"
        )

CHECKLINE_LAST_QUERY = (
        "SELECT item_id, item.seq_order, "
        "time_date, item.name, "
        "role.short_name AS Resp, complete_status.status "
        "FROM complete "
        "INNER JOIN item ON item_id = item.id "
        "INNER JOIN role ON item.role_id = role.id "
        "INNER JOIN complete_status ON "
        "complete_status_id = complete_status.id "
        "WHERE complete.shot = :shot_no AND "
        # "CheckLineSigned.SignedBy = :sign_by AND "
        "item.subsystem_id = :list_id "
        "ORDER BY time_date DESC LIMIT 5"
        )

CHECK_WAITING_LIST_QUERY = (
        "SELECT item.id, seq_order, item.name AS Action, "
        "subsystem.name AS System, "
        "day_phase.name AS Phase, "
        "role.short_name AS Resp "
        "FROM item "
        "INNER JOIN subsystem ON subsystem_id = subsystem.id "
        "INNER JOIN day_phase ON day_phase_id = day_phase.id "
        "INNER JOIN role ON role_id = role.id "
        "WHERE seq_order > :l_order AND day_phase_id = :d_plan AND "
        "role_id = :sign_by AND subsystem_id = :list_id "
        "ORDER BY seq_order ASC LIMIT 4"
        )
# "Checklist = :list_id AND CheckBy = :sign_by "
LAST_SIGNED_QRY = (
        "SELECT item_id, item.seq_order "
        "FROM complete "
        "INNER JOIN item ON complete.item_id = item.id "
        "WHERE complete.shot = :shot_no AND "
        "item.role_id= :sign_by AND "
        "item.subsystem_id = :list_id "
        "ORDER BY time_date DESC LIMIT 1"
        )

PRECENDENCE_QRY = (
            "SELECT item_id, after_item_id "
            "FROM precedence "
            "INNER JOIN item ON item_id = item.id "
            "WHERE item_id = :line_id "
            "ORDER BY item_id ASC"
        )

db = QSqlDatabase("QMARIADB")
db.setHostName(config.host)
db.setDatabaseName(config.database)
db.setUserName(config.username)
db.setPassword(config.password)

db.open()

# General Query for quick selects
queryGlobal = QSqlQuery(db=db)

FONT_NORMAL = QFont("Arial", 12)


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

        # self.rBv = QRadioButton('No Problem', self)
        self.rBa = QRadioButton('Attention required', self)
        self.rBa.setChecked(True)
        self.rBu = QRadioButton('Urgent Repair', self)
        self.layout = QVBoxLayout()
        message = QLabel("Sure you want to sign this Checkline?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.rBa)
        self.layout.addWidget(self.rBu)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.listId = 0
        self.planId = 1
        self.shotNo = 180
        self.signBy = 0
        self.lastSigned = 0
        self.nextLineId = -1
        if queryGlobal.exec(
                "SELECT shot FROM complete "
                "ORDER BY shot DESC LIMIT 1"):
            if queryGlobal.first():
                self.shotNo = queryGlobal.value(0)
        list_names = []
        if queryGlobal.exec(
                "SELECT name FROM subsystem "
                "ORDER BY id ASC"):
            while queryGlobal.next():
                list_names.append(queryGlobal.value(0))
            print(list_names)
        self.tableCL = QTableView()
        qryModel = QSqlQueryModel()
        self.tableCL.setModel(qryModel)

        self.tableLastCL = QTableView()

        self.missingSignTable = QTableView()
        model = QSqlQueryModel()
        self.missingSignTable.setModel(model)

        query = QSqlQuery(db=db)
        query.prepare(CHECK_WAITING_LIST_QUERY)
        model = QSqlQueryModel()
        model.setQuery(query)
        self.tableWaitSign = QTableView()
        self.tableWaitSign.setModel(model)

        container = QWidget()

        layoutTables = QVBoxLayout()
        label = QLabel('CheckLists')
        label.setFont(FONT_NORMAL)
        layoutTables.addWidget(label)
        self.tabs = QTabWidget()
        query = QSqlQuery(db=db)
        for n, lst in enumerate(list_names):
            query.prepare(CHECK_LIST_QUERY)
            query.bindValue(":list_id", n)
            query.bindValue(":plan_id", self.planId)
            query.exec()
            qryModel = QSqlQueryModel()
            qryModel.setQuery(query)
            tableVw = QTableView()
            tableVw.setModel(qryModel)
            self.tabs.addTab(tableVw, lst)
#            self.tabs.addTab(self.tableCL, lst)
        self.tabs.currentChanged.connect(self.list_changed)
        layoutTables.addWidget(self.tabs, stretch=3)

        label = QLabel('Checked Lines on this Shot')
        label.setFont(FONT_NORMAL)
        layoutTables.addWidget(label)

        layoutTables.addWidget(self.tableLastCL, stretch=2)

        label = QLabel('Missing Signatures')
        label.setFont(FONT_NORMAL)
        layoutTables.addWidget(label)
        layoutTables.addWidget(self.missingSignTable, stretch=1)

        label = QLabel('Next Lines to Check')
        label.setFont(FONT_NORMAL)
        layoutTables.addWidget(label)
        layoutTables.addWidget(self.tableWaitSign, stretch=2)

        layoutTools = QVBoxLayout()

        refreshButt = QPushButton("Refresh")
        pdfButt = QPushButton("Report PDF")
        pdfButt.clicked.connect(self.make_report_pdf)
#        refreshButt.clicked.connect(self.refresh_model)

#        layoutTools.addWidget(add_rec)
#        self.list = QLineEdit()
#        self.list.setPlaceholderText("1")
#        self.list.textChanged.connect(self.update_query)
        layoutTools.addWidget(refreshButt)
        layoutTools.addWidget(pdfButt)
        layoutTools.addWidget(QLabel('Exp. Phase'))
        widget = QComboBox()
        widget.addItems(["StartOfDay", "Shot", "EndOfDay"])
        widget.currentIndexChanged.connect(self.plan_changed)
        widget.setCurrentIndex(self.planId)
        layoutTools.addWidget(widget)

        layoutTools.addWidget(QLabel('Shot'))
        shotSpin = QSpinBox()
        shotSpin.setMinimum(170)
        shotSpin.setMaximum(1000)  # May need to change (hopefully)
# Or: widget.setRange(-10,3)
    # widget.setPrefix("$")
# widget.setSuffix("c")
        shotSpin.setSingleStep(1)  # Or e.g. 0.5 for QDoubleSpinBox
        shotSpin.setValue(self.shotNo)
        layoutTools.addWidget(shotSpin)

#        layoutTools.addWidget(QLabel('Filter Checklist:'))
#        layoutTools.addWidget(self.list)

        layoutTools.addStretch()
        # .addSpacing(20)
        layoutTools.addWidget(QLabel('Checked By: '))
        radiobutton = QRadioButton('ChiefEngineer', self)
        radiobutton.setChecked(True)
        radiobutton.sign = 0
        radiobutton.toggled.connect(self.update_signBy)
        layoutTools.addWidget(radiobutton)

        radiobutton = QRadioButton('Researcher', self)
        radiobutton.sign = 1
        radiobutton.toggled.connect(self.update_signBy)
        layoutTools.addWidget(radiobutton)
        checkButtOK = QPushButton("Check Line OK")
        checkButtOK.clicked.connect(self.checkLineButtOK_clicked)
        layoutTools.addWidget(checkButtOK)
        checkButt = QPushButton("Check Next Line NOK")
        checkButt.clicked.connect(self.checkLineButt_clicked)
        layoutTools.addWidget(checkButt)

        layoutMain = QHBoxLayout()

        layoutMain.addLayout(layoutTools)

        layoutMain.addLayout(layoutTables)
        container.setLayout(layoutMain)

#        self.update_queryCL()
        self.update_queryLastCL()
        self.update_ChkLists()
        self.updateMissingSignTable([10, 20])
        shotSpin.valueChanged.connect(self.shot_changed)
        # listComb.currentIndexChanged.connect(self.list_changed)
        self.setMinimumSize(QSize(1200, 700))
        self.setCentralWidget(container)

    def plan_changed(self, pId):
        self.planId = pId
        # self.update_queryCL()
        self.update_ChkLists(pId)
        self.update_queryLastCL()

    def list_changed(self, lid):
        # print('list is ' + str(l))
        self.listId = lid
        # self.update_queryCL()
        # self.update_ChkLists()
        self.update_queryLastCL()

    def shot_changed(self, s):
        # print('Shot is ' + str(s))
        self.shotNo = s
        self.update_queryLastCL()

    def update_signBy(self):
        # get the radio button the send the signal
        rb = self.sender()
        # check if the radio button is checkedDayPlanId
        if rb.isChecked():
            print("signBy is %s" % (rb.sign))
            self.signBy = rb.sign
            # self.update_ChkLists()
            self.update_queryLastCL()

    def updateMissingSignTable(self, missingList):
        model = self.missingSignTable.model()
        query = QSqlQuery(db=db)
        sqlStr = (
                "SELECT item.id, seq_order, item.name, "
                "subsystem.name AS System, day_phase.short_name AS Phase, "
                "role.short_name AS Resp "
                "FROM item "
                "INNER JOIN subsystem ON subsystem_id = subsystem.id "
                "INNER JOIN day_phase ON day_phase_id = day_phase.id "
                "INNER JOIN role ON role_id = role.id "
                "WHERE item.id IN ("
                )
        Ids = ','.join(map(str, missingList))
        sqlStr = sqlStr + Ids + ")"
        # query.exec(sqlStr)
        if (not query.exec(sqlStr)):
            print(f"{query.executedQuery()}")

        model.setQuery(query)

    def update_ChkLists(self, planId=1):
        # print('count is ' + str(self.tabs.count()))
        for i in range(self.tabs.count()):
            tabw = self.tabs.widget(i)
            model = tabw.model()
            query = model.query()
            query.bindValue(":plan_id", planId)
            query.bindValue(":list_id", i)
            if (not query.exec()):
                print(f"NOT exec(). CL Query i: {i}", end='')
                print(f"{query.executedQuery()} signBy: {self.signBy}")
            # return
            model.setQuery(query)
            tabw.setAlternatingRowColors(True)
            tabw.setColumnWidth(0, 80)
            tabw.setColumnWidth(3, 100)
            tabw.setColumnWidth(4, 500)

    def update_queryLastCL(self, s=None):
        # print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        # print(s)
        model = QSqlQueryModel()
        query = QSqlQuery(db=db)
        query.prepare(CHECKLINE_LAST_QUERY)
        # self.tableLastCL.setModel(qryModel)
        query.bindValue(":shot_no", self.shotNo)
        # query.bindValue(":sign_by", self.signBy)
        query.bindValue(":list_id", self.listId)
        # if (not queryLastCL.exec()):
        if (not query.exec()):
            # print(f"NOT exec(). CL Query i: {i}", end='')
            print(f"NOT exec: {query.executedQuery()}")
            # print(f"{query.executedQuery()} signBy: {self.signBy}")
            # print("Last CL Query: " + query.executedQuery() + " signBy: " + str(self.signBy))
            return
        # print(":shot_no", str(self.shotNo)  + " signBy: " + str(self.signBy))
        # QSqlQueryModel::setQuery() is a member of the model, QSqlQueryModel::query().exec() 
        # is just a method on the query. So the model knows about the former and refreshes, 
        # but does not know you're doing the latter.
        model.setQuery(query)
# https://forum.qt.io/topic/13658/qsqltablemodel-qtableview-how-to-sort-by-column/2

        proxyModel = QSortFilterProxyModel(model)
        proxyModel.setSourceModel(model)
        self.tableLastCL.setModel(proxyModel)
        self.tableLastCL.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.tableLastCL.setSortingEnabled(True)
        # self.tableLastCL.reset()
        # self.tableLastCL.show()
        self.tableLastCL.setColumnWidth(3, 400)
        # self.tableLastCL.resizeColumnsToContents()
        self.tableLastCL.setAlternatingRowColors(True)

        query = QSqlQuery(db=db)
        query.prepare(LAST_SIGNED_QRY)
        query.bindValue(":shot_no", self.shotNo)
        query.bindValue(":sign_by", self.signBy)
        query.bindValue(":list_id", self.listId)
        if (query.exec()):
            if query.first():
                self.lastSigned = query.value(1)
            else:
                self.lastSigned = 0
            print(f"lastOrder: {self.lastSigned}")
        else:
            print(f"Last signed NOT exec: {query.executedQuery()}")
        #    lastOK  = 0
        #    lastLineId  = 0
        # print(self.queryLastCL.lastQuery())
        # self.update_queryLastCL()
        # self.lastSignedId = lastLineId
        self.update_queryWaitList()

    def update_queryWaitList(self):
        # print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        model = self.tableWaitSign.model()
        query = model.query()
        # queryWaitOK = QSqlQuery(db=db)
        query.bindValue(":l_order", self.lastSigned)
        query.bindValue(":list_id", self.listId)
        query.bindValue(":sign_by", self.signBy)
        query.bindValue(":d_plan", self.planId)
        missLines = []
        if query.exec():
            if query.first():
                missLines = self.getMissingLines(query.value(0))
                if not missLines:
                    print("No missing Lines")
                    self.nextLineId = query.value(0)
                else:
                    print("Missing Lines")
                    print(missLines)
                    self.nextLineId = -1
                self.updateMissingSignTable(missLines)
            else:
                self.nextLineId = 0
                print("Not exec() missing Lines")
            model.setQuery(query)
            self.tableWaitSign.setColumnWidth(0, 100)
            self.tableWaitSign.setColumnWidth(1, 100)
            self.tableWaitSign.setColumnWidth(2, 400)
        else:
            print(f"Wait List NOT exec: {query.executedQuery()}")

    def getMissingLines(self, nextLineId):
        qryCheckPrecedence = QSqlQuery(db=db)
        qryCheckPrecedence.prepare(PRECENDENCE_QRY)
        qryCheckPrecedence.bindValue(":line_id", nextLineId)
        if (not qryCheckPrecedence.exec()):
            print(f"Prececence {qryCheckPrecedence.executedQuery()}")

        qryCheckSigned = QSqlQuery(db=db)
        qryCheckSigned.prepare(
            "SELECT item_id, shot, complete_status_id "
            "FROM complete "
            "WHERE item_id = :line AND shot = :shot_no"
        )
        missingList = []
        while qryCheckPrecedence.next():
            lineBefore = qryCheckPrecedence.value(1)
            qryCheckSigned.bindValue(":line", lineBefore)
            qryCheckSigned.bindValue(":shot_no", self.shotNo)
            qryCheckSigned.exec()
            if not qryCheckSigned.first():
                missingList.append(lineBefore)
                print(f"Line Before not Signed: {lineBefore}")
        return missingList

    def insertCheckedLine(self, value):
        insertCLine = QSqlQuery(db=db)
        insertCLine.prepare(
            "INSERT INTO complete VALUES (NULL, :shot_no, "
            "current_timestamp(), :cLine_id, :sign_val, NULL)")
        insertCLine.bindValue(":shot_no", self.shotNo)
        insertCLine.bindValue(":cLine_id", self.nextLineId)
        insertCLine.bindValue(":sign_val", value)
        if insertCLine.exec():
            print("Inserted record")
            self.update_queryLastCL()
        else:
            QMessageBox.critical(
                    None, "Record NOT Inserted ", "SQL Error")
            print(f"Insert failed: {insertCLine.lastQuery()}")
        # print(f":shot_no + {self.shotNo} :cLine_id {self.nextLineId} :sign_by {self.signBy}")

    def checkLineButtOK_clicked(self):
        if self.nextLineId > 0:
            self.insertCheckedLine(0)
        else:
            print(f"Insert Cancel! {self.nextLineId}")

    def checkLineButt_clicked(self):
        if self.nextLineId > 0:
            dlg = SignDialog(self)
            if dlg.exec():
                if dlg.rBa.isChecked():
                    signVal = 1
                elif dlg.rBu.isChecked():
                    signVal = 2
                else:
                    signVal = 255
                print(f"dlg rBx: {signVal}")
                self.insertCheckedLine(signVal)
        else:
            print(f"Insert Cancel! {self.nextLineId}")

    def make_report_pdf(self):
        report_pdf(db, self.shotNo, self.listId)


#    def update_filter(self, s):
#        filter_str = 'Checklist LIKE "{}"'.format(s)
#        self.model.setFilter(filter_str)

#        self.model.setFilter(filter_str)
    # def refresh_model(self, s):
    #    self.model.select()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# vim: syntax=python ts=4 sw=4 sts=4 sr et
