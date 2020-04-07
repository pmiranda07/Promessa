#!/usr/bin/env python3
import psycopg2
import datetime
import statistics

print("Issue Priority?")
priority = input()
# print ("Issue Opened in")
# opened = input() 

try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="jira_dataset")
   cursor = connection.cursor()
   cursor.execute("SELECT created FROM jira_issue_report WHERE priority='" + priority + "' AND status!='Open' AND created IS NOT NULL")
   created = cursor.fetchall() 
   cursor.execute("SELECT resolved FROM jira_issue_report WHERE priority='" + priority + "' AND status!='Open' AND resolved IS NOT NULL")
   resolved = cursor.fetchall() 
   created= [i[0] for i in created]
   resolved = [n[0] for n in resolved]
   diff = [x2 - x1 for (x1, x2) in zip(created, resolved)] 
   ts = []
   for x in diff:
      ts.append(x.total_seconds())

   mean = datetime.timedelta(seconds=statistics.mean(ts))
   mean = mean - datetime.timedelta(microseconds=mean.microseconds)

   print(mean)
   #pvar = datetime.timedelta(seconds=statistics.pvariance(ts))
   #pvar = pstdev - datetime.timedelta(microseconds=pstdev.microseconds)

   


except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)

finally:
    #closing database connection.
 if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
