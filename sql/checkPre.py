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
    #QSqlTableModel,
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
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QCheckBox,
    QComboBox,
#    QSpinBox,
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

class SignDialog(QDialog):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)

        #print("Pare: " + str(parent.shotNo))
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
        
        self.listId = 0
        self.lineId = 11
        self.planId = 1
        self.signBy = 0
        self.shotNo = 180
        self.lastSigned = 0
        self.nextLineId  = 0
        self.tableCL = QTableView()
        qryModel = QSqlQueryModel()
        self.tableCL.setModel(qryModel)
        self.tableLastCL = QTableView()
        self.tablePreCLines = QTableView()
        self.tableWaitOK = QTableView()
        container = QWidget()

        layoutMain = QHBoxLayout()
        layoutTools = QVBoxLayout()
        layoutTables = QVBoxLayout()

        self.search = QLineEdit()
        #add_rec = QPushButton("Add record")
        #add_rec.clicked.connect(self.add_row)

        refreshButt = QPushButton("Refresh")
        refreshButt.clicked.connect(self.refresh_checkline)

#        layoutTools.addWidget(add_rec)
#        self.list = QLineEdit()
#        self.list.setPlaceholderText("1")
#        self.list.textChanged.connect(self.update_query)
        
        layoutTools.addWidget(refreshButt)
        layoutTools.addStretch()
        # .addSpacing(20)
        layoutTools.addWidget(QLabel('Exp. Phase'))
        widget = QComboBox()
        widget.addItems(["StartOfDay", "Shot", "EndOfDay"])
        widget.currentIndexChanged.connect(self.plan_changed)
        widget.setCurrentIndex(self.planId)
        layoutTools.addWidget(widget, stretch=2)

        layoutTools.addWidget(QLabel('Checklist:'))
        listComb = QComboBox()
        listComb.addItems(["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"])
        layoutTools.addWidget(listComb)
        # layoutTools.addWidget(listComb, stretch=4)

        layoutTools.addWidget(QLabel('Shot'))
#        layoutTools.addWidget(QLabel('Filter Checklist:'))
#        layoutTools.addWidget(self.list)

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

        layoutMain.addLayout(layoutTools)
        

# Third Panel

        layoutTables.addWidget(self.tableCL)
        #layoutTables.addWidget(self.tableLastCL)
        layoutTables.addWidget(self.tablePreCLines)
        layoutMain.addLayout(layoutTables)

        #layoutMain.addWidget(self.tableWaitOK)
        container.setLayout(layoutMain)

        self.update_queryCL()
        self.update_queryLastCL()
        self.update_queryPre()
        #self.update_queryWaitOK()
        listComb.currentIndexChanged.connect(self.list_changed)
        self.setMinimumSize(QSize(1100, 600))
        self.setCentralWidget(container)

    def refresh_checkline(self, s):
        indexes = self.tableCL.selectionModel().selectedRows()
        model = self.tableCL.model()
        for index in sorted(indexes):
            print('Row %d is selected' % index.row())
            #QSqlRecord
            record = model.record(index.row())
            field = record.field(0)
            self.lineId = int(field.value())
            print('Line is %d is selected' % field.value())

        self.update_queryPre()

    #    self.model.select()
    def plan_changed(self, i):
