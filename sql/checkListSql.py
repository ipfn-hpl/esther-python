#!/usr/bin/env python3
"""
PyQt6 SQL App for signed Esther Checklists
"""

#import os
import sys

from PyQt6.QtCore import QSize, Qt, QSortFilterProxyModel
# from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtGui import QFont
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
    QCheckBox,
    QComboBox,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QRadioButton,
    QTabWidget,
    QLabel,
)

#basedir = os.path.dirname(__file__)

# db = QSqlDatabase("QSQLITE")
#db.setDatabaseName(os.path.join(basedir, "chinook.sqlite"))
#db.open()
CHECK_LIST_QUERY = ("SELECT CheckLineId, ChecklistName, EstherRoles.RoleName, "
            "LineOrder, LineDesc FROM ChecklistLines "
            "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
            "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
            "INNER JOIN EstherRoles ON SignedBy = EstherRoles.RoleId "
            "WHERE Checklist = :list_id AND DayPlan = :plan_id "
            "ORDER BY LineOrder ASC"
        )

CHECKLINE_LAST_QUERY = ("SELECT CheckLine, ChecklistLines.LineOrder, LineStatusDate, ChecklistLines.LineDesc, CheckLineSigned.SignedBy, EstherRoles.RoleName "
            "FROM CheckLineSigned "
            "INNER JOIN ChecklistLines ON CheckLineSigned.CheckLine = ChecklistLines.CheckLineId "
            "INNER JOIN EstherRoles ON ChecklistLines.SignedBy = EstherRoles.RoleId "
            "WHERE CheckLineSigned.ShotNumber = :shot_no AND CheckLineSigned.SignedBy = :sign_by AND ChecklistLines.Checklist = :list_id "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineStatusDate DESC LIMIT 4")

CHECK_WAITING_LIST_QUERY = ("SELECT CheckLineId, LineOrder, LineDesc, SignedBy "
            "FROM ChecklistLines "
            "WHERE LineOrder > :l_order AND Checklist = :list_id AND SignedBy = :sign_by "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC LIMIT 3")

LIST_NAMES = ["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"]
db = QSqlDatabase("QMARIADB")
#db.setHostName("epics.ipfn.tecnico.ulisboa.pt");
db.setHostName("efda-marte.ipfn.tecnico.ulisboa.pt");
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
        self.planId = 1
        self.shotNo = 180
        self.signBy = 0
        self.lastSigned = 0
        self.nextLineId  = 0
        self.tableCL = QTableView()
        qryModel = QSqlQueryModel()
        self.tableCL.setModel(qryModel)

        self.tableLastCL = QTableView()
        """
        query = QSqlQuery(db=db)
        query.prepare(CHECKLINE_LAST_QUERY)
        self.tableLastCL.setModel(qryModel)
        """
        query = QSqlQuery(db=db)
        query.prepare(CHECK_WAITING_LIST_QUERY)
        model = QSqlQueryModel()
        model.setQuery(query)
        self.tableWaitOK = QTableView()
        self.tableWaitOK.setModel(model)

        container = QWidget()

        #query = QSqlQuery("SELECT DayPlan, EstherChecklists.ChecklistName FROM ChecklistLines INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId", db=db)
        #self.model.removeColumns(0,1)
        #self.model.select()
        #self.queryLastCL.exec()

# Third Panel

        layoutTables = QVBoxLayout()
        self.tabs = QTabWidget()
        query = QSqlQuery(db=db)
        for n, lst in enumerate(LIST_NAMES):
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
        #layoutTables.addWidget(self.tableCL)
        self.tabs.currentChanged.connect(self.list_changed)
        layoutTables.addWidget(self.tabs, stretch=3)
        label = QLabel('Checked Lines on this Shot')
        label.setFont(QFont('Arial', 20))
        layoutTables.addWidget(label)

        layoutTables.addWidget(self.tableLastCL)

        label = QLabel('Next Lines')
        label.setFont(QFont('Arial', 20))
        layoutTables.addWidget(label)
        layoutTables.addWidget(self.tableWaitOK)

        layoutTools = QVBoxLayout()

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

        #layoutTools.addWidget(QLabel('Checklist:'))
        #listComb = QComboBox()
        #listComb.addItems(["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"])
#        layoutTools.addWidget(listComb)

        layoutTools.addWidget(QLabel('Shot'))
        shotSpin = QSpinBox()
        shotSpin.setMinimum(170)
        shotSpin.setMaximum(1000) # May need to change (hopefully)
# Or: widget.setRange(-10,3)
    #widget.setPrefix("$")
#widget.setSuffix("c")
        shotSpin.setSingleStep(1) # Or e.g. 0.5 for QDoubleSpinBox
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
        checkButt = QPushButton("Check Next Line")
        checkButt.clicked.connect(self.checkButt_clicked)
        layoutTools.addWidget(checkButt)

        layoutMain = QHBoxLayout()

        layoutMain.addLayout(layoutTools)

        layoutMain.addLayout(layoutTables)
        container.setLayout(layoutMain)

#        self.update_queryCL()
        self.update_queryLastCL()
        self.update_queryWaitOK()
        
        self.update_ChkLists()
        shotSpin.valueChanged.connect(self.shot_changed)
        #listComb.currentIndexChanged.connect(self.list_changed)
        self.setMinimumSize(QSize(1200, 800))
        self.setCentralWidget(container)
        
    def plan_changed(self, i):
#        print('plan is ' + str(i))
        self.planId = i
        #self.update_queryCL()
        self.update_ChkLists()
        self.update_queryLastCL()
        self.update_queryWaitOK()

    def list_changed(self, i):
        print('list is ' + str(i))
        self.listId = i
        #self.update_queryCL()
        self.update_ChkLists()
        self.update_queryLastCL()
        self.update_queryWaitOK()

    def shot_changed(self, i):
        print('Shot is ' + str(i))
        self.shotNo = i
        self.update_queryLastCL()
        self.update_queryWaitOK()

    def update_signBy(self):
        # get the radio button the send the signal
        rb = self.sender()
        # check if the radio button is checked
        if rb.isChecked():
            print("signBy is %s" % (rb.sign))
            self.signBy = rb.sign
            #self.update_ChkLists()
            self.update_queryLastCL()
            self.update_queryWaitOK()
            #self.result_label.setText(f'You selected {rb.text()}')

    def update_ChkLists(self):
        print('count is ' + str(self.tabs.count()))
        for i in range(self.tabs.count()):
            tableVw = self.tabs.widget(i)
            model = tableVw.model()
            query = model.query()
            query.bindValue(":plan_id", self.planId)
            query.bindValue(":list_id", i)
            if (not query.exec()):
                print("NOT exec(). CL Query i: " + str(i) + query.executedQuery() + " signBy: " + str(self.signBy))
            #return
            model.setQuery(query)
            tableVw.setAlternatingRowColors(True)
            tableVw.setColumnWidth(4,300)

    def update_queryLastCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        #model = self.tableLastCL.model()
        #query = model.query()
        model = QSqlQueryModel()
        query = QSqlQuery(db=db)
        query.prepare(CHECKLINE_LAST_QUERY)
        #qryModel.setQuery(query)
        #self.tableLastCL.setModel(qryModel)
        query.bindValue(":shot_no", self.shotNo)
        query.bindValue(":sign_by", self.signBy)
        query.bindValue(":list_id", self.listId)
        #if (not queryLastCL.exec()):
        if (not query.exec()):
            print("Last CL Query: " + query.executedQuery() + " signBy: " + str(self.signBy))
            return
        print("LastCL Query: " + query.executedQuery())
        print(":shot_no", str(self.shotNo)  + " signBy: " + str(self.signBy))
        # QSqlQueryModel::setQuery() is a member of the model, QSqlQueryModel::query().exec() 
        # is just a method on the query. So the model knows about the former and refreshes, 
        # but does not know you're doing the latter.
        model.setQuery(query)
# https://forum.qt.io/topic/13658/qsqltablemodel-qtableview-how-to-sort-by-column/2

        proxyModel = QSortFilterProxyModel(model)
        proxyModel.setSourceModel(model)
        self.tableLastCL.setModel(proxyModel)
        self.tableLastCL.sortByColumn(1,Qt.SortOrder.AscendingOrder)
        self.tableLastCL.setSortingEnabled(True)
        #self.tableLastCL.reset()
        #self.tableLastCL.show()
        self.tableLastCL.setColumnWidth(3, 400)
        #self.tableLastCL.resizeColumnsToContents()
        self.tableLastCL.setAlternatingRowColors(True)

        #while self.queryLastCL.next():
        #    lastOK  = self.queryLastCL.value(0)
        if query.first():
#            self.lastSignedLineId = query.value(0)
            self.lastSigned = query.value(1)
            print("lastOrder: " + str(self.lastSigned)) # + ", lastLineId: " + str(self.lastSignedLineId))
        else:
            self.lastSigned = 0
        #    lastOK  = 0
        #    lastLineId  = 0
        #print(self.queryLastCL.lastQuery())
        #self.update_queryLastCL()
        #elf.lastSigned = lastOK
        #self.lastSignedId = lastLineId

    def update_queryWaitOK(self):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        model = self.tableWaitOK.model()
        query = model.query()
        # queryWaitOK = QSqlQuery(db=db)
        """
        queryWaitOK.prepare(
            "SELECT CheckLineId, LineOrder, LineDesc, SignedBy "
            "FROM ChecklistLines "
            "WHERE LineOrder > :l_order AND Checklist = :list_id AND SignedBy = :sign_by "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC LIMIT 3"
        )
        #queryWaitOK.bindValue(":l_order", lastOK)
        """

        query.bindValue(":l_order", self.lastSigned)
        query.bindValue(":list_id", self.listId)
        query.bindValue(":sign_by", self.signBy)
        query.exec()
        if query.first():
            self.nextLineId  = query.value(0)
        else:
            self.nextLineId  = 0
        # print("Wait: " + queryWaitOK.lastQuery() + ", next Id: " + str(self.nextLineId))
        #modelWaitOK = QSqlQueryModel()
        model.setQuery(query)
        self.tableWaitOK.setColumnWidth(0,160)
        self.tableWaitOK.setColumnWidth(1,160)
        self.tableWaitOK.setColumnWidth(2,300)

    def checkButt_clicked(self):
        #print("click ", s)
        qryCheckPrecedence = QSqlQuery(db=db)
        qryCheckPrecedence.prepare(
            "SELECT Line, PrecededBy "
            "FROM CheckPrecedence "
            "INNER JOIN ChecklistLines ON Line = ChecklistLines.CheckLineId "
            "WHERE Line = :line_id "
            "ORDER BY Line ASC"
        )
        qryCheckPrecedence.bindValue(":line_id", self.nextLineId)
        qryCheckPrecedence.exec()

        qryCheckSigned = QSqlQuery(db=db)
        qryCheckSigned.prepare(
            "SELECT CheckLine, ShotNumber, checkValue "
            "FROM CheckLineSigned "
            "WHERE CheckLine = :line AND ShotNumber = :shot_no"
        )
        
        # print("Last qryCheckPrecedence: " + qryCheckPrecedence.executedQuery() + ' list_id: ' + str(self.nextLineId))
        missingSigned = False
        lines_not_found = ""
        while qryCheckPrecedence.next():
            lineBefore  = qryCheckPrecedence.value(1)
            qryCheckSigned.bindValue(":line", lineBefore)
            qryCheckSigned.bindValue(":shot_no", self.shotNo)
            qryCheckSigned.exec()
            # print(qryCheckSigned.lastQuery() + "; Line Before: " + str(lineBefore))
            if not qryCheckSigned.first():
                print("Line Before not Signed: " + str(lineBefore))
                lines_not_found = lines_not_found + f'<p> not Signed: {lineBefore} </p>'
                missingSigned = True
            else:
                print("Line Signed Value: " + str(qryCheckSigned.value(2)))
            #lastLineId  = qryCheckPrecedence.value(0)

        if missingSigned:
            dlg = QDialog(self)
            dlg.setWindowTitle("Missing Signatures. Please Check.")
            print("Missing Signatures. Please Check.")
            dlg.resize(400, 100)
            #dlg.exec()
            QMessageBox.critical(None, "Error",
                f"""<p>The following checklines are missing
                </p> {lines_not_found}""")
            return

        insertCLine = QSqlQuery(db=db)
        insertCLine.prepare("INSERT INTO CheckLineSigned VALUES (NULL, :shot_no, "
                "current_timestamp(), :cLine_id, :sign_by, 0, NULL)")
        insertCLine.bindValue(":shot_no", self.shotNo)
        insertCLine.bindValue(":cLine_id", self.nextLineId)
        insertCLine.bindValue(":sign_by", self.signBy)
        # self.insertCLine.bindValue(":cLine_id", 6)
        dlg = SignDialog(self)
        if dlg.exec():
            #print("Success! " + str(self.nextLineId))
            if insertCLine.exec():
                print("Inserted record")
                self.update_queryLastCL()
                self.update_queryWaitOK()
            else:
                #print("NOT Inserted")
                print("Insert failed: " + insertCLine.lastQuery())
                print(f":shot_no + {self.shotNo} :cLine_id {self.nextLineId} :sign_by {self.signBy}")
        else:
            print("Cancel!")

        #insertCLine.bindValue(":sign_by", self.shotNo)

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

"""
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
        modelCL = QSqlQueryModel()
        modelCL.setQuery(queryCL)
        self.tableCL.setModel(modelCL)
        self.tableCL.setColumnWidth(0,60)
        self.tableCL.setColumnWidth(1,100)
        self.tableCL.setColumnWidth(2,100)
        self.tableCL.setColumnWidth(3,60)
        self.tableCL.setColumnWidth(4,600)

"""
