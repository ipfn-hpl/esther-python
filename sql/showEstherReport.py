#!/usr/bin/env python3
"""
PyQt6 SQL App for signed Esther Reports
"""

#import os
import sys

from PyQt6.QtCore import QSize, Qt

from PyQt6.QtGui import QFont

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
    QVBoxLayout, QHBoxLayout,
    QWidget,
    QDialog,
    QDialogButtonBox, QPushButton,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QRadioButton,
    QLabel,
    QTableWidget, QTableWidgetItem,
)

from epics import caget, caput, cainfo

# import os

# os.environ['EPICS_CA_ADDR_LIST'] = '10.10.136.128'
# os.environ['EPICS_CA_ADDR_LIST'] = 'localhost 192.168.1.110'
# os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'

#basedir = os.path.dirname(__file__)

# db = QSqlDatabase("QSQLITE")
#db.setDatabaseName(os.path.join(basedir, "chinook.sqlite"))
#db.open()

db = QSqlDatabase("QMARIADB")
db.setHostName("epics.ipfn.tecnico.ulisboa.pt");
#db.setHostName("10.10.136.177");
#db.setHostName("localhost");
db.setDatabaseName("archive");
db.setUserName("archive");
db.setPassword("$archive");
# db.setUserName("report");
# db.setPassword("$report");

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
        
        self.shotNo = 177
        self.signBy = 0
        self.lastSigned = 0
        self.tableReports = QTableView()
        container = QWidget()
        layoutMain = QHBoxLayout()
        layoutTools = QVBoxLayout()
        layoutTables = QVBoxLayout()

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
        
        shotSpin = QSpinBox()
        shotSpin.setMinimum(10)
        shotSpin.setMaximum(1000) # May need to change (hopefully)
# Or: widget.setRange(-10,3)
    #widget.setPrefix("$")
#widget.setSuffix("c")
        shotSpin.setSingleStep(1) # Or e.g. 0.5 for QDoubleSpinBox
        self.shotNo = 160
        shotSpin.setValue(self.shotNo)
        shotSpin.valueChanged.connect(self.shot_changed)
        layoutTools.addWidget(shotSpin)

        tableModelReports = QSqlTableModel(db=db)
        tableModelReports.setTable('esther_reports')
        tableModelReports.setFilter("shot_number > 160")
        tableModelReports.select()

        self.tableViewReports = QTableView()
        self.tableViewReports.setModel(tableModelReports)
        self.tableReport = QTableWidget(2,6)
        self.tableReport.setHorizontalHeaderLabels(("O2 Bottle","He I Bottle","H2 Bottle",'He II Bottle','N2 Bottle', 'N2 Command Bottle'))
        self.tableReport.setVerticalHeaderLabels(('Initial','Final',))

        layoutTools.addWidget(refreshButt)
#        layoutTools.addWidget(QLabel('Exp. Phase'))
        label = QLabel('Bottle Pressures (Bar)')
        label.setFont(QFont('Arial', 20))
        layoutTables.addWidget(label)
        layoutTables.addWidget(self.tableReport)
        label = QLabel('Partial Pressures (Bar)')
        label.setFont(QFont('Arial', 20))
        layoutTables.addWidget(label)
        #layoutTables.addWidget(self.tableReports)
        layoutTables.addWidget(self.tableViewReports)

        layoutMain.addLayout(layoutTools)
        layoutMain.addLayout(layoutTables)
        container.setLayout(layoutMain)
        self.setMinimumSize(QSize(1200, 800))
        self.setCentralWidget(container)
        self.update_queryReports()
        self.update_Report()
        

    def set_cell(self, qR, name, lin, col):
        val  = qR.value(name)
        item = QTableWidgetItem(f'{val:0.2f}')
        self.tableReport.setItem(lin,col, item)
    def shot_changed(self, i):
        print('shot is ' + str(i))
        self.shotNo = i
        #self.update_queryLastCL()
        #self.update_queryWaitOK()
        self.update_queryReports()
        self.update_Report()

    def update_Report(self, s=None):
        queryReport = QSqlQuery(db=db)
        queryReport.prepare(
            "SELECT shot_number, esther_reports.manager_id, "
            "O2_bottle_initial, O2_bottle_final, He1_bottle_initial, He1_bottle_final, "
            "H_bottle_initial, H_bottle_final, N2_bottle_initial, N2_bottle_final, "
            "esther_managers.manager_name, start_time, end_time "
            "FROM esther_reports "
            "INNER JOIN esther_managers ON esther_reports.manager_id = esther_managers.manager_id "
            #"WHERE shot_number  > 160 "
            "WHERE shot_number  = :shot_no "
        )

        queryReport.bindValue(":shot_no", self.shotNo)
        queryReport.exec()
        if queryReport.first():
            #val  = queryReport.value(2)
            self.set_cell(queryReport, 'O2_bottle_initial', 0, 0)
            self.set_cell(queryReport, 'O2_bottle_final', 1, 0)
            val  = queryReport.value('N2_bottle_initial')
            lastOK      = queryReport.value(1)
            item = QTableWidgetItem(f'{val:0.2f}')
            #item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tableReport.setItem(0,4, item)
            #val  = queryReport.value(3)
            val  = queryReport.value('N2_bottle_final')
            item = QTableWidgetItem(f'{val:0.2f}')
            self.tableReport.setItem(1,4, item)
        else:
            val  = 0
            lastLineId  = 0
            print('No Report')
        print(queryReport.lastQuery() + str(val))

    def update_queryReports(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        queryReports = QSqlQuery(db=db)
        queryReports.prepare(
            "SELECT shot_number, esther_reports.manager_id, "
            "esther_managers.manager_name, start_time, end_time "
            "FROM esther_reports "
            "INNER JOIN esther_managers ON esther_reports.manager_id = esther_managers.manager_id "
            #"INNER JOIN EstherRoles ON SignedBy = EstherRoles.RoleId "
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
