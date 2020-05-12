#!/usr/bin/env python3
import psycopg2
import datetime
import statistics
from scipy.stats import sem, t
import matplotlib.pyplot as plt
import numpy as np



def taktTimeRandProj():

   cursor.execute("SELECT project FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(MONTH FROM resolutionDate) =12 AND EXTRACT(YEAR FROM resolutionDate) = 2019")
   idList = cursor.fetchall()
   idList = [il[0] for il in idList]
   project = np.random.choice(idList)
   return project

def taktTimeValidation(project):
   
   cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(MONTH FROM resolutionDate) = 12 AND EXTRACT(YEAR FROM resolutionDate) = 2019 AND project =" + str(project))
   validationFinish = cursor.fetchall() 
   validationFinish = [vf[0] for vf in validationFinish]
   validationFinish.sort()
   validation = []
   l = 0
   while l < len(validationFinish)-1:
      timeInt = validationFinish[l + 1] - validationFinish[l]
      if(timeInt.total_seconds() > 300 and timeInt.total_seconds() < 1728000 ):
         validation.append(timeInt.total_seconds())
      l += 1
   return validation

def taktTimeProj(project):

   cursor.execute("SELECT resolutionDate FROM output WHERE resolutionDate IS NOT NULL AND EXTRACT(MONTH FROM resolutionDate) < 12 AND EXTRACT(YEAR FROM resolutionDate) = 2019 AND project =" + str(project))
   resolution = cursor.fetchall() 
   resolution= [i[0] for i in resolution]
   resolution.sort()
   ts = []
   l = 0
   while l < len(resolution)-1:
      timeInt = resolution[l + 1] - resolution[l]
      if(timeInt.total_seconds() > 300 and timeInt.total_seconds() < 1728000):
         ts.append(timeInt.total_seconds())
      l += 1

   if(len(ts) < 2):
      raise Exception(": Not enough data")

   return ts


def taktTimeMC(ts):
   num_reps = 1000
   takt = []
   r = 0
   while r < num_reps:
      obj = np.random.choice(ts)
      takt.append(obj)
      r = r + 1
   md = statistics.mean(takt)
   deviation = sem(takt) * t.ppf((1 + 0.95) / 2. , len(takt) - 1)
   return [md,deviation]



def taktTimePrints(md, deviation, idProject, actualValue):
   upperEstimation = md + deviation
   bottomEstimation = md - deviation
   upperEstimation = datetime.timedelta(seconds=upperEstimation)
   upperEstimation = upperEstimation - datetime.timedelta(microseconds=upperEstimation.microseconds)
   bottomEstimation = datetime.timedelta(seconds=bottomEstimation)
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

def durationMC(ts):
   num_reps = 1000
   tf1 = []    # 0 - 5 Days
   tf2 = []    # 5 - 10 Days
   tf3 = []    # 10 - 15 Days
   tf4 = []    # > 15 Days
   r = 0
   while r < num_reps:
      obj = np.random.choice(ts)
      if(obj < 432000):
         tf1.append(obj)
      elif(obj >= 432000 and obj < 864000):
         tf2.append(obj)
      elif(obj >= 864000 and obj < 1296000):
         tf3.append(obj)
      elif(obj >= 1296000):
         tf4.append(obj)
      r = r + 1 
   md, deviation = 0, 0
   if(len(tf1) >= len(tf2) and len(tf1) >= len(tf3) and len(tf1) >= len(tf4)):
      md = statistics.mean(tf1)
      deviation = sem(tf1) * t.ppf((1 + 0.95) / 2. , len(tf1) - 1)
   elif(len(tf2) > len(tf1) and len(tf2) > len(tf3) and len(tf2) > len(tf4)):
      md = statistics.mean(tf2)
      deviation = sem(tf2) * t.ppf((1 + 0.95) / 2. , len(tf2) - 1)
   elif(len(tf3) > len(tf1) and len(tf3) > len(tf2) and len(tf3) > len(tf4)):
      md = statistics.mean(tf3)
      deviation = sem(tf3) * t.ppf((1 + 0.95) / 2. , len(tf3) - 1)
   elif(len(tf4) > len(tf1) and len(tf4) > len(tf2) and len(tf4) > len(tf3)):
      md = statistics.mean(tf4)
      deviation = sem(tf4) * t.ppf((1 + 0.95) / 2. , len(tf4) - 1)

   return [md, deviation]

def durationPrints(md, deviation, idProject, actualValue):

   upperEstimation = md + deviation
   bottomEstimation = md - deviation
   upperEstimation = datetime.timedelta(seconds=upperEstimation)
   upperEstimation = upperEstimation - datetime.timedelta(microseconds=upperEstimation.microseconds)
   bottomEstimation = datetime.timedelta(seconds=bottomEstimation)
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

def percentageError(actualValue, upperEstimation, bottomEstimation):
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
      durationMc = durationMC(ts)
      md = durationMc[0]
      y_forecast.append(md)
      y_true.append(validation[int(element)])
      s = s + 1
   mse = np.square(np.subtract(y_true,y_forecast)).mean() 
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
      takttimeMC = taktTimeMC(ts)
      md = takttimeMC[0]
      y_forecast.append(md)
      y_true.append(statistics.mean(validation))
      s = s + 1 
   mse = np.square(np.subtract(y_true,y_forecast)).mean()
   rmse = np.sqrt(mse)
   print("RMSE: " + str(rmse))


try:
   connection = psycopg2.connect(user="pmiranda", host="localhost", port="5432", database="issues")
   cursor = connection.cursor()

   ################## TaktTime ###################

   # idProject = taktTimeRandProj()
   # validation = taktTimeValidation(idProject)
   # ts = taktTimeProj(idProject)
   # taktTimeMC = taktTimeMC(ts)
   # md = taktTimeMC[0]
   # deviation = taktTimeMC[1]
   # upperEstimation = md + deviation
   # bottomEstimation = md - deviation
   # actualValue = statistics.mean(validation)
   # taktTimePrints(md,deviation,idProject,actualValue)

   ###############################################

   ################# Duration ####################

   durationValidation = durationValidation()
   validation = durationValidation[0]
   idProject = durationValidation[1]
   resolutionDates = durationValidation[2]
   element = np.random.randint(low=0, high=len(idProject))
   ts = durationProj(element, idProject, resolutionDates)
   durationMC = durationMC(ts)
   md = durationMC[0]
   deviation = durationMC[1]
   upperEstimation = md + deviation
   bottomEstimation = md - deviation
   actualValue = validation[int(element)]
   durationPrints(md, deviation, idProject[int(element)], actualValue)


   ###############################################

   ################# Errors ######################

   percentageError(actualValue, upperEstimation, bottomEstimation)

   ###############################################

   ############# Mean Square Error ############

   #durationRMSE()
   #takttimeRMSE()

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
