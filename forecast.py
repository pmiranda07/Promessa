#!/usr/bin/env python3
import psycopg2
import datetime
import statistics
from scipy.stats import sem, t
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import numpy as np



def taktTimeRandProj():

   #cursor.execute("SELECT project FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(MONTH FROM resolutionDate) = 12 AND EXTRACT(YEAR FROM resolutionDate) = 2019")
   cursor.execute("SELECT project FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(YEAR FROM resolutionDate) = 2019") # For the last element Forecast
   idList = cursor.fetchall()
   idList = [il[0] for il in idList]
   project = np.random.choice(idList)
   return project

def taktTimeValidation(project):
   
   #cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(MONTH FROM resolutionDate) = 12 AND EXTRACT(YEAR FROM resolutionDate) = 2019 AND project =" + str(project))
   cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(YEAR FROM resolutionDate) = 2019 AND project =" + str(project))  # For the last element Forecast
   validationFinish = cursor.fetchall() 
   validationFinish = [vf[0] for vf in validationFinish]
   validationFinish.sort()
   validation = []
   l = 0
   while l < len(validationFinish)-1:
      timeInt = validationFinish[l + 1] - validationFinish[l]
      if(timeInt.total_seconds() > 300 and timeInt.total_seconds() < 200000):
         validation.append(timeInt.total_seconds())
      l += 1
   print(len(validation))
   return [validation, validationFinish[0]]

def getProjSprintsDates(project):
   cursor.execute("SELECT a.endDate FROM sprints a INNER JOIN output b ON a.idSprint = ANY(b.sprints) AND b.project =" + str(project))
   sprints = cursor.fetchall() 
   sprints = [sp[0] for sp in sprints]
   sprints.sort()

   return sprints


def taktTimeProj(project):

   cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(MONTH FROM resolutionDate) = 12 AND EXTRACT(YEAR FROM resolutionDate) < 2019 AND project =" + str(project))
   resolution = cursor.fetchall() 
   resolution= [i[0] for i in resolution]
   resolution.sort()
   ts = []
   l = 0
   while l < len(resolution)-1:
      timeInt = resolution[l + 1] - resolution[l]
      if(timeInt.total_seconds() > 300 and timeInt.total_seconds() < 200000):
         ts.append(timeInt.total_seconds())
      l += 1

   if(len(ts) < 2):
      raise Exception(": Not enough data")

   return ts


def taktTimePrints(lower, upper, idProject, actualValue):
   upperEstimation = datetime.timedelta(seconds=upper)
   upperEstimation = upperEstimation - datetime.timedelta(microseconds=upperEstimation.microseconds)
   bottomEstimation = datetime.timedelta(seconds=lower)
   bottomEstimation = bottomEstimation - datetime.timedelta(microseconds=bottomEstimation.microseconds)


   rangeEstimation = "[" + str(bottomEstimation) + " -- " + str(upperEstimation) + "]"


   print("Project ID:" + str(idProject))
   realValue = datetime.timedelta(seconds=actualValue)
   realValue = realValue - datetime.timedelta(microseconds=realValue.microseconds)

   print("Real Value: " + str(realValue))
   print("Model Estimation: " + str(rangeEstimation))


def durationValidation():
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN output b ON a.id = ANY(b.changelog) AND a.toString = 'In Progress' INNER JOIN changelog c ON c.id = ANY(b.changelog) AND c.toString = 'Done'") #AND b.timeestimate IS NOT NULL")
   validationStart = cursor.fetchall() 
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN output b ON a.id = ANY(b.changelog) AND a.toString = 'Done' INNER JOIN changelog c ON c.id = ANY(b.changelog) AND c.toString = 'In Progress'") #AND b.timeestimate IS NOT NULL")
   validationFinish = cursor.fetchall() 
   # cursor.execute("SELECT a.timeestimate FROM output a INNER JOIN changelog b ON b.id = ANY(a.changelog) AND b.toString = 'In Progress' INNER JOIN changelog c ON c.id = ANY(a.changelog) AND c.toString = 'Done' AND a.timeestimate IS NOT NULL")
   # estimations = cursor.fetchall()
   cursor.execute("SELECT a.project FROM output a INNER JOIN changelog b ON b.id = ANY(a.changelog) AND b.toString = 'In Progress' INNER JOIN changelog c ON c.id = ANY(a.changelog) AND c.toString = 'Done'") # AND a.timeestimate IS NOT NULL")
   idList = cursor.fetchall()
   validationStart= [vs[0] for vs in validationStart]
   validationFinish = [vf[0] for vf in validationFinish]
   #estimations = [e[0] for e in estimations]
   idList = [il[0] for il in idList]
   validationDiff = [x2 - x1 for (x1, x2) in zip(validationStart, validationFinish)] 
   validation = []
   validationEstimations = []
   idProject = []
   resolutionDates = []
   for index, x in enumerate(validationDiff):
      if(x.total_seconds() > 600 and x.total_seconds() < 4320000): # and estimations[index] != 0):
         validation.append(x.total_seconds())
         #validationEstimations.append(estimations[index])
         idProject.append(idList[index])
         resolutionDates.append(validationFinish[index])

   return [validation, idProject, validationEstimations, resolutionDates]

