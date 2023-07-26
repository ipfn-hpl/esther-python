#!/usr/bin/env python3
"""
PyQt6 SQL App example
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
    QLabel,
)

#basedir = os.path.dirname(__file__)

# db = QSqlDatabase("QSQLITE")
#db.setDatabaseName(os.path.join(basedir, "chinook.sqlite"))
#db.open()

db = QSqlDatabase("QMARIADB")
db.setHostName("10.136.240.213");
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
        self.list = QLineEdit()
        self.list.setPlaceholderText("1")
        self.list.textChanged.connect(self.update_query)
        self.ceChck = QCheckBox("Chief Engineer")
        self.ceChck.setCheckState(Qt.CheckState.Checked)
# For tristate: widget.setCheckState(Qt.PartiallyChecked)
# Or: widget.setTristate(True)
        self.ceChck.stateChanged.connect(self.update_ce)

        self.reChck = QCheckBox("Researcher")
        self.reChck.setCheckState(Qt.CheckState.Unchecked)
        self.reChck.stateChanged.connect(self.update_re)

        layoutTools.addWidget(refreshButt)
        layoutTools.addWidget(QLabel('Filter Checklist:'))
        layoutTools.addWidget(self.shot)
        layoutTools.addWidget(self.list)
        layoutTools.addWidget(self.ceChck)
        layoutTools.addWidget(self.reChck)
        #layoutTools.addWidget(self.search)

        self.table = QTableView()
        self.tableOK = QTableView()
        layoutMain.addLayout(layoutTools)
        layoutMain.addWidget(self.table)
        layoutMain.addWidget(self.tableOK)
        container.setLayout(layoutMain)
        
        #self.table = QTableView()
        self.model = QSqlQueryModel()
        self.table.setModel(self.model)
        #query = QSqlQuery("SELECT DayPlan, EstherChecklists.ChecklistName FROM ChecklistLines INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId", db=db)
        self.query = QSqlQuery(db=db)
        self.query.prepare(
            "SELECT DayPlan, EstherChecklists.ChecklistName, ChiefEngineer, Researcher, LineStatus FROM ChecklistLines "
            "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
            "WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineOrder ASC"
        )
        #query = QSqlQuery("SELECT * FROM 'ChecklistLines' ORDER BY 'ChecklistLines'.'LineOrder' ASC", db=db)
        #query = QSqlQuery("SELECT * FROM ChecklistLines", db=db)

        #self.table.setModel(self.model)
        self.query.bindValue(":list_id", 1)
        self.query.bindValue(":ce_checked", '1')
        self.query.bindValue(":re_checked", '0')

        #self.model.removeColumns(0,1)
        #self.model.select()
        self.modelOK = QSqlQueryModel()
        self.tableOK.setModel(self.modelOK)
        self.queryOK = QSqlQuery(db=db)
        self.queryOK.prepare(
            "SELECT LineStatusDate, CheckLine, SignedBy FROM CheckLinesOk "
           # "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
         #   "WHERE ShotNumber = :shot_no "
            #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
            "ORDER BY LineStatusDate DESC LIMIT 1"
        )
        self.queryOK.bindValue(":shot_no", 177)
        self.queryOK.exec()
        self.modelOK.setQuery(self.queryOK)
        print(self.queryOK.lastQuery())

        self.update_query()
        self.setMinimumSize(QSize(1424, 800))
        self.setCentralWidget(container)

    def update_ce(self, s):
        if (Qt.CheckState(s) == Qt.CheckState.Checked):
            self.query.bindValue(":ce_checked", '1')
        else:
            self.query.bindValue(":ce_checked", '0')
        self.update_query()

    def update_re(self, s):
        if (Qt.CheckState(s) == Qt.CheckState.Checked):
            self.query.bindValue(":re_checked", '1')
            print(Qt.CheckState(s) == Qt.CheckState.Checked)
        else:
            self.query.bindValue(":re_checked", '0')
            print(Qt.CheckState(s) == Qt.CheckState.Checked)
        self.update_query()
        print(s)

    def update_query(self, s=None):
        #print(Qt.CheckState(self.ceChck) == Qt.CheckState.Checked)
        #print(s)
        self.query.bindValue(":list_id", self.list.text())
        self.query.exec()
        self.model.setQuery(self.query)

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
