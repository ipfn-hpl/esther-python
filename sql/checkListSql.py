#!/usr/bin/env python3
"""
PyQt6 SQL App for signing Esther Checklists
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
        "SELECT CheckLineId, ChecklistName, "
        "EstherRoles.RoleName, "
        "LineOrder, LineDesc FROM ChecklistLines "
        "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
        "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
        "INNER JOIN EstherRoles ON CheckBy = EstherRoles.RoleId "
        "WHERE Checklist = :list_id AND DayPlan = :plan_id "
        "ORDER BY LineOrder ASC"
        )

CHECKLINE_LAST_QUERY = (
        "SELECT CheckLine, ChecklistLines.LineOrder, "
        "LineStatusDate, ChecklistLines.LineDesc, "
        "EstherRoles.ShortName, SignValues.SignatureName "
        "FROM CheckLineSigned "
        "INNER JOIN ChecklistLines ON CheckLineSigned.CheckLine = ChecklistLines.CheckLineId "
        "INNER JOIN EstherRoles ON ChecklistLines.CheckBy = EstherRoles.RoleId "
        "INNER JOIN SignValues ON checkValue = SignValues.SignId "
        "WHERE CheckLineSigned.ShotNumber = :shot_no AND "
        # "CheckLineSigned.SignedBy = :sign_by AND "
        "ChecklistLines.Checklist = :list_id "
        # "WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
        "ORDER BY LineStatusDate DESC LIMIT 5"
        )

CHECK_WAITING_LIST_QUERY = (
        "SELECT CheckLineId, LineOrder, LineDesc, "
        "EstherChecklists.ChecklistName, "
        "DayPlans.DayPlanName, "
        "EstherRoles.ShortName AS Responsible, CheckBy "
        "FROM ChecklistLines "
        "INNER JOIN EstherChecklists ON Checklist = EstherChecklists.ChecklistId "
        "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
        "INNER JOIN EstherRoles ON CheckBy = EstherRoles.RoleId "
        "WHERE LineOrder > :l_order AND DayPlan = :d_plan AND "
        "Checklist = :list_id "
        "ORDER BY LineOrder ASC LIMIT 4"
        )
        # "Checklist = :list_id AND CheckBy = :sign_by "

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

        self.rBv = QRadioButton('No Problem', self)
        self.rBv.setChecked(True)
        self.rBa = QRadioButton('Attention required', self)
        self.layout = QVBoxLayout()
        message = QLabel("Sure you want to sign this Checkline?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.rBv)
        self.layout.addWidget(self.rBa)
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
        self.nextLineId = 0
        self.nextLineRole = 0
        if queryGlobal.exec(
                "SELECT ShotNumber FROM CheckLineSigned "
                "ORDER BY ShotNumber DESC LIMIT 1"):
            if queryGlobal.first():
                self.shotNo = queryGlobal.value(0)
        list_names = []
        if queryGlobal.exec(
                "SELECT ChecklistName FROM EstherChecklists "
                "ORDER BY ChecklistId ASC"):
            while queryGlobal.next():
                list_names.append(queryGlobal.value(0))
            print(list_names)
        self.tableCL = QTableView()
        qryModel = QSqlQueryModel()
        self.tableCL.setModel(qryModel)

        self.tableLastCL = QTableView()
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

        layoutTables.addWidget(self.tableLastCL)

        label = QLabel('Next Lines to Check')
        label.setFont(FONT_NORMAL)
        layoutTables.addWidget(label)
        layoutTables.addWidget(self.tableWaitSign)

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

        # layoutTools.addWidget(QLabel('Checklist:'))
        # listComb = QComboBox()
        #listComb.addItems(["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"])
#        layoutTools.addWidget(listComb)

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
        self.update_queryWaitSign()
        self.update_ChkLists()
        shotSpin.valueChanged.connect(self.shot_changed)
        # listComb.currentIndexChanged.connect(self.list_changed)
        self.setMinimumSize(QSize(1200, 800))
        self.setCentralWidget(container)

    def plan_changed(self, i):
        #        print('plan is ' + str(i))
        self.planId = i
        # self.update_queryCL()
        self.update_ChkLists()
        self.update_queryLastCL()
        self.update_queryWaitSign()

    def list_changed(self, i):
        print('list is ' + str(i))
        self.listId = i
        # self.update_queryCL()
        self.update_ChkLists()
        self.update_queryLastCL()
        self.update_queryWaitSign()

    def shot_changed(self, i):
        print('Shot is ' + str(i))
        self.shotNo = i
        self.update_queryLastCL()
        self.update_queryWaitSign()

    def update_signBy(self):
        # get the radio button the send the signal
        rb = self.sender()
        # check if the radio button is checked
        if rb.isChecked():
            print("signBy is %s" % (rb.sign))
            self.signBy = rb.sign
            # self.update_ChkLists()
            self.update_queryLastCL()
            self.update_queryWaitSign()
            # self.result_label.setText(f'You selected {rb.text()}')

    def update_ChkLists(self):
        print('count is ' + str(self.tabs.count()))
        for i in range(self.tabs.count()):
            tabw = self.tabs.widget(i)
            model = tabw.model()
            query = model.query()
            query.bindValue(":plan_id", self.planId)
            query.bindValue(":list_id", i)
            if (not query.exec()):
                print(f"NOT exec(). CL Query i: {i}", end='')
                print(f"{query.executedQuery()} signBy: {self.signBy}")
            # return
            model.setQuery(query)
            tabw.setAlternatingRowColors(True)
            tabw.setColumnWidth(0, 80)
            tabw.setColumnWidth(3, 100)
            tabw.setColumnWidth(4, 400)

    def update_queryLastCL(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        model = QSqlQueryModel()
        query = QSqlQuery(db=db)
        query.prepare(CHECKLINE_LAST_QUERY)
        # qryModel.setQuery(query)
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

        if query.first():
            self.lastSigned = query.value(1)
            print("lastOrder: " + str(self.lastSigned))
        else:
            self.lastSigned = 0
        #    lastOK  = 0
        #    lastLineId  = 0
        # print(self.queryLastCL.lastQuery())
        # self.update_queryLastCL()
        # self.lastSignedId = lastLineId

    def update_queryWaitSign(self):
        # print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        model = self.tableWaitSign.model()
        query = model.query()
        # queryWaitOK = QSqlQuery(db=db)
        query.bindValue(":l_order", self.lastSigned)
        query.bindValue(":list_id", self.listId)
        # query.bindValue(":sign_by", self.signBy)
        query.bindValue(":d_plan", self.planId)
        if query.exec():
            if query.first():
                self.nextLineId = query.value(0)
                self.nextLineRole = query.value(6)
                print(f"Next Role {self.nextLineRole}")
            else:
                self.nextLineId = 0
            model.setQuery(query)
            self.tableWaitSign.setColumnWidth(0, 100)
            self.tableWaitSign.setColumnWidth(1, 100)
            self.tableWaitSign.setColumnWidth(2, 400)
        else:
            print("Last Wait Query: " + query.executedQuery())
        # print("Wait: " + queryWaitOK.lastQuery() + ", next Id: " + str(self.nextLineId))

    def checkPrecendence(self):
        # print("click ", s)
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
            lineBefore = qryCheckPrecedence.value(1)
            qryCheckSigned.bindValue(":line", lineBefore)
            qryCheckSigned.bindValue(":shot_no", self.shotNo)
            qryCheckSigned.exec()
            # print(qryCheckSigned.lastQuery() + "; Line Before: " + str(lineBefore))
            if not qryCheckSigned.first():
                print(f"Line Before not Signed: {lineBefore}")
                if not queryGlobal.exec(
                        "SELECT EstherChecklists.ChecklistName, CheckLineId, Checklist FROM ChecklistLines "
                        "INNER JOIN EstherChecklists ON Checklist = EstherChecklists.ChecklistId "
                        f"WHERE CheckLineId = {lineBefore}"
                        ):
                     print(queryGlobal.lastQuery())

                if queryGlobal.first():
                    listName = queryGlobal.value(0)
                else:
                    listName = 'NoList'

                lines_not_found = lines_not_found + f'<p>Line Id: {lineBefore} List: {listName} </p>'
                missingSigned = True
            else:
                print("Line Signed Value: " + str(qryCheckSigned.value(2)))
            # lastLineId  = qryCheckPrecedence.value(0)

        if missingSigned:
            dlg = QDialog(self)
            dlg.setWindowTitle("Missing Signatures. Please Check.")
            print("Missing Signatures. Please Check.")
            dlg.resize(400, 100)
            # dlg.exec()
            QMessageBox.critical(
                    None, "Error",
                    f"""<p>The following checklines are missing
                </p> {lines_not_found}""")
            return False
        else:
            return True

    def checkLineButtOK_clicked(self):
        if self.nextLineRole == self.signBy:
            if self.checkPrecendence():
                insertCLine = QSqlQuery(db=db)
                insertCLine.prepare(
                    "INSERT INTO CheckLineSigned VALUES (NULL, :shot_no, "
                    "current_timestamp(), :cLine_id, 0, :sign_val, NULL)")
                insertCLine.bindValue(":shot_no", self.shotNo)
                insertCLine.bindValue(":cLine_id", self.nextLineId)
                # insertCLine.bindValue(":sign_by", self.signBy)
                insertCLine.bindValue(":sign_val", 0)  # OK
                if insertCLine.exec():
                    print("Inserted record")
                    self.update_queryLastCL()
                    self.update_queryWaitSign()
                else:
                    QMessageBox.critical(
                            None, "Record NOT Inserted ", "SQL Error")
                    print(f"Insert failed: {insertCLine.lastQuery()}")
                    # print(f":shot_no + {self.shotNo} :cLine_id {self.nextLineId} :sign_by {self.signBy}")
            else:
                print("Cancel!")
        else:
            QMessageBox.warning(
                    None, "NOT Inserted ", "Next Line not signed by you...")

    def checkLineButt_clicked(self):
        if self.nextLineRole == self.signBy:
            if self.checkPrecendence():
                insertCLine = QSqlQuery(db=db)
                insertCLine.prepare(
                    "INSERT INTO CheckLineSigned VALUES (NULL, :shot_no, "
                    "current_timestamp(), :cLine_id, 0, :sign_val, NULL)")
                insertCLine.bindValue(":shot_no", self.shotNo)
                insertCLine.bindValue(":cLine_id", self.nextLineId)
                # insertCLine.bindValue(":sign_by", self.signBy)
            # self.insertCLine.bindValue(":cLine_id", 6)
                dlg = SignDialog(self)
                if dlg.exec():
                    if dlg.rBv.isChecked():
                        signVal = 0
                    elif dlg.rBa.isChecked():
                        signVal = 1
                    else:
                        signVal = 255
                    print(f"dlg rBv: {signVal}")
                    insertCLine.bindValue(":sign_val", signVal)
                # print("Success! " + str(self.nextLineId))
                    if insertCLine.exec():
                        QMessageBox.information(
                            None, "Record Inserted ", f"dlg rBv: {signVal}")
                        print("Inserted record")
                        self.update_queryLastCL()
                        self.update_queryWaitSign()
                    else:
                        QMessageBox.critical(
                            None, "Record NOT Inserted ", f"dlg rBv: {signVal}")
                    # print("NOT Inserted")
                        print(f"Insert failed: {insertCLine.lastQuery()}")
                        # print(f":shot_no + {self.shotNo} :cLine_id {self.nextLineId} :sign_by {self.signBy}")
                else:
                    print("Cancel!")
            else:
                print("Missing Lines!")
        else:
            QMessageBox.warning(
                    None, "NOT Inserted ", "Next Line not signed by you...")

    def make_report_pdf(self):
        # report_pdf(self.shotNo, self.signBy, self.listId)
        report_pdf(db, self.shotNo, self.listId)

    #    self.model.select()


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
