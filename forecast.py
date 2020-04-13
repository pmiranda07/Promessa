#!/usr/bin/env python3
import psycopg2
import datetime
import statistics

print("Issue Priority?")
priority = input()
# print ("Issue Opened in")
# opened = input() 

try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="issues")
   cursor = connection.cursor()
   cursor.execute("SELECT created FROM output WHERE priority='" + priority + "'  AND created IS NOT NULL AND resolutionDate IS NOT NULL")
   created = cursor.fetchall() 
   cursor.execute("SELECT resolutionDate FROM output WHERE priority='" + priority + "' AND resolutionDate IS NOT NULL AND created IS NOT NULL")
   resolved = cursor.fetchall() 
   created= [i[0] for i in created]
   resolved = [n[0] for n in resolved]
   diff = [x2 - x1 for (x1, x2) in zip(created, resolved)] 
   ts = []
   for x in diff:
      ts.append(x.total_seconds())


   avg = statistics.mean(ts)
   var = statistics.pvariance(ts)
   sDev = statistics.pstdev(ts)

   

   mean = datetime.timedelta(seconds=avg)
   mean = mean - datetime.timedelta(microseconds=mean.microseconds)
   print(mean)



   stdev = datetime.timedelta(seconds=sDev)
   stdev = stdev - datetime.timedelta(microseconds=stdev.microseconds)
   print(stdev)
   

   


except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)

finally:
    #closing database connection.
 if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