def durationProj(element, idProject, resolutionDates):

   cursor.execute("SELECT a.date FROM changelog a INNER JOIN output b ON a.id = ANY(b.changelog) AND a.toString = 'In Progress' INNER JOIN changelog c ON c.id = ANY(b.changelog) AND c.toString = 'Done' AND b.project=" + str(idProject[int(element)]))
   start = cursor.fetchall() 
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN output b ON a.id = ANY(b.changelog) AND a.toString = 'Done' INNER JOIN changelog c ON c.id = ANY(b.changelog) AND c.toString = 'In Progress' AND b.project=" + str(idProject[int(element)]))
   finish = cursor.fetchall() 
   start= [i[0] for i in start]
   finish = [n[0] for n in finish]
   diff = [x2 - x1 for (x1, x2) in zip(start, finish)] 
   ts = []
   for ind, x in enumerate(diff):
      if(x.total_seconds() > 300 and x.total_seconds() < 4320000 and finish[int(ind)] < resolutionDates[int(element)]):
         ts.append(x.total_seconds())
   if(len(ts) < 2):
      raise Exception(": Not enough data")
   
   return ts

def monteCarlo(ts, nTasks):
   num_reps = 500  
   target = []
   r, b = 0, 0
   obj = 0
   while r < num_reps: 
      while b < nTasks:
         obj = obj + np.random.choice(ts) #Select a random duration/Takt time from the historic data
         b = b + 1
      target.append(obj)
      r = r + 1
      b = 0
      obj = 0
   target.sort()   # Order the durations/ Takt Time
   rem = int(0.025 * len(target)) 
   mn = statistics.mean(target)
   if(rem > 0):
      target = target[rem:-rem]  # Remove % on each end of the ordered list 
   md = statistics.median(target)
   lower = min(target)
   upper = max(target)

   return [md, mn, lower, upper]

def durationPrints(lower, upper, idProject, actualValue, estimation):

   upperEstimation = datetime.timedelta(seconds=upper)
   upperEstimation = upperEstimation - datetime.timedelta(microseconds=upperEstimation.microseconds)
   bottomEstimation = datetime.timedelta(seconds=lower)
   bottomEstimation = bottomEstimation - datetime.timedelta(microseconds=bottomEstimation.microseconds)


   rangeEstimation = "[" + str(bottomEstimation) + " -- " + str(upperEstimation) + "]"

   print("ID:" + str(idProject))
   # originalEstimation = datetime.timedelta(seconds=estimation)
   # originalEstimation = originalEstimation - datetime.timedelta(microseconds=originalEstimation.microseconds)


   realValue = datetime.timedelta(seconds=actualValue)
   realValue = realValue - datetime.timedelta(microseconds=realValue.microseconds)

   # print("Original Estimation: " + str(originalEstimation))
   print("Real Value: " + str(realValue))
   print("Model Estimation: " + str(rangeEstimation))

def percentageError(actualValue, bottomEstimation, upperEstimation):
   if(actualValue > upperEstimation):
      percentageError = (actualValue - upperEstimation)/actualValue * 100
   elif(actualValue < bottomEstimation):
      percentageError = (abs(actualValue - bottomEstimation))/actualValue * 100
   elif(actualValue < upperEstimation and actualValue > bottomEstimation):
      percentageError = 0
   print("Percentage Error: " + str(int(percentageError)) + "%")

