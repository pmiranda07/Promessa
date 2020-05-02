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


   ################### Validation ##################################################

   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'In Progress' AND b.toString = 'Done' INNER JOIN output ON output.id = a.idOutput AND output.timeestimate IS NOT NULL")
   validationStart = cursor.fetchall() 
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'Done' AND b.toString = 'In Progress' INNER JOIN output ON output.id = a.idOutput AND output.timeestimate IS NOT NULL")
   validationFinish = cursor.fetchall() 
   cursor.execute("SELECT a.timeestimate FROM output a INNER JOIN changelog b ON a.id = b.idOutput AND b.toString = 'In Progress' INNER JOIN changelog c ON a.id = c.idOutput AND c.toString = 'Done' AND b.idOutput = c.idOutput AND a.timeestimate IS NOT NULL")
   estimations = cursor.fetchall()
   cursor.execute("SELECT a.project FROM output a INNER JOIN changelog b ON a.id = b.idOutput AND b.toString = 'In Progress' INNER JOIN changelog c ON a.id = c.idOutput AND c.toString = 'Done' AND b.idOutput = c.idOutput AND a.timeestimate IS NOT NULL")
   idList = cursor.fetchall()
   validationStart= [vs[0] for vs in validationStart]
   validationFinish = [vf[0] for vf in validationFinish]
   estimations = [e[0] for e in estimations]
   idList = [il[0] for il in idList]
   validationDiff = [x2 - x1 for (x1, x2) in zip(validationStart, validationFinish)] 
   validation = []
   validationEstimations = []
   idProject = []
   resolutionDates = []
   for index, x in enumerate(validationDiff):
      if(x.total_seconds() > 600 and x.total_seconds() < 2629743 and estimations[index] != 0):
         validation.append(x.total_seconds())
         validationEstimations.append(estimations[index])
         idProject.append(idList[index])
         resolutionDates.append(validationFinish[index])
   
   element = np.random.randint(low=0, high=len(validationEstimations))

   ##################################################################################

   ####################### Duration ##########################


   #cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'In Progress' AND b.toString = 'Done' INNER JOIN output ON output.id = a.idOutput")
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'In Progress' AND b.toString = 'Done' INNER JOIN output ON output.id = a.idOutput AND output.project=" + str(idProject[int(element)]))
   start = cursor.fetchall() 
   #cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'Done' AND b.toString = 'In Progress' INNER JOIN output ON output.id = a.idOutput")
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'Done' AND b.toString = 'In Progress' INNER JOIN output ON output.id = a.idOutput AND output.project=" + str(idProject[int(element)]))
   finish = cursor.fetchall() 
   start= [i[0] for i in start]
   finish = [n[0] for n in finish]
   diff = [x2 - x1 for (x1, x2) in zip(start, finish)] 
   ts = []
   for ind, x in enumerate(diff):
      if(x.total_seconds() > 600 and x.total_seconds() < 2629743):
      #if(x.total_seconds() > 600 and x.total_seconds() < 2629743 and finish[int(ind)] < resolutionDates[int(element)]):
         ts.append(x.total_seconds())

   if(len(ts) < 2):
      raise Exception(": Not enough data")

   ###########################################################

   ################# TAKT TIME #######################
   
   # cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL")
   # resolution = cursor.fetchall() 
   # resolution= [i[0] for i in resolution]
   # resolution.sort()
   # ts = []
   # l = 0
   # while l < len(resolution)-1:
   #    timeInt = resolution[l + 1] - resolution[l]
   #    if(timeInt.total_seconds() < 2629743):
   #       ts.append(timeInt.total_seconds())
   #    l += 1


   ####################################################

   avg = statistics.mean(ts)
   var = statistics.pvariance(ts)
   sDev = statistics.pstdev(ts)
   med = statistics.median(ts)

   # mean = datetime.timedelta(seconds=avg)
   # mean = mean - datetime.timedelta(microseconds=mean.microseconds)
   # print("Mean:", mean)



   # stdev = datetime.timedelta(seconds=sDev)
   # stdev = stdev - datetime.timedelta(microseconds=stdev.microseconds)
   # print("STD Deviation:", stdev)
   

   # median = datetime.timedelta(seconds=med)
   # median = median - datetime.timedelta(microseconds=median.microseconds)
   # print("Median:", median)

   # std_err = sem(ts)
   # interval = std_err * t.ppf((1 + 0.95) / 2. , len(ts) - 1)
   # lb = med - interval
   # ub = med + interval

   # interval = datetime.timedelta(seconds=interval)
   # interval = interval - datetime.timedelta(microseconds=interval.microseconds)
   # print("Interval:", interval)




################################# Monte Carlo ###################################
   num_reps = 500
   num_sim = 1000
         
   all_med = []
   all_dev = []
   for s in range(num_sim):
      target = np.random.normal(med, sDev, num_reps).round(2)
      new_target = []
      for j in target:
         if j > 600:
            new_target.append(j)
      md = statistics.median(new_target)
      sErr = sem(new_target)
      deviation = sErr * t.ppf((1 + 0.95) / 2. , len(new_target) - 1)
      all_med.append(md)
      all_dev.append(deviation)

   estimationMean = statistics.median(all_med)
   estimationInterval = statistics.median(all_dev)


   upperEstimation = estimationMean + estimationInterval
   bottomEstimation = estimationMean - estimationInterval
   upperEstimation = datetime.timedelta(seconds=upperEstimation)
   upperEstimation = upperEstimation - datetime.timedelta(microseconds=upperEstimation.microseconds)
   bottomEstimation = datetime.timedelta(seconds=bottomEstimation)
   bottomEstimation = bottomEstimation - datetime.timedelta(microseconds=bottomEstimation.microseconds)


   rangeEstimation = "[" + str(bottomEstimation) + " -- " + str(upperEstimation) + "]"


   # plt.hist(all_med)
   # plt.axvline(statistics.median(all_med), color='k', linestyle='dashed', linewidth=1)
   # min_ylim, max_ylim = plt.ylim()
   # plt.text(statistics.median(all_med)*1.1, max_ylim*0.9, 'Mean: {:.2f}'.format(statistics.median(all_med)))
   # plt.show()
   

   #################################################################################
   
   
   
   ########################## Print Values ########################################
   
   originalEstimation = datetime.timedelta(seconds=validationEstimations[int(element)])
   originalEstimation = originalEstimation - datetime.timedelta(microseconds=originalEstimation.microseconds)

   realValue = datetime.timedelta(seconds=validation[int(element)])
   realValue = realValue - datetime.timedelta(microseconds=realValue.microseconds)

   print("Original Estimation: " + str(originalEstimation))
   print("Real Value: " + str(realValue))
   print("Model Estimation: " + str(rangeEstimation))


##################################################################################



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
