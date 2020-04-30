#!/usr/bin/env python3
import psycopg2
import datetime
import statistics
from scipy.stats import sem, t
import matplotlib.pyplot as plt
import numpy as np


try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="issues")
   cursor = connection.cursor()

   ####################### Duration ##########################


   # cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'In Progress' AND b.toString = 'Done' INNER JOIN output ON output.id = a.idOutput")
   # start = cursor.fetchall() 
   # cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'Done' AND b.toString = 'In Progress' INNER JOIN output ON output.id = a.idOutput")
   # finish = cursor.fetchall() 
   # start= [i[0] for i in start]
   # finish = [n[0] for n in finish]
   # diff = [x2 - x1 for (x1, x2) in zip(start, finish)] 
   # ts = []
   # for x in resolution:
   #  if(x.total_seconds() > 600 and x.total_seconds() < 15778462.98):
   #       ts.append(x.total_seconds())


   ###########################################################

   ################# TAKT TIME #######################
   
   cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL")
   resolution = cursor.fetchall() 
   resolution= [i[0] for i in resolution]
   resolution.sort()
   ts = []
   l = 0
   while l < len(resolution)-1:
      timeInt = resolution[l + 1] - resolution[l]
      if(timeInt.total_seconds() < 15778462.98):
         ts.append(timeInt.total_seconds())
      l += 1


   ####################################################

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

   std_err = sem(ts)
   interval = std_err * t.ppf((1 + 0.95) / 2. , len(ts) - 1)
   lb = med - interval
   ub = med + interval

   interval = datetime.timedelta(seconds=interval)
   interval = interval - datetime.timedelta(microseconds=interval.microseconds)
   print("Interval:", interval)




################################# Monte Carlo ###################################
   # num_reps = 500
   # num_sim = 1000
         
   # all_med = []
   # all_dev = []
   # for s in range(num_sim):
   #    target = np.random.normal(med, sDev, num_reps).round(2)
   #    new_target = []
   #    for j in target:
   #       if j > 600:
   #          new_target.append(j)
   #    md = statistics.median(new_target)
   #    sErr = sem(new_target)
   #    deviation = sErr * t.ppf((1 + 0.95) / 2. , len(new_target) - 1)
   #    all_med.append(md/86400)
   #    all_dev.append(deviation/86400)  
   # plt.hist(all_med)
   # plt.axvline(statistics.median(all_med), color='k', linestyle='dashed', linewidth=1)
   # min_ylim, max_ylim = plt.ylim()
   # plt.text(statistics.median(all_med)*1.1, max_ylim*0.9, 'Mean: {:.2f}'.format(statistics.median(all_med)))
   # plt.show()
   

#################################################################################

   # fig1, ax1 = plt.subplots()
   # ax1.set_title('Data Plot')
   # ax1.boxplot(ts)
   # plt.show()



except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)

finally:
    #closing database connection.
 if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
