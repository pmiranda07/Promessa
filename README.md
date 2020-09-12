# Monte Carlo Forecasting Analysis

Software developers can’t usually estimate accurately the effort, time and cost of a project to be developed. This is inherit to the uncertainty that underlies their activity, since after the first estimation of the effort, the project may, with some likelihood, need to adapt to evolving circumstances, which may lead to changes in its scope, and consequently in delivery dates. These new circumstances may be impossible to predict in any estimation effort taken when the project started. These delays not only affect the development team but also other parts of the company, such as staffing or marketing. This could, in some situations, lead to the company losing time and in many situations the trust of stakeholders. A snowball effect that had its beginning in that poor estimation. 

Methods that rely on human estimation are, often, time consuming, what can represent a problem when teams waste time in making estimations that will, often, underestimate the effort and duration. From this problem rises the lean forecasting techniques, which aim for accurate forecasts with less effort and time spent estimating for the team or developer.

In this repository, you can find a implementation of a Monte Carlo simulation method and 3 different approaches for forecasting effort and delivery dates. To validate this 3 approaches, 6 different experiments were prepared.

### Monte Carlo Method

Given a set of historical values (for effort, duration or takt time), the algorithm selects a random value from that historical data, adding them together to get the value for all the stories. We then have a set of values for the specific number of stories and after sorting this set, we exclude a percentage of confidence on each side, getting this way a certain confidence interval. We then return the mean, median, optimist (lower) and pessimist (upper) forecasts for that number of stories. The median is classified as our forecast, being our confidence interval defined by the optimist and pessimist values.

In our implementation we use 200 repetitions, due the results obtained. For all the projects in the dataset, with the takt time approach, using half of the project as historical data points(stories) and the other half to validate the forecasts, we analyse the values of MMRE produced with different numbers of repetitions, in relation to the processing time it took to calculate these MMRE. We assume that the other approaches would lead to similar results and conclusions.

The code relative to the Monte Carlo Method implementation can be found [here](forecast.py#L123)

## Forecasting Approaches
The 3 delivery forecasting approaches implemented are based on duration, takt time and effort. **Duration** measures the time between the beginning and end of a story development. **Takt time** measures the times between completion dates of consecutive stories. **Effort** measures the amount of time spent on developing a story. All these provide different ways to achieve a delivery date forecast. These 3 approaches were selected since these are all very common metrics in the field and after the state of the art analysis, our confidence was that these approaches could deliver good results in terms of accuracy and leanity.

### Duration

When forecasting based on duration, the goal is to forecast how long will a story or a set of stories take to be completed and ready to be delivered. In this approach, we take as input N stories as historical data to output the forecast of M stories in the future. The duration d_i, with i = 1,2,3,...,N, of past stories is calculated as the difference between the date the story was put in the state *"In Progress"* (s_i) and the date the story was put in the state *"Done"* (f_i). We do this instead of calculating d_i as the difference between the beginning and end of a story to achieve more accurate results.
The final forecast outputted D is calculated as the sum of the M forecasts, that can be used as a delivery forecast if the user stories are implemented sequentially. The code for the approach implementation can be found [here](forecast.py#L377)

### Takt Time

Takt time is an another approach when trying to forecast a delivery date. When using this measurement of throughput, the date of the final delivery D outputted is calculated through the sum of the M forecasts, using as input the N takt times t_i, with i = 1,2,3,...,N, calculated through the difference between the completion dates of the historical stories c_n, with n = 1,2,3,..., N+1. This way we extract the amount of time between the finishing dates of a set of tasks, that is, the amount of time no story was completed, achieving development rates. With takt times, we can forecast how long will a story or a set of stories take to be completed.
The code for this implementation can be found [here](forecast.py#L365)

### Effort

Effort is another way to go when trying to make forecast for a story or a set of stories.
This approach takes as input the amount of time the developer assigned to the story was really working on that story, counting the amount of other stories that were also assigned to him at the time that specific story was put in the state *"In Progress"* till the time the story was put in the state *"Done"*, that is, for a set of N historical stories, the effort of each story fe_j, with j = 1,2,3,..., N is calculated as the sum of eph_i, with i = 1,2,3,...,h_j, and h_j being the number of hours between the date the story was put in the state *"In Progress"* s_i and the date the story was put in the state *"Done"* f_i. At each hour i of this duration, the number of stories st_j in the state *"In Progress"* and assigned to the developer responsible for the story u_j is calculated and the effort eph_i is calculated dividing st_j per 1, representing the effort per hour spent on a story. In short this approach analyses the time a developer spent really working on a specific story. The approach outputs a W working effort for a number M of stories, taking into account the N historical efforts.

A problem with the effort approach is the fact that it's based on two assumptions. The first is saying a developer will work on all its assigned and opened stories during one hour. This will not be true most of the times, but since at the end the developer will work on all the stories, these assumptions will balance each other, normalizing again the error. The second assumption is that a developer works 8 hours per day.

## Experiments

To evaluate the delivery forecasting approaches mentioned, were developed 6 experiments.

### Duration Forecast For One Story

In [here](forecast.py#L377) is represented the setup of one experience made with the duration approach, that uses all the past stories of the project and that compares the forecasts with the real value of that story, that is, the real duration of the story to forecast.

The duration approach produces confidence intervals too wide and most times not so accurate forecasts. This is due to the fact that even when the story is *"In Progress"*, the developing team is also working on other stories that may have higher priority what will lead to a extended duration when in reality the story was not being worked on. This will produce outputs that are not very helpful for a team or developer trying to forecast how long will take the story to be completed.

### Takt Time Forecast For A Set of Stories

The first experiment made with takt time was to forecast the delivery date for a set of stories and compare it with the values that occurred in real life. In [here](forecast.py#L401) is represented the setup of this experiment.
In this experiment, we take the takt time historical data and predict for the following stories. The number of stories and the finishing dates of sprints are also represented.

### Takt Time Historical/Forecast

The second experiment made with the takt time was in order to know, in this context, what were the best numbers of stories to use as historical data and as forecast. In this experiment we want to know the percentage error of the forecasts in relation to the number of stories to use as historical data and the number of stories to forecast. To aggregate the projects per historical and future number of stories is used the median of relative error or percentage error. In [here](forecast.py#L627) is represented the setup of this experiment.

### Takt Time Moving Window

The third and last experiment made with takt time was in order to take advantage of the fact that the dataset has a project with over 2000 stories, that when taking out the outliers goes to almost 900 stories. We analysed how does this delivery forecasting approach behaves with the evolution of the project. In [here](forecast.py#L717) is presented the setup of a moving window that advances 60 stories at each iteration and uses the previous 45 stories to forecast for that window of 60 stories. 

### Effort Forecast For One Story

In [here](forecast.py#L204) is represented the setup of one experience made with the effort approach, that uses all the past stories of the project and that compares the forecasts with the real value of that story, that is, the real effort of the story to forecast, and has the possibility of comparing with estimations provided by users. This last information is not available for all the projects.

### Effort Forecast For A Set of Stories

The second experiment to do with the effort approach is to test its efficacy when forecasting for a set of stories. In [here](forecast.py#L204) is represented the setup of that experiment.


This work is part of the PROMESSA project, being developer in FEUP.
