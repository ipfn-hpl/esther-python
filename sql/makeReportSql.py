#!/usr/bin/env python3
"""
PyQt6 SQL App for making Esther Report Checklists
https://www.reportlab.com/docs/reportlab-userguide.pdf
"""

#import os
import sys

# from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (Paragraph, Spacer, Table,
                                TableStyle, SimpleDocTemplate,)
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.rl_config import defaultPageSize

from PyQt6.QtSql import (
        QSqlDatabase,
        QSqlQuery,
        )

PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styleSheet = getSampleStyleSheet()

shotNum = 180
listId = 0
if len(sys.argv) > 2:
    listId = int(sys.argv[2])
if len(sys.argv) > 1:
    shotNum = int(sys.argv[1])

'''
CHECK_LIST_QUERY = ("SELECT CheckLineId, ChecklistName, EstherRoles.RoleName, "
                    "LineOrder, LineDesc FROM ChecklistLines "
                    "INNER JOIN DayPlans ON DayPlan = DayPlans.DayPlanId "
                    "INNER JOIN EstherChecklists ON ChecklistLines.Checklist = EstherChecklists.ChecklistId "
                    "INNER JOIN EstherRoles ON CheckBy = EstherRoles.RoleId "
                    "WHERE Checklist = :list_id AND DayPlan = :plan_id "
                    "ORDER BY LineOrder ASC"
                    )
'''
CHECKLINE_LAST_QUERY = ("SELECT CheckLine, ChecklistLines.LineOrder, LineStatusDate, ChecklistLines.LineDesc, "
                        "EstherRoles.RoleName, EstherRoles.ShortName, checkValue "
                        "FROM CheckLineSigned "
                        "INNER JOIN ChecklistLines ON CheckLineSigned.CheckLine = ChecklistLines.CheckLineId "
                        "INNER JOIN EstherRoles ON ChecklistLines.CheckBy = EstherRoles.RoleId "
                        "WHERE CheckLineSigned.ShotNumber = :shot_no AND ChecklistLines.Checklist = :list_id "
                        #"WHERE Checklist = :list_id AND ChiefEngineer = :ce_checked AND Researcher = :re_checked  AND CheckLineSigned.SignedBy = :sign_by"
                        "ORDER BY LineStatusDate ASC")

#LIST_NAMES = ["Master", "Combustion Driver", "Vacuum","Test Gases (CT, ST)","Shock Detection System","Optical Diagnostics","Microwave Diagnostics"]
db = QSqlDatabase("QMARIADB")
#db.setHostName("epics.ipfn.tecnico.ulisboa.pt");
db.setHostName("efda-marte.ipfn.tecnico.ulisboa.pt");
#db.setHostName("localhost");
db.setDatabaseName("archive");
db.setUserName("archive");
db.setPassword("$archive");

db.open()

list_names = []
dataTable = []

def report_pdf(db, shotNo, listId):
    query = QSqlQuery(db=db)
    # Create the report
    if query.exec("SELECT ChecklistName FROM EstherChecklists ORDER BY ChecklistId ASC"):
        while query.next():
            #print(query.value(0))
            list_names.append(query.value(0))
    query.prepare(CHECKLINE_LAST_QUERY)
    #qryModel.setQuery(query)
    query.bindValue(":shot_no", shotNo)
    query.bindValue(":list_id", listId)
    #P0 = Paragraph('A paragraph1', styleSheet["BodyText"])
    doc = SimpleDocTemplate(f"test_{shotNo}.pdf", pagesize=A4)
    #elements = [Spacer(1,1*inch)]
    elements = []
    styleNormal= styleSheet["Normal"]
    p = Paragraph(f"Esther Report. Shot: {shotNo}. Check List: {list_names[listId]}", styleNormal)
    #time_format = "yyyy-MM-dd HH:mm:ss"
    time_format = "HH:mm:ss"
    elements.append(p)
    elements.append(Spacer(1,0.2*inch))
    #elements.append(Paragraph(" ", style))
    styleDesc = ParagraphStyle(
        #name='Normal',
        name='Helvetica',
        fontSize = 9,
    )
    if (query.exec()):
        while query.next():
            #qn.append(query.next())
            line = []
            #line.append(query.value('CheckLine'))
            line.append(f"{query.value('ShortName')}{query.value('LineOrder')}")
            #print(str(query.value('LineStatusDate')))
            #print(query.value('LineDesc'))
            P0 = Paragraph(str(query.value('LineDesc')), styleDesc)
            #P0 = Paragraph(str(query.value('LineDesc')), styleSheet["BodyText"])
            line.append(P0)
            line.append(query.value('checkValue'))
            line.append(query.value('LineStatusDate').toString(time_format))
            dataTable.append(line)

    else:
        print("NOT exec(). Query : " + query.executedQuery())
    
    if(len(dataTable) > 0):
        t1=Table(dataTable, colWidths=(38, 400, 25, 50))
        t1.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.blue),
                                ]))
    else:
        t1 = Paragraph("NO Checked Lines in this Report", styleNormal)
    elements.append(t1)
    # write the document to disk
    doc.build(elements)

if __name__ == '__main__':
    report_pdf(db, shotNum, listId)
    #query = QSqlQuery(db=db)

# vim: syntax=python ts=4 sw=4 sts=4 sr et

