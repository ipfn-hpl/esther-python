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
    QDialog,
    QDialogButtonBox,
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

class SignDialog(QDialog):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)

        self.setWindowTitle("Sign Line!")

        buttons = (
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Sure youwant to sign this Checkline?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.listId = 0
        self.planId = 1
        self.lastSigned = 0
        self.nextLineId  = 0
        self.tableCL = QTableView()
        self.tableLastCL = QTableView()
        self.tableWaitOK = QTableView()
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
        widget.setCurrentIndex(self.planId)
        layoutTools.addWidget(widget)

        layoutTools.addWidget(QLabel('Checklist:'))
        listComb = QComboBox()
        listComb.addItems(["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"])
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

        layoutMain.addLayout(layoutTools)
        layoutMain.addWidget(self.tableCL)
        layoutMain.addWidget(self.tableLastCL)
        
        #self.table = QTableView()
        #query = QSqlQuery("SELECT DayPlan, EstherChecklists.ChecklistName FROM ChecklistLines INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId", db=db)
        #self.model.removeColumns(0,1)
        #self.model.select()
        #self.queryLastCL.exec()

# Third Panel

        layoutTools = QHBoxLayout()
        checkButt = QPushButton("Check this Line")
        checkButt.clicked.connect(self.checkButt_clicked)
        layoutTools.addWidget(checkButt)
        layoutMain.addLayout(layoutTools)

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
        self.update_queryWaitOK()

    def list_changed(self, i):
        print('list is ' + str(i))
        self.listId = i
        self.update_queryCL()
        self.update_queryWaitOK()

    def shot_changed(self, i):
        print('shot is ' + str(i))
        self.shotNo = i
        self.update_queryLastCL()
        self.update_queryWaitOK()

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
            "SELECT ChecklistId, ChecklistName, EstherRoles.RoleName, "
            "LineOrder, LineStatus, LineDesc FROM ChecklistLines "
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
        modelCL = QSqlQueryModel()
        modelCL.setQuery(queryCL)
        self.tableCL.setModel(modelCL)
        self.tableCL.setColumnWidth(0,60)
        self.tableCL.setColumnWidth(1,160)
        self.tableCL.setColumnWidth(2,100)
        self.tableCL.setColumnWidth(3,100)
        self.tableCL.setColumnWidth(4,100)
        self.tableCL.setColumnWidth(5,300)

    def update_queryLastCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        queryLastCL = QSqlQuery(db=db)
        queryLastCL.prepare(
            "SELECT CheckLine, ChecklistLines.LineOrder, LineStatusDate, ChecklistLines.LineDesc, CheckLinesOk.SignedBy, EstherRoles.RoleName "
            "FROM CheckLinesOk "
            "INNER JOIN ChecklistLines ON CheckLinesOk.CheckLine = ChecklistLines.CheckLineId "
            "INNER JOIN EstherRoles ON ChecklistLines.SignedBy = EstherRoles.RoleId "
            "WHERE CheckLinesOk.ShotNumber = :shot_no AND CheckLinesOk.SignedBy = :sign_by AND ChecklistLines.Checklist = :list_id "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineStatusDate DESC LIMIT 4"
        )
        queryLastCL.bindValue(":shot_no", self.shotNo)
        queryLastCL.bindValue(":sign_by", self.signBy)
        queryLastCL.bindValue(":list_id", self.listId)
        queryLastCL.exec()
        #print("Last CL executedQuery : " + queryLastCL.executedQuery() + " signBy: " + str(self.signBy))
        modelLastCL = QSqlQueryModel()
        modelLastCL.setQuery(queryLastCL)
        self.tableLastCL.setModel(modelLastCL)
        self.tableLastCL.setColumnWidth(3,300)

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
            "WHERE LineOrder > :l_order AND Checklist = :list_id "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC LIMIT 3"
        )
        #queryWaitOK.bindValue(":l_order", lastOK)

        queryWaitOK.bindValue(":l_order", self.lastSigned)
        queryWaitOK.bindValue(":list_id", self.listId)
        queryWaitOK.exec()
        if queryWaitOK.first():
            self.nextLineId  = queryWaitOK.value(0)
        else:
            self.nextLineId  = 0
        print("Wait: " + queryWaitOK.lastQuery() + ", next Id: " + str(self.nextLineId))
        modelWaitOK = QSqlQueryModel()
        modelWaitOK.setQuery(queryWaitOK)
        self.tableWaitOK.setModel(modelWaitOK)
        self.tableWaitOK.setColumnWidth(0,160)
        self.tableWaitOK.setColumnWidth(1,160)
        self.tableWaitOK.setColumnWidth(2,300)

    def checkButt_clicked(self, s):
        print("click ", s)
        qryCheckPrecedence = QSqlQuery(db=db)
        qryCheckPrecedence.prepare(
            "SELECT Line, PrecededBy "
            "FROM CheckPrecedence "
            "INNER JOIN ChecklistLines ON Line = ChecklistLines.CheckLineId "
            "WHERE Line = :list_id "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY Line ASC"
        )
        qryCheckPrecedence.bindValue(":list_id", self.nextLineId)
        qryCheckPrecedence.exec()
        print("Last qryCheckPrecedence: " + qryCheckPrecedence.executedQuery() + ' list_id: ' + str(self.nextLineId))
        while qryCheckPrecedence.next():
            lineBefore  = qryCheckPrecedence.value(1)
            print("Line Before: " + str(lineBefore))
            #lastLineId  = qryCheckPrecedence.value(0)

        insertCLine = QSqlQuery(db=db)
        insertCLine.prepare("INSERT INTO CheckLinesOk VALUES (NULL, :shot_no, current_timestamp(), :cLine_id, :sign_by)")
        # self.insertCLine.bindValue(":cLine_id", 6)
        dlg = SignDialog(self)
        if dlg.exec():
            print("Success! " + str(self.lastSigned))
        else:
            print("Cancel!")

        insertCLine.bindValue(":shot_no", self.shotNo)
        insertCLine.bindValue(":cLine_id", self.nextLineId)
        insertCLine.bindValue(":sign_by", self.signBy)
        #insertCLine.bindValue(":sign_by", self.shotNo)
        # if insertCLine.exec():
            # print("Inserted record")
            # self.update_queryLastCL()
            # #self.update_queryWaitOK()
        # else:
            # print("NOT Inserted")

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
