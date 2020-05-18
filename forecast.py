#!/usr/bin/env python3
import psycopg2
import datetime
import statistics
from scipy.stats import sem, t
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
   return validation

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
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'In Progress' AND b.toString = 'Done' INNER JOIN output ON output.id = a.idOutput") # AND output.timeestimate IS NOT NULL")
   validationStart = cursor.fetchall() 
   cursor.execute("SELECT a.date FROM changelog a INNER JOIN changelog b ON a.idOutput = b.idOutput AND a.toString = 'Done' AND b.toString = 'In Progress' INNER JOIN output ON output.id = a.idOutput") # AND output.timeestimate IS NOT NULL")
   validationFinish = cursor.fetchall() 
   #cursor.execute("SELECT a.timeestimate FROM output a INNER JOIN changelog b ON a.id = b.idOutput AND b.toString = 'In Progress' INNER JOIN changelog c ON a.id = c.idOutput AND c.toString = 'Done' AND b.idOutput = c.idOutput AND a.timeestimate IS NOT NULL")
   #estimations = cursor.fetchall()
   cursor.execute("SELECT a.project FROM output a INNER JOIN changelog b ON a.id = b.idOutput AND b.toString = 'In Progress' INNER JOIN changelog c ON a.id = c.idOutput AND c.toString = 'Done' AND b.idOutput = c.idOutput") # AND a.timeestimate IS NOT NULL")
   idList = cursor.fetchall()
   validationStart= [vs[0] for vs in validationStart]
   validationFinish = [vf[0] for vf in validationFinish]
   #estimations = [e[0] for e in estimations]
   idList = [il[0] for il in idList]
   validationDiff = [x2 - x1 for (x1, x2) in zip(validationStart, validationFinish)] 
   validation = []
   #validationEstimations = []
   idProject = []
   resolutionDates = []
   for index, x in enumerate(validationDiff):
      if(x.total_seconds() > 600 and x.total_seconds() < 4320000): #and estimations[index] != 0):
         validation.append(x.total_seconds())
         #validationEstimations.append(estimations[index])
         idProject.append(idList[index])
         resolutionDates.append(validationFinish[index])

   return [validation, idProject, resolutionDates]

def durationProj(element, idProject, resolutionDates):

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
      #if(x.total_seconds() > 300 and x.total_seconds() < 4320000):
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
   rem = int(0.05 * len(target)) 
   if(rem > 0):
      target = target[rem:-rem]  # Remove 5% on each end of the ordered list 
   md = statistics.median(target)
   mn = statistics.mean(target)
   lower = min(target)
   upper = max(target)

   return [md, mn, lower, upper]

def durationPrints(lower, upper, idProject, actualValue):

   upperEstimation = datetime.timedelta(seconds=upper)
   upperEstimation = upperEstimation - datetime.timedelta(microseconds=upperEstimation.microseconds)
   bottomEstimation = datetime.timedelta(seconds=lower)
   bottomEstimation = bottomEstimation - datetime.timedelta(microseconds=bottomEstimation.microseconds)


   rangeEstimation = "[" + str(bottomEstimation) + " -- " + str(upperEstimation) + "]"

   print("ID:" + str(idProject))
   # originalEstimation = datetime.timedelta(seconds=validationEstimations[int(element)])
   # originalEstimation = originalEstimation - datetime.timedelta(microseconds=originalEstimation.microseconds)


   realValue = datetime.timedelta(seconds=actualValue)
   realValue = realValue - datetime.timedelta(microseconds=realValue.microseconds)

   #print("Original Estimation: " + str(originalEstimation))
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
      validation = taktTimeValidation(idProject)
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