def durationRMSE():
   durValidation = durationValidation()
   validation = durValidation[0]
   idProject = durValidation[1]
   resolutionDates = durValidation[2]
   num_sims = 5
   y_forecast = []
   y_true = []
   s = 0
   while s < num_sims:
      element = np.random.randint(low=0, high=len(idProject))
      ts = durationProj(element, idProject , resolutionDates)
      durationMc = monteCarlo(ts, 1)
      lower = durationMc[1]
      upper = durationMc[2]
      actualValue = validation[int(element)]
      if(actualValue > upper):
         y_forecast.append(upper)
      elif(actualValue < lower):
         y_forecast.append(lower)
      elif(actualValue >= lower and actualValue <= upper):
         y_forecast.append(actualValue)
      y_true.append(actualValue)
      s = s + 1
   mse = np.square(abs(np.subtract(y_true,y_forecast))).mean() 
   rmse = np.sqrt(mse)
   print("RMSE: " + str(rmse))

def takttimeRMSE():
   s = 0
   num_sims = 5
   y_forecast = []
   y_true = []
   while s < num_sims:
      idProject = taktTimeRandProj()
      validationFunc = taktTimeValidation(idProject)
      validation = validationFunc[0]
      ts = taktTimeProj(idProject)
      takttimeMC = monteCarlo(ts, 1)
      lower = takttimeMC[1]
      upper = takttimeMC[2]
      actualValue = statistics.mean(validation)
      if(actualValue > upper):
         y_forecast.append(upper)
      elif(actualValue < lower):
         y_forecast.append(lower)
      elif(actualValue >= lower and actualValue <= upper):
         y_forecast.append(actualValue)
      y_true.append(actualValue)
      s = s + 1 
   mse = np.square(np.subtract(y_true,y_forecast)).mean()
   rmse = np.sqrt(mse)
   print("RMSE: " + str(rmse))

def getTaktTimeForecast():
   idProject = taktTimeRandProj()
   validationFunc = taktTimeValidation(idProject)
   validation = validationFunc[0]
   ts = taktTimeProj(idProject)
   taktTimeMC = monteCarlo(ts, 1)
   lower = taktTimeMC[2]
   upper = taktTimeMC[3]
   actualValue = statistics.mean(validation)
   taktTimePrints(lower,upper,idProject,actualValue)
   percentageError(actualValue, lower, upper)

def getDurationForecast():
   durationValidationF = durationValidation()
   validation = durationValidationF[0]
   idProject = durationValidationF[1]
   validationEstimations = durationValidationF[2]
   resolutionDates = durationValidationF[3]
   element = np.random.randint(low=0, high=len(idProject))
   ts = durationProj(element, idProject, resolutionDates)
   durationMC = monteCarlo(ts, 1)
   lower = durationMC[2]
   upper = durationMC[3]
   actualValue = validation[int(element)]
   durationPrints(lower, upper, idProject[int(element)], actualValue, validationEstimations)
   #durationPrints(lower, upper, idProject[int(element)], actualValue, validationEstimations[element])
   percentageError(actualValue, lower, upper)

def readInput():
   print("How many tasks?")
   nTasks = int(input())

   return nTasks

