#!/usr/bin/env python3
"""
PyQt6 SQL App for signed Esther Checklists
"""

#import os
import sys

from PyQt6.QtCore import QSize, Qt
# from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtSql import (
    QSqlDatabase,
    #QSqlRelation,
    #QSqlRelationalDelegate,
    #QSqlRelationalTableModel,
    QSqlTableModel,
    QSqlQuery,
    QSqlQueryModel,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QRadioButton,
    QLabel,
)

#basedir = os.path.dirname(__file__)

# db = QSqlDatabase("QSQLITE")
#db.setDatabaseName(os.path.join(basedir, "chinook.sqlite"))
#db.open()

db = QSqlDatabase("QMARIADB")
db.setHostName("epics.ipfn.tecnico.ulisboa.pt");
#db.setHostName("10.136.240.213");
#db.setHostName("localhost");
db.setDatabaseName("archive");
db.setUserName("archive");
db.setPassword("$archive");

db.open()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        container = QWidget()
        layoutMain = QVBoxLayout()
        layoutTools = QHBoxLayout()

        self.search = QLineEdit()
#        self.search.textChanged.connect(self.update_filter)

        #add_rec = QPushButton("Add record")
        #add_rec.clicked.connect(self.add_row)

        refreshButt = QPushButton("Refresh")
#        refreshButt.clicked.connect(self.refresh_model)

#        layoutTools.addWidget(add_rec)
#        self.list = QLineEdit()
#        self.list.setPlaceholderText("1")
#        self.list.textChanged.connect(self.update_query)
        
        layoutTools.addWidget(refreshButt)
        layoutTools.addWidget(QLabel('Exp. Phase'))
        widget = QComboBox()
        widget.addItems(["StartOfDay", "Shot", "EndOfDay"])
        widget.currentIndexChanged.connect(self.plan_changed)
        self.planId = 0
        
        layoutTools.addWidget(widget)

        layoutTools.addWidget(QLabel('Checklist:'))
        listComb = QComboBox()
        listComb.addItems(["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"])
        self.listId = 0
        layoutTools.addWidget(listComb)

        layoutTools.addWidget(QLabel('Shot'))
        shotSpin = QSpinBox()
        shotSpin.setMinimum(170)
        shotSpin.setMaximum(1000) # May need to change (hopefully)
# Or: widget.setRange(-10,3)
    #widget.setPrefix("$")
#widget.setSuffix("c")
        shotSpin.setSingleStep(1) # Or e.g. 0.5 for QDoubleSpinBox
        self.shotNo = 177
        shotSpin.setValue(self.shotNo)
        layoutTools.addWidget(shotSpin)

#        layoutTools.addWidget(QLabel('Filter Checklist:'))
#        layoutTools.addWidget(self.list)

        layoutTools.addWidget(QLabel('Checked By: '))
        radiobutton = QRadioButton('ChiefEngineer', self)
        radiobutton.setChecked(True)
        radiobutton.sign = 0
        self.signBy = 0
        radiobutton.toggled.connect(self.update_signBy)
        layoutTools.addWidget(radiobutton)

        radiobutton = QRadioButton('Researcher', self)
        radiobutton.sign = 1
        radiobutton.toggled.connect(self.update_signBy)
        layoutTools.addWidget(radiobutton)

        self.tableCL = QTableView()
        self.tableLastCL = QTableView()
        self.tableWaitOK = QTableView()
        layoutMain.addLayout(layoutTools)
        layoutMain.addWidget(self.tableCL)
        layoutMain.addWidget(self.tableLastCL)
        
        #self.table = QTableView()
        self.modelCL = QSqlQueryModel()
        self.tableCL.setModel(self.modelCL)
        #query = QSqlQuery("SELECT DayPlan, EstherChecklists.ChecklistName FROM ChecklistLines INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId", db=db)
        self.queryCL = QSqlQuery(db=db)
        self.queryCL.prepare(
            "SELECT DayPlans.DayPlanName, EstherChecklists.ChecklistName, EstherRoles.RoleName, "
            "LineOrder, LineStatus, LineDesc FROM ChecklistLines "
            "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
            "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
            "INNER JOIN EstherRoles ON SignedBy = EstherRoles.RoleId "
            "WHERE Checklist = :list_id AND DayPlan = :plan_id "
            "ORDER BY LineOrder ASC"
        )
        #query = QSqlQuery("SELECT * FROM 'ChecklistLines' ORDER BY 'ChecklistLines'.'LineOrder' ASC", db=db)
        #query = QSqlQuery("SELECT * FROM ChecklistLines", db=db)

        #self.table.setModel(self.model)
        self.queryCL.bindValue(":list_id", 0)
        self.queryCL.bindValue(":plan_id", self.planId)

        #self.model.removeColumns(0,1)
        #self.model.select()
        self.modelLastCL = QSqlQueryModel()
        self.tableLastCL.setModel(self.modelLastCL)
        self.queryLastCL = QSqlQuery(db=db)
        self.queryLastCL.prepare(
            "SELECT CheckLine, ChecklistLines.LineOrder, LineStatusDate, ChecklistLines.LineDesc, EstherRoles.RoleName "
            "FROM CheckLinesOk "
            "INNER JOIN ChecklistLines ON CheckLinesOk.CheckLine = ChecklistLines.CheckLineId "
            "INNER JOIN EstherRoles ON ChecklistLines.SignedBy = EstherRoles.RoleId "
            "WHERE CheckLinesOk.ShotNumber = :shot_no "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineStatusDate ASC LIMIT 5"
        )
        self.queryLastCL.bindValue(":shot_no", 177)
        #self.queryLastCL.exec()