def takttimeLastElement():
   idProject = taktTimeRandProj()  #Select a random project
   project = taktTimeValidation(idProject)  #Select all the stories form that project
   num = int(0.5 * len(project))  #Divide the project in two
   ts = project[:num]  #First Half
   validation = project[-int(len(project) - num):]  #Second Half
   y_axis_historical = []
   y_axis_forecast = []
   y = 1
   while y <= num:
      y_axis_historical.append(y)   #Prepare the y_axis with the stories numbers
      y = y + 1
   y_axis_forecast.append(num)
   while y <= len(project):
      y_axis_forecast.append(y)
      y = y + 1
   f,t = 0, 0
   sum_ts = 0
   ts_sum = []
   while t < len(ts):
      sum_ts = sum_ts + ts[t]/3600        # Generate the X axis values for the historic data (1st half)
      ts_sum.append(sum_ts)
      t = t + 1
   sum_val = sum_ts
   medianForecast, meanForecast, lowerForecast, upperForecast = 0, 0, 0, 0
   med_sum, mn_sum, upper_sum, lower_sum, val_sum = [sum_ts], [sum_ts], [sum_ts], [sum_ts], [sum_ts]
   while f < int(len(project) - num):
      taktTimeMC = monteCarlo(ts, (f+1))
      medianForecast = sum_ts + taktTimeMC[0]/3600
      meanForecast = sum_ts + taktTimeMC[1]/3600
      lowerForecast = sum_ts + taktTimeMC[2]/3600
      upperForecast = sum_ts + taktTimeMC[3]/3600   
      med_sum.append(medianForecast)
      mn_sum.append(meanForecast)
      upper_sum.append(upperForecast)
      lower_sum.append(lowerForecast)
      sum_val = sum_val + validation[f]/3600
      val_sum.append(sum_val)
      f = f + 1

   #Generate the Graph
   plt.plot(ts_sum, y_axis_historical, color='green', linestyle='solid', linewidth = 2, marker='o', markerfacecolor='blue', markersize=2, label = "Historical Data")
   plt.plot(med_sum, y_axis_forecast, color='yellow', linestyle='solid', linewidth = 2, marker='o', markerfacecolor='blue', markersize=2, label = "Median")
   plt.plot(mn_sum, y_axis_forecast, color='gray', linestyle='solid', linewidth = 2, marker='o', markerfacecolor='blue', markersize=2, label = "Mean")
   plt.plot(lower_sum, y_axis_forecast, color='red', linestyle='solid', linewidth = 2, marker='o', markerfacecolor='blue', markersize=2, label = "Optimist")
   plt.plot(upper_sum, y_axis_forecast, color='orange', linestyle='solid', linewidth = 2, marker='o', markerfacecolor='blue', markersize=2, label = "Pessimist")
   plt.plot(val_sum, y_axis_forecast, color='purple', linestyle='solid', linewidth = 2, marker='o', markerfacecolor='blue', markersize=2, label = "Real Values")
   plt.xlabel('Time (h)') 
   plt.ylabel('Stories') 
   plt.title('Time To Complete Story') 
   plt.legend() 
   plt.show() 


try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="issues")
   cursor = connection.cursor()

   ################## TaktTime ###################

   # idProject = taktTimeRandProj()
   # validation = taktTimeValidation(idProject)
   # ts = taktTimeProj(idProject)
   # taktTimeMC = monteCarlo(ts, 1)
   # md = taktTimeMC[0]
   # lower = taktTimeMC[2]
   # upper = taktTimeMC[3]
   # actualValue = statistics.mean(validation)
   # taktTimePrints(lower,upper,idProject,actualValue)

   ###############################################

   ################# Duration ####################

   # durationValidation = durationValidation()
   # validation = durationValidation[0]
   # idProject = durationValidation[1]
   # resolutionDates = durationValidation[2]
   # element = np.random.randint(low=0, high=len(idProject))
   # ts = durationProj(element, idProject, resolutionDates)
   # durationMC = monteCarlo(ts, 1)
   # md = durationMC[0]
   # lower = durationMC[2]
   # upper = durationMC[3]
   # actualValue = validation[int(element)]
   # durationPrints(lower, upper, idProject[int(element)], actualValue)


   ###############################################

   ################# Errors ######################

   #percentageError(actualValue, lower, upper)

   ###############################################

   ############# Mean Square Error ############

   #durationRMSE()
   #takttimeRMSE()

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
