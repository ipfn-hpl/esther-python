#!/usr/bin/env python3
"""
PyQt6 SQL App for signed Esther Reports
"""

#import os
import sys

from PyQt6.QtCore import QSize, Qt
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

from epics import caget, caput, cainfo

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
        shotSpin.setMinimum(170)
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

        layoutTools.addWidget(refreshButt)
#        layoutTools.addWidget(QLabel('Exp. Phase'))
        layoutTables.addWidget(self.tableReports)
        layoutTables.addWidget(self.tableViewReports)

        layoutMain.addLayout(layoutTools)
        layoutMain.addLayout(layoutTables)
        container.setLayout(layoutMain)
        self.setMinimumSize(QSize(1200, 800))
        self.setCentralWidget(container)
        self.update_queryReports()
        

    def shot_changed(self, i):
        print('shot is ' + str(i))
        self.shotNo = i
        #self.update_queryLastCL()
        #self.update_queryWaitOK()
        self.update_queryReports()

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
        print(queryReports.lastQuery()) #  + "; Line Before: " + str(lineBefore))
        model = QSqlQueryModel()
        model.setQuery(queryReports)
        self.tableReports.setModel(model)
        self.tableReports.setColumnWidth(0,60)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# vim: syntax=python ts=4 sw=4 sts=4 sr et
