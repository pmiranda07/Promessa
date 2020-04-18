#!/usr/bin/env python3
import psycopg2
import datetime
import statistics


try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="issues")
   cursor = connection.cursor()
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'In Progress' AND b.toString = 'Done' INNER JOIN output ON output.id = a.idOutput")
   start = cursor.fetchall() 
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'Done' AND b.toString = 'In Progress' INNER JOIN output ON output.id = a.idOutput")
   finish = cursor.fetchall() 
   start= [i[0] for i in start]
   finish = [n[0] for n in finish]
   diff = [x2 - x1 for (x1, x2) in zip(start, finish)] 
   ts = []
   for x in diff:
      if(x.total_seconds() > 300 and x.total_seconds() < 15778462.98):
         ts.append(x.total_seconds())

   
   avg = statistics.mean(ts)
   var = statistics.pvariance(ts)
   sDev = statistics.pstdev(ts)
   med = statistics.median(ts)


   mean = datetime.timedelta(seconds=avg)
   mean = mean - datetime.timedelta(microseconds=mean.microseconds)
   print("Mean:", mean)



   stdev = datetime.timedelta(seconds=sDev)
   stdev = stdev - datetime.timedelta(microseconds=stdev.microseconds)
   print("STD Deviation:", stdev)
   

   median = datetime.timedelta(seconds=med)
   median = median - datetime.timedelta(microseconds=median.microseconds)
   print("Median:", median)



except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)

finally:
    #closing database connection.
 if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