# Third Panel

        self.insertCLine = QSqlQuery(db=db)
        self.insertCLine.prepare(
                "INSERT INTO CheckLinesOk VALUES (NULL, :shot_no , current_timestamp(), :cLine_id, :sign_by)"
        )
        layoutTools = QHBoxLayout()
        checkButt = QPushButton("Check this Line")
        checkButt.clicked.connect(self.checkButt_click)
        layoutTools.addWidget(checkButt)
        layoutMain.addLayout(layoutTools)

        self.modelWaitOK = QSqlQueryModel()
        self.tableWaitOK.setModel(self.modelWaitOK)
        self.queryWaitOK = QSqlQuery(db=db)
        self.queryWaitOK.prepare(
            "SELECT CheckLineId, LineOrder, LineDesc "
            "FROM ChecklistLines "
            "WHERE LineOrder > :l_order "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC LIMIT 3"
            #"ORDER BY LineStatusDate DESC LIMIT 5"
        )
        lastOK  = 0
        self.lastSigned = lastOK
        self.queryWaitOK.bindValue(":l_order", lastOK)
        self.queryWaitOK.exec()
        self.modelWaitOK.setQuery(self.queryWaitOK) 
        print(self.queryWaitOK.lastQuery())

        layoutMain.addWidget(self.tableWaitOK)
        container.setLayout(layoutMain)

        self.update_queryCL()
        self.update_queryLastCL()
        self.update_queryWaitOK()
        shotSpin.valueChanged.connect(self.shot_changed)
        listComb.currentIndexChanged.connect(self.list_changed)
        self.setMinimumSize(QSize(1424, 800))
        self.setCentralWidget(container)
        
    def plan_changed(self, i):
#        print('plan is ' + str(i))
        self.planId = i
        self.update_queryCL()

    def list_changed(self, i):
        print('list is ' + str(i))
        self.listId = i
        self.update_queryCL()

    def shot_changed(self, i):
        print('shot is ' + str(i))
        self.shotNo = i
        self.update_queryLastCL()

    def update_signBy(self):
        # get the radio button the send the signal
        rb = self.sender()
        # check if the radio button is checked
        if rb.isChecked():
            print("sign is %s" % (rb.sign))
            self.signBy = rb.sign
            #self.result_label.setText(f'You selected {rb.text()}')

    def update_queryCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        self.queryCL.bindValue(":list_id", self.listId)
        self.queryCL.bindValue(":plan_id", self.planId)
        self.queryCL.exec()
        self.modelCL.setQuery(self.queryCL)
        self.tableCL.setColumnWidth(0,160)
        self.tableCL.setColumnWidth(1,160)
        self.tableCL.setColumnWidth(2,300)

    def update_queryLastCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        self.queryLastCL.bindValue(":shot_no", self.shotNo)
        self.queryLastCL.exec()
        self.modelLastCL.setQuery(self.queryLastCL)
        self.tableLastCL.setColumnWidth(3,260)

        #while self.queryLastCL.next():
        #    lastOK  = self.queryLastCL.value(0)
        if self.queryLastCL.last():
            lastLineId  = self.queryLastCL.value(0)
            lastOK      = self.queryLastCL.value(1)
        else:
            lastOK  = 0
            lastLineId  = 0
        #print(self.queryLastCL.lastQuery())
        #self.update_queryLastCL()
        self.lastSigned = lastOK
        self.lastSignedId = lastLineId
        print("lastOrder: " + str(lastOK)+ ", lastLineId: " + str(lastLineId))

    def update_queryWaitOK(self):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        self.queryWaitOK.bindValue(":l_order", self.lastSigned)
        self.queryWaitOK.exec()
        self.modelWaitOK.setQuery(self.queryWaitOK)
        self.tableWaitOK.setColumnWidth(0,160)
        self.tableWaitOK.setColumnWidth(1,160)
        self.tableWaitOK.setColumnWidth(2,300)

    def checkButt_click(self):
        self.insertCLine.bindValue(":shot_no", self.shotNo)
        self.insertCLine.bindValue(":cLine_id", 6)
        self.insertCLine.bindValue(":sign_by", self.signBy)
        #self.insertCLine.bindValue(":sign_by", self.shotNo)
        if self.insertCLine.exec():
            print("Inserted record")
            self.update_queryLastCL()
            #self.update_queryWaitOK()
        else:
            print("NOT Inserted")

#    def update_filter(self, s):
#        filter_str = 'Checklist LIKE "{}"'.format(s)
#        self.model.setFilter(filter_str)

#        self.model.setFilter(filter_str)
    #def refresh_model(self, s):
    #    self.model.select()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# vim: syntax=python ts=4 sw=4 sts=4 sr et
