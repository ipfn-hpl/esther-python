#!/usr/bin/env python3
"""
PyQt6 SQL App for making Esther Report Checklists
https://www.reportlab.com/docs/reportlab-userguide.pdf
"""

#import os
#import sys

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Paragraph, Spacer, Table,
                                TableStyle, SimpleDocTemplate,)
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.rl_config import defaultPageSize
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styleSheet = getSampleStyleSheet()

from PyQt6.QtSql import (
        QSqlDatabase,
        #QSqlRelation,
        #QSqlRelationalDelegate,
        #QSqlRelationalTableModel,
        #QSqlTableModel,
        QSqlQuery,
        )
CHECK_LIST_QUERY = ("SELECT CheckLineId, ChecklistName, EstherRoles.RoleName, "
                    "LineOrder, LineDesc FROM ChecklistLines "
                    "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
                    "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
                    "INNER JOIN EstherRoles ON CheckBy = EstherRoles.RoleId "
                    "WHERE Checklist = :list_id AND DayPlan = :plan_id "
                    "ORDER BY LineOrder ASC"
                    )

CHECKLINE_LAST_QUERY = ("SELECT CheckLine, ChecklistLines.LineOrder, LineStatusDate, ChecklistLines.LineDesc, "
                        "EstherRoles.RoleName, checkValue "
                        "FROM CheckLineSigned "
                        "INNER JOIN ChecklistLines ON CheckLineSigned.CheckLine = ChecklistLines.CheckLineId "
                        "INNER JOIN EstherRoles ON ChecklistLines.CheckBy = EstherRoles.RoleId "
                        "WHERE CheckLineSigned.ShotNumber = :shot_no AND CheckLineSigned.SignedBy = :sign_by AND ChecklistLines.Checklist = :list_id "
                        #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked "
                        "ORDER BY LineStatusDate DESC LIMIT 4")

LIST_NAMES = ["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"]
db = QSqlDatabase("QMARIADB")
#db.setHostName("epics.ipfn.tecnico.ulisboa.pt");
db.setHostName("efda-marte.ipfn.tecnico.ulisboa.pt");
#db.setHostName("localhost");
db.setDatabaseName("archive");
db.setUserName("archive");
db.setPassword("$archive");

db.open()

query = QSqlQuery(db=db)
list_names = []
dataTable = []
qn = []
        #insertCLine.bindValue(":sign_by", self.shotNo)

def report_pdf(shotNo, signBy, listId):
    # Create the report
    if query.exec("SELECT ChecklistName FROM EstherChecklists ORDER BY ChecklistId ASC"):
        while query.next():
            print(query.value(0))
            list_names.append(query.value(0))
    query.prepare(CHECKLINE_LAST_QUERY)
    #qryModel.setQuery(query)
    #self.tableLastCL.setModel(qryModel)
    query.bindValue(":shot_no", shotNo)
    query.bindValue(":sign_by", signBy)
    query.bindValue(":list_id", listId)
    pdf = canvas.Canvas(f"report_{shotNo}.pdf", pagesize=A4)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, "Customer Report")
    pdf.setFont("Helvetica", 12)
    P0 = Paragraph('A paragraph1', styleSheet["BodyText"])
    multiline_text =  '''
    The ReportLab Left
    Logo
    Image'''
    if (query.exec()):
        y = 700
        while query.next():
            qn.append(query.next())
            line = []
            line.append(query.value(0))
            line.append(query.value('RoleName'))
            #line.append(query.value('ChecklistName'))LineStatusDate
            #line.append(query.value('LineStatusDate'))
            print(query.value('LineStatusDate'))
            line.append(query.value('checkValue'))
            P0 = Paragraph(query.value(3), styleSheet["BodyText"])
            #line.append(query.value(3))
            line.append(P0)
            dataTable.append(line)
            pdf.drawString(50, y, f"Name: {query.value(0)}")
            pdf.drawString(50, y-20, f"Description: {query.value(3)}")
            y -= 60
    else:
        print("NOT exec(). Query : " + query.executedQuery() + " signBy: ")
    data1= [['00', '01', '02', '03', '04','10', '11', '12', '13', '14'],
                ['10', '11', '12', '13', '14', '10', '11', '12', '13', '14'],
                ['20', '21', '22', '23', '24', '10', '11', '12', '13', '14'],
                ['30', '31', '32', '33', '34', '10', '11', '12', '13', '14']]

    t1=Table(dataTable)
    t1.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                ]))
    #pdf.save()

    doc = SimpleDocTemplate(f"test_{shotNo}.pdf", pagesize=A4)
    elements = [Spacer(1,1*inch)]
    style = styleSheet["Normal"]
    p = Paragraph("Esther Report", style)
    elements.append(p)
    elements.append(t1)
    # write the document to disk
    doc.build(elements)

if __name__ == '__main__':
    shotNum=180
    report_pdf(shotNum, 0, 1)
    #query = QSqlQuery(db=db)

# vim: syntax=python ts=4 sw=4 sts=4 sr et