#        print('plan is ' + str(i))
        self.planId = i
        self.update_queryCL()
        #self.update_queryWaitOK()

    def list_changed(self, i):
        print('list is ' + str(i))
        self.listId = i
        self.update_queryCL()
        #self.update_queryWaitOK()


    def update_signBy(self):
        # get the radio button the send the signal
        rb = self.sender()
        # check if the radio button is checked
        if rb.isChecked():
            print("sign is %s" % (rb.sign))
            self.signBy = rb.sign
            self.update_queryLastCL()
            self.update_queryWaitOK()
            #self.result_label.setText(f'You selected {rb.text()}')

    def update_queryCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        queryCL = QSqlQuery(db=db)
        queryCL.prepare(
            "SELECT CheckLineId, ChecklistName, EstherRoles.RoleName, "
            "LineOrder, LineDesc FROM ChecklistLines "
            "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
            "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
            "INNER JOIN EstherRoles ON SignedBy = EstherRoles.RoleId "
            "WHERE Checklist = :list_id AND DayPlan = :plan_id "
            "ORDER BY LineOrder ASC"
        )
        #query = QSqlQuery("SELECT * FROM 'ChecklistLines' ORDER BY 'ChecklistLines'.'LineOrder' ASC", db=db)
        #query = QSqlQuery("SELECT * FROM ChecklistLines", db=db)

        queryCL.bindValue(":list_id", self.listId)
        queryCL.bindValue(":plan_id", self.planId)
        queryCL.exec()
        print("CL Query: " + queryCL.executedQuery())
        model = self.tableCL.model()
        #modelCL = QSqlQueryModel()
        model.setQuery(queryCL)
        #self.tableCL.setModel(modelCL)
        self.tableCL.setColumnWidth(0,50)
        self.tableCL.setColumnWidth(1,80)
        self.tableCL.setColumnWidth(2,100)
        self.tableCL.setColumnWidth(3,100)
        self.tableCL.setColumnWidth(4,600)

    def update_queryPre(self):
        #print("click ", s)
        qryPrecedence = QSqlQuery(db=db)
        qryPrecedence.prepare(
            "SELECT Line, PrecededBy, ChecklistLines.Checklist, "
            "ChecklistLines.LineOrder, ChecklistLines.LineDesc "
            "FROM CheckPrecedence "
            "INNER JOIN ChecklistLines ON PrecededBy = ChecklistLines.CheckLineId "
            "WHERE Line = :list_id "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY Line ASC"
        )
        qryPrecedence.bindValue(":list_id", self.lineId)
        #qryPrecedence.bindValue(":list_id", self.nextLineId)
        if (not qryPrecedence.exec()):
            print("Last qryCheckPrecedence: " + qryPrecedence.executedQuery() + ' list_id: ' + str(self.nextLineId))
            return
            
        modelPre = QSqlQueryModel()
        modelPre.setQuery(qryPrecedence)
        self.tablePreCLines.setModel(modelPre)
        self.tablePreCLines.setColumnWidth(2,80)
        self.tablePreCLines.setColumnWidth(3,80)
        self.tablePreCLines.setColumnWidth(4,600)

    def update_queryLastCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        queryLastCL = QSqlQuery(db=db)
        queryLastCL.prepare(
            "SELECT CheckLine, ChecklistLines.LineOrder, LineStatusDate, ChecklistLines.LineDesc, CheckLineSigned.SignedBy, EstherRoles.RoleName "
            "FROM CheckLineSigned "
            "INNER JOIN ChecklistLines ON CheckLineSigned.CheckLine = ChecklistLines.CheckLineId "
            "INNER JOIN EstherRoles ON ChecklistLines.SignedBy = EstherRoles.RoleId "
            "WHERE CheckLineSigned.ShotNumber = :shot_no AND CheckLineSigned.SignedBy = :sign_by AND ChecklistLines.Checklist = :list_id "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineStatusDate DESC LIMIT 4"
        )
        #queryLastCL.bindValue(":shot_no", self.shotNo)
        queryLastCL.bindValue(":sign_by", self.signBy)
        queryLastCL.bindValue(":list_id", self.listId)
        queryLastCL.exec()
        #print("Last CL Query: " + queryLastCL.executedQuery() + " signBy: " + str(self.signBy))
        modelLastCL = QSqlQueryModel()
        modelLastCL.setQuery(queryLastCL)
        self.tableLastCL.setModel(modelLastCL)
        self.tableLastCL.setColumnWidth(3,300)
        #self.tableLastCL.sortByColumn(1,Qt.SortOrder.AscendingOrder)
        #self.tableLastCL.setSortingEnabled(True)

        #while self.queryLastCL.next():
        #    lastOK  = self.queryLastCL.value(0)
        if queryLastCL.first():
            lastLineId  = queryLastCL.value(0)
            lastOK      = queryLastCL.value(1)
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
        queryWaitOK = QSqlQuery(db=db)
        queryWaitOK.prepare(
            "SELECT CheckLineId, LineOrder, LineDesc, SignedBy "
            "FROM ChecklistLines "
            "WHERE LineOrder > :l_order AND Checklist = :list_id AND SignedBy = :sign_by "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC LIMIT 3"
        )
        #queryWaitOK.bindValue(":l_order", lastOK)

        queryWaitOK.bindValue(":l_order", self.lastSigned)
        queryWaitOK.bindValue(":list_id", self.listId)
        queryWaitOK.bindValue(":sign_by", self.signBy)
        queryWaitOK.exec()
        if queryWaitOK.first():
            self.nextLineId  = queryWaitOK.value(0)
        else:
            self.nextLineId  = 0
        # print("Wait: " + queryWaitOK.lastQuery() + ", next Id: " + str(self.nextLineId))
        modelWaitOK = QSqlQueryModel()
        modelWaitOK.setQuery(queryWaitOK)
        self.tableWaitOK.setModel(modelWaitOK)
        self.tableWaitOK.setColumnWidth(0,160)
        self.tableWaitOK.setColumnWidth(1,160)
        self.tableWaitOK.setColumnWidth(2,300)


#    def update_filter(self, s):
#        filter_str = 'Checklist LIKE "{}"'.format(s)
#        self.model.setFilter(filter_str)

#        self.model.setFilter(filter_str)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# vim: syntax=python ts=4 sw=4 sts=4 sr et
