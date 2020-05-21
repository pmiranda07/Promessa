#!/usr/bin/env python3
import json
import datetime


fn = "/Users/pmiranda/Desktop/Tese/Data/output.json"

k = open("/Users/pmiranda/Desktop/output.sql", "w")

with open (fn,'r') as f:
    jsondata = json.loads(f.read())

def elementExist(listToCheck,elementToCheck):
    userExist = False
    for k in listToCheck: 
        if k == elementToCheck:
            userExist = True
            break
    return userExist

def replace(ObjectToReplace):
    for v in ObjectToReplace:
        if ObjectToReplace[v] == "":
           ObjectToReplace[v] = 'NULL'
        elif (type(ObjectToReplace[v]) in (bytes,str) and has_symbol(ObjectToReplace[v],"\u0027")):
            ObjectToReplace[v]= ObjectToReplace[v].replace("\u0027","''")
    return ObjectToReplace


def is_date(string):

    try:
        datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f%z')
        return True
    except ValueError:
        return False

def has_symbol(string, symbol):
    if (string.find(symbol) != -1): 
        return True
    else: 
        return False



k.write("CREATE TABLE output (id integer PRIMARY KEY, summary text, key text, type text, created timestamp without time zone , assignee integer, creator integer, reporter integer, project integer, status integer, updated timestamp without time zone , priority text, aggregateProgress integer, aggregateProgressTotal integer, aggregateTimeEstimate integer, aggregateTimeSpent integer, sprints integer[], issueLinks text, labels text, resolution text, resolutionDate timestamp without time zone , changelog integer[], timeestimate integer, timeoriginalestimate integer, timespent integer);\n")
k.write("CREATE TABLE users (id integer PRIMARY KEY, name text, key text);\n")
k.write("CREATE TABLE projects (id integer PRIMARY KEY, name text, key text, type text);\n")
k.write("CREATE TABLE status (id integer PRIMARY KEY, name text);\n")
k.write("CREATE TABLE sprints (idSprint integer PRIMARY KEY, id integer, rapidViewid integer, state text, startDate timestamp without time zone, endDate timestamp without time zone, completedDate timestamp without time zone, activatedDate timestamp without time zone, sequence integer, goal text);\n")
k.write("CREATE TABLE changelog (id integer PRIMARY KEY, idOutput integer, field text, author text, fromI text, fromString text, toI text, toString text, date timestamp without time zone );\n")


sqlStatement, sqlUsers, sqlProject, sqlStatus, sqlSprints, sqlChangelog = '', '', '', '', '', ''
Users, Projects, Status, Sprints = [], [], [], []
changelogInc = 0
idOutput = 0
userExist = False
for json in jsondata:
    keylist = "("
    valuelist = "("
    firstPair = True
    for key, value in json.items():
        if key == "id":
            idOutput = value
        if not firstPair:
            keylist += ", "
            valuelist += ", "
        firstPair = False
        keylist += key
        if type(value) in (bytes, str):
            if value == '':
                valuelist += 'NULL' 
            elif has_symbol(value,"\u0027"):
                valuelist += "'" + value.replace("\u0027","''") + "'"
            elif is_date(value):
                value = value.replace("T", " ").split(".")[0]
                valuelist += "'" + str(value) + "'"
            else:
                valuelist += "'" + value + "'"
        elif isinstance(value,dict):
            new_value = replace(value)
            valuelist += new_value["id"]
            if key == "assignee" or key == "creator" or key == "reporter":
                if (elementExist(Users,new_value["id"]) == False and new_value["id"]!='NULL'):
                    Users.append(new_value["id"])
                    sqlUsers = "INSERT INTO users (id, name, key) VALUES (" + new_value["id"]+ ", '" + new_value["name"] + "', '" + new_value["key"] + "');\n"
            elif key == "project":
                if elementExist(Projects,new_value["id"]) == False:
                    Projects.append(new_value["id"])
                    sqlProject = "INSERT INTO projects (id, name, key, type) VALUES (" + new_value["id"]+ ", '" + new_value["name"] + "', '" + new_value["key"] + "', '" + new_value["type"] +"');\n"
            elif key == "status":
                if (elementExist(Status,new_value["id"]) == False and new_value["id"] != 'NULL'):
                    Status.append(new_value["id"])
                    sqlStatus = "INSERT INTO status (id, name) VALUES (" + new_value["id"]+ ", '" + new_value["name"] + "');\n"
        elif isinstance(value,list):
            if key == "sprints":
                valuelist += "'{"
                for s, item in enumerate(value):
                    item = replace(item)
                    if(elementExist(Sprints,item["id"]) == False and item["id"] != 'NULL'):
                        Sprints.append(item["id"])
                        nameStr = item["value"].replace('[', ';').replace('];',';')
                        valuesStr = nameStr.split(';')
                        sprintID = ""
                        sprintValue = ""
                        r = 1
                        while r < (len(valuesStr)-1):
                            elementR = valuesStr[r].split('=')
                            if r == 1:
                                sprintID = str(elementR[0])
                                sprintValue =  "'" + str(elementR[1]) + "'"
                            else:
                                sprintID += ", " + str(elementR[0]) + ""
                                if elementR[1] == '' or elementR[1] == "<null>":
                                    sprintValue += ", " + 'NULL'
                                elif is_date(elementR[1]):
                                    dateS = elementR[1].replace("T", " ").split(".")[0]
                                    sprintValue += ", '" + dateS + "' "
                                else:
                                    sprintValue += ", '" + str(elementR[1]) + "'"
                            r = r + 1
                        
                        sqlSprints += "INSERT INTO sprints (idSprint, " + sprintID + ") VALUES (" + str(item["id"]) + ", " + sprintValue + ");\n"
                    if s:
                        valuelist += ", " + str(item["id"])
                    else:
                        valuelist += str(item["id"])
                valuelist += "}'"
            elif key == "changelog":
                valuelist += "'{"
                for n, change in enumerate(value):
                    new_change = replace(change)
                    changelogInc = changelogInc + 1
                    if new_change["date"] != 'NULL':
                        date = new_change["date"].replace("T", " ").split(".")[0]
                    sqlChangelog += "INSERT INTO changelog (id, idOutput ,field, author, fromI, fromString, toI, toString, date) VALUES (" + str(changelogInc) + ", " + idOutput + ", '" + new_change["field"] + "', '" + new_change["author"] + "', '" + new_change["from"] + "', '" + new_change["fromString"] + "', '" + new_change["to"] + "', '" + new_change["toString"] +"', '"+ date +"');\n"
                    if n:
                        valuelist += ", " + str(changelogInc)
                    else:
                        valuelist += str(changelogInc)
                valuelist += "}'"
        else:
            if value == "":
                value = 'NULL'
            valuelist += str(value)
    keylist += ")"
    valuelist += ")"
    sqlStatement = "INSERT INTO output " + keylist + " VALUES " + valuelist + ";\n"
    k.write(sqlStatement)
    k.write(sqlUsers)
    k.write(sqlProject)
    k.write(sqlStatus)
    k.write(sqlSprints)
    k.write(sqlChangelog)
    sqlStatement, sqlUsers, sqlProject, sqlStatus, sqlSprints, sqlChangelog = '', '', '', '', '', ''

k.close()

