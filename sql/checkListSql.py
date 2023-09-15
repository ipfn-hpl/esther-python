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
        self.shot = QLineEdit()
        self.shot.setPlaceholderText("177")
#        self.list = QLineEdit()
#        self.list.setPlaceholderText("1")
#        self.list.textChanged.connect(self.update_query)
        
        widget = QComboBox()
        widget.addItems(["StartOfDay", "Shot", "EndOfDay"])
        widget.currentIndexChanged.connect(self.plan_changed)
        self.planId = 0
        
        layoutTools.addWidget(refreshButt)
        layoutTools.addWidget(QLabel('Exp. Phase'))
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

        layoutTools.addWidget(widget)
        layoutTools.addWidget(QLabel('Filter Checklist:'))
        layoutTools.addWidget(self.shot)
#        layoutTools.addWidget(self.list)

        radiobutton = QRadioButton('ChiefEngineer', self)
        radiobutton.setChecked(True)
        #radiobutton.sign = "0"
        radiobutton.sign = 0
        self.signBy = 0
        radiobutton.toggled.connect(self.update_signBy)
        layoutTools.addWidget(radiobutton)

        radiobutton = QRadioButton('Researcher', self)
        #radiobutton.sign = "Researcher"
        radiobutton.sign = 1
        radiobutton.toggled.connect(self.update_signBy)
        layoutTools.addWidget(radiobutton)

        self.tableCL = QTableView()
        self.tableLastCL = QTableView()
        self.tableWaitOK = QTableView()
        layoutMain.addLayout(layoutTools)
        layoutMain.addWidget(self.tableCL)
        layoutMain.addWidget(self.tableLastCL)
        layoutMain.addWidget(self.tableWaitOK)
        container.setLayout(layoutMain)
        
        #self.table = QTableView()
        self.modelCL = QSqlQueryModel()
        self.tableCL.setModel(self.modelCL)
        #query = QSqlQuery("SELECT DayPlan, EstherChecklists.ChecklistName FROM ChecklistLines INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId", db=db)
        self.queryCL = QSqlQuery(db=db)
        self.queryCL.prepare(
            "SELECT DayPlans.DayPlanName, EstherChecklists.ChecklistName, EstherRoles.RoleName, LineStatus FROM ChecklistLines "
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
        #self.query.bindValue(":ce_checked", '1')
        #self.query.bindValue(":re_checked", '0')
        self.modelCL.setQuery(self.queryCL)

        #self.model.removeColumns(0,1)
        #self.model.select()
        self.modelLastCL = QSqlQueryModel()
        self.tableLastCL.setModel(self.modelLastCL)
        self.queryLastCL = QSqlQuery(db=db)
        self.queryLastCL.prepare(
            "SELECT ChecklistLines.LineOrder, LineStatusDate, CheckLine, ChecklistLines.LineDesc, EstherRoles.RoleName "
            "FROM CheckLinesOk "
            "INNER JOIN ChecklistLines ON CheckLinesOk.CheckLine = ChecklistLines.CheckLineId "
            "INNER JOIN EstherRoles ON ChecklistLines.SignedBy = EstherRoles.RoleId "
            "WHERE CheckLinesOk.ShotNumber = :shot_no "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineStatusDate ASC LIMIT 5"
        )
        self.queryLastCL.bindValue(":shot_no", 177)
        self.queryLastCL.exec()
        lastOK  = 0
        while self.queryLastCL.next():
            lastOK  = self.queryLastCL.value(0)
        self.modelLastCL.setQuery(self.queryLastCL)
        print(self.queryLastCL.lastQuery())
        self.update_query()
        print("lastOrder: " + str(lastOK))

        self.modelWaitOK = QSqlQueryModel()
        self.tableWaitOK.setModel(self.modelWaitOK)
        self.queryWaitOK = QSqlQuery(db=db)
        self.queryWaitOK.prepare(
            #"SELECT * FROM ChecklistLines "
            "SELECT CheckLineId, LineOrder, LineDesc "
            "FROM ChecklistLines "
            "WHERE LineOrder > :l_order "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC LIMIT 3"
            #"ORDER BY LineStatusDate DESC LIMIT 5"
        )
        self.queryWaitOK.bindValue(":l_order", lastOK)
        self.queryWaitOK.exec()
        self.modelWaitOK.setQuery(self.queryWaitOK) 
        print(self.queryWaitOK.lastQuery())

        self.update_queryCL()
        shotSpin.valueChanged.connect(self.shot_changed)
        listComb.currentIndexChanged.connect(self.list_changed)
        self.setMinimumSize(QSize(1424, 800))
        self.setCentralWidget(container)
        
    def plan_changed(self, i):
        print('plan is ' + str(i))
        self.planId = i
        self.update_query()

    def list_changed(self, i):
        print('list is ' + str(i))
        self.listId = i
        self.update_queryCL()

    def shot_changed(self, i):
        print('shot is ' + str(i))
        self.shotNo = i
        self.update_queryCL()

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
        self.tableCL.setColumnWidth(1,360)
        self.tableCL.setColumnWidth(2,2000)

    def update_query(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        #self.queryCL.bindValue(":list_id", self.listId)
        #self.queryCL.bindValue(":plan_id", self.planId)
        #self.queryCL.exec()
        #self.model.setQuery(self.queryCL)
#        self.table.setColumnWidth(0,160)

        self.queryLastCL.bindValue(":shot_no", self.shotNo)
        self.queryLastCL.exec()


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