def takttimeLastElement():
   idProject = taktTimeRandProj()  #Select a random project
   validationFunc = taktTimeValidation(idProject)  #Select all the stories from that project
   project = validationFunc[0]
   firstelement = validationFunc[1]
   sprints = getProjSprintsDates(idProject)
   num = int(0.5 * len(project))  #Divide the project in two
   ts = project[:num]  #First Half
   validation = project[-int(len(project) - num):]  #Second Half
   nTasks = readInput()
   y_axis_historical = []
   y_axis_forecast = []
   y_axis_validation = []
   y = 1
   while y <= num:
      y_axis_historical.append(y)   #Prepare the y_axis with the stories numbers
      y = y + 1
   y_axis_forecast.append(num)
   y_axis_validation.append(num)
   yv = y
   while yv <= len(project):
      y_axis_validation.append(yv)
      yv = yv + 1
   if(nTasks == 0):
      forecastLen = len(project)
      nTasks = int(len(project) - num)
   else:
      forecastLen = y+nTasks - 1
   while y <= forecastLen:
      y_axis_forecast.append(y)
      y = y + 1
   f,t,v = 0, 0, 0
   sum_ts = firstelement
   ts_sum = []
   while t < len(ts):
      sum_ts = sum_ts + datetime.timedelta(seconds = ts[t])       # Generate the X axis values for the historic data (1st half)
      ts_sum.append(sum_ts)
      t = t + 1
   sum_val = sum_ts
   error_val = sum_ts - firstelement
   val_error = [error_val]
   medianForecast, lowerForecast, upperForecast = 0, 0, 0
   med_sum, val_sum = [sum_ts], [sum_ts]
   upper_sum, lower_sum = [], []
   while f < nTasks:
      taktTimeMC = monteCarlo(ts, (f+1))
      medianForecast = sum_ts + datetime.timedelta(seconds = taktTimeMC[0])
      lowerForecast = sum_ts + datetime.timedelta(seconds = taktTimeMC[2])
      upperForecast = sum_ts + datetime.timedelta(seconds = taktTimeMC[3])   
      med_sum.append(medianForecast)
      upper_sum.append(upperForecast)
      lower_sum.append(lowerForecast)
      f = f + 1
   while v < int(len(project) - num):
      sum_val = sum_val + datetime.timedelta(seconds = validation[v])
      error_val = error_val + datetime.timedelta(seconds = validation[v])
      val_sum.append(sum_val)
      val_error.append(error_val)
      v = v + 1
   errorLen = min(len(val_sum), len(med_sum))
   eL = 1
   error_sum = []
   while eL < errorLen:
      pe = (abs(val_sum[eL] - med_sum[eL]))/val_error[eL] * 100
      error_sum.append(pe)
      eL = eL + 1
   lu,li = 0,0
   while lu < len(upper_sum):
      lower_sum[lu] = (lower_sum[lu] - firstelement).total_seconds()
      upper_sum[lu] = (upper_sum[lu] - firstelement).total_seconds()
      lu = lu + 1
   lower_sum = list(savgol_filter(lower_sum, 51, 3, mode="nearest"))
   upper_sum = list(savgol_filter(upper_sum,51,3,  mode="nearest"))
   while li < len(upper_sum):
      lower_sum[li] = firstelement + datetime.timedelta(seconds = lower_sum[li])
      upper_sum[li] = firstelement + datetime.timedelta(seconds = upper_sum[li])
      li = li + 1
   lower_sum.insert(0,sum_ts)
   upper_sum.insert(0,sum_ts)

   sprints = [spr for spr in sprints if spr <= max(upper_sum)]
   sprints = [spt for spt in sprints if spt >= firstelement]
   sprints = list(dict.fromkeys(sprints))


   #Generate the Graph
   fig, ax1 = plt.subplots()
   ax2 = ax1.twinx()
   ax1.invert_yaxis()
   l1, = ax1.plot(ts_sum, y_axis_historical, color='green', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=2)
   l2, = ax1.plot(med_sum, y_axis_forecast, color='blue', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=2)
   l3, = ax1.plot(lower_sum, y_axis_forecast, color='brown', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=2)
   l4, = ax1.plot(upper_sum, y_axis_forecast, color='orange', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=2)
   l5, = ax1.plot(val_sum, y_axis_validation, color='purple', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=2)
   ax2.set_ylim([0,100])
   if len(sprints) == 0:
      plt.xticks([firstelement])
      plt.axvline(x=firstelement, color='red')
   else:
      plt.xticks(sprints)
      for xc in sprints:
         plt.axvline(x=xc, color='red')

   if(len(val_sum) > len(med_sum)):
      med_sum.pop(0)
      l6, = ax2.plot(med_sum, error_sum, color='black', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='white', markersize=2)
   else:
      val_sum.pop(0)
      l6, = ax2.plot(val_sum, error_sum, color='black', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='white', markersize=2)
   ax1.set_xlabel('Sprints') 
   ax1.set_ylabel('Stories') 
   ax2.set_ylabel('Error(%)') 
   plt.title('Time To Complete Story') 
   plt.legend(handles = [l1,l2,l3,l4,l5,l6], labels = ['Historical Data','Median','Optimist','Pessimist','Real Values','Error'], loc=2) 
   plt.show() 


try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="output_issues")
   cursor = connection.cursor()

   ################## TaktTime ###################

   # getTaktTimeForecast()

   ###############################################

   ################# Duration ####################

   # getDurationForecast()

   ###############################################

   ############# Mean Square Error ############

   # durationRMSE()
   # takttimeRMSE()

   ############################################

   ######## TaktTime till last element ########

   takttimeLastElement()

   ############################################

   ################# Graphs ######################



   # plt.hist(array)
   # plt.axvline(statistics.median(array), color='k', linestyle='dashed', linewidth=1)
   # min_ylim, max_ylim = plt.ylim()
   # plt.text(statistics.median(array)*1.1, max_ylim*0.9, 'Mean: {:.2f}'.format(statistics.median(array)))
   # plt.show()



   # fig1, ax1 = plt.subplots()
   # ax1.set_title('Data Plot')
   # ax1.boxplot(array)
   # plt.show()

   ################################################


except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)

finally:
    #closing database connection.
 if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
