# Let’s read the dataset and see the variables we have.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
import statsmodels.stats.api as sms
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 350)
  
#read the files
data = pd.read_csv("referral.csv")
data.date = pd.to_datetime(data.date)
print(data.shape)

# (97341, 6)

print(data.head())

#  user_id       date country  money_spent  is_referral      device_id
# 0        2 2015-10-03      FR           65            0  EVDCJTZMVMJDG
# 1        3 2015-10-03      CA           54            0  WUBZFTVKXGQQX
# 2        6 2015-10-03      FR           35            0  CBAPCJRTFNUJG
# 3        7 2015-10-03      UK           73            0  PRGXJZAJKMXRH
# 4        7 2015-10-03      MX           35            0  PRGXJZAJKMXRH

# Let’s check data reliability. Firstly, the referral program started on Oct, 31. 
# Let’s make sure we have no referred users prior to that:

print(data[data['date'] < '2015-10-31']['is_referral'].value_counts())
# print(data.query('date<\'2015-10-31\'')['is_referral'].value_counts())

# is_referral
# 0    47341
# Name: count, dtype: int64

# what about after? 

print(data.query('date>=\'2015-10-31\'')['is_referral'].value_counts())
# print(data[data['date'] >= '2015-10-31']['is_referral'].value_counts())

# is_referral
# 1    28017
# 0    21983
# Name: count, dtype: int64

# Each user then should not be in both groups. Let’s see:

print(data.groupby('user_id').is_referral.nunique().sort_values(ascending=False).head(5))
# print(data.groupby('user_id')['is_referral'].nunique().sort_values(ascending=False).head(5))

# user_id
# 9776     2
# 6639     2
# 13642    2
# 6661     2
# 6660     2
# Name: is_referral, dtype: int64

# Certain users are both referred and non-referred…let’s check one of them:

print(data.query('user_id==9776'))

#        user_id   date    country   money_spent  is_referral      device_id
# 61364     9776 2015-11-07      CA           53            0  UWKROJTCYNTHF
# 61365     9776 2015-11-07      CA           15            1  UWKROJTCYNTHF
# 94319     9776 2015-11-25      ES           20            0  UWKROJTCYNTHF

# This is obviously impossible. 
# Let’s just assign to each user its first value of is_referral for all other transactions as well. 
# Obviously, in a real situation we would need to find out what’s happening here by talking 
# to whoever implemented logging.

#make sure data is sorted by date
data['date'] = pd.to_datetime(data['date'])
print(data['date'].is_monotonic_increasing)

# True

#fix is_referral putting the first value
data['is_referral'] = data.groupby('user_id')['is_referral'].transform('first')

#check if all is good now
print(data.groupby('user_id')['is_referral'].nunique().max())
# print(data.groupby('user_id').is_referral.nunique().max())

# 1 

# Q: Can you estimate the impact the program had on the site?

# Firstly, let’s check if it is true that the number of users went up:

#check avg number of users per day before and after the program launch

# plt.figure(figsize=(10, 6))  # optional: improves readability
# plt.title('The total number of unique customers')
# plt.xticks(rotation=45)
# plt.plot(data.groupby('date')['user_id'].nunique())
# # Save the plot before showing it
# plt.savefig("unique_customers_per_day.png", bbox_inches='tight')  # saves to the current directory
# # plt.show()

# # Yeah, it clearly went up around the launch.
# # Let’s now break it down by referred and non-referred users:

# plt.figure(figsize=(10, 6))
# plt.title('The total number of unique customers')
# sns.lineplot(data=data.groupby(['is_referral','date'])['user_id'].nunique().reset_index(), x='date', y='user_id', hue='is_referral')
# plt.xticks(rotation=45)
# plt.savefig("is_referred_customers_per_day.png", bbox_inches='tight')  # saves to the current directory
# # plt.show()

# Interestingly, there has been a noticeable decrease in the number of users 
# who did not participate in the referral program. This decline strongly indicates cannibalization, 
# where the introduction of the new feature is diverting existing customers away from another source. 
# Cannibalization is a common phenomenon seen, for instance, when marketing initiatives 
# like paid advertisements draw users away from organic channels such as SEO.

# Let’s check total revenue by day. This is after all the main goal of the program.

# plt.title('The total revenue by day')
# plt.xticks(rotation=45)
# plt.plot(data.groupby('date')['money_spent'].sum())
# plt.savefig("revenue_by_day.png", bbox_inches='tight')
# # plt.show()

# It looks up, but less than total users.

# avg percentage increase of revenue and users after the change
# percentage change = (new_average / old_average - 1) * 100

print(pd.DataFrame({
                   "metric" : ["revenue", "users"],
               "pct_change" : [100*(data.query("date>\"2015-10-30\"").groupby('date')['money_spent'].sum().mean()/data.query("date<\"2015-10-31\"").groupby('date')['money_spent'].sum().mean()-1), 
                               100*(data.query("date>\"2015-10-30\"").groupby('date')['user_id'].nunique().mean()/data.query("date<\"2015-10-31\"").groupby('date')['user_id'].nunique().mean()-1)
               ]
           })
           )

#     metric  pct_change
# 0  revenue   16.826539
# 1    users   21.849607

# Let’s break it down by people who were referred and people who were not.

data_plot = data.groupby(['date', 'is_referral'])['money_spent'].sum().reset_index()

# plt.figure(figsize=(10, 6))
# sns.lineplot(data=data_plot, x='date', y='money_spent', hue='is_referral')
# plt.xticks(rotation=45)
# plt.savefig("is_referred_revenue_by_day.png", bbox_inches='tight')
# # plt.show()

# This observation strongly aligns with the cannibalization hypothesis.

# One plausible scenario is that many existing users are creating new accounts to capitalize 
# on the referral bonus. This could explain why there has been an overall increase in the 
# number of users but a negligible impact on revenue. Additionally, the significant drop in 
# non-referred users immediately after the program's launch supports this hypothesis.

# To validate this, we can leverage the device_id variable. If multiple users are associated 
# with the same device_id, it would suggest suspicious activity. 
# Let's analyze the number of unique device_id entries per day alongside unique users 
# to further investigate this hypothesis.

# #check avg number of users per day before and after the program launch
# plt.title('The total number of unique devices vs unique users')
# plt.xticks(rotation=45)
# plt.plot(data.groupby('date')['device_id'].nunique(), color='blue', label='Unique Devices')
# plt.plot(data.groupby('date')['user_id'].nunique(), color='red', label='Unique Users')
# plt.legend()
# plt.savefig("num_devices_vs_num_users_per_day.png", bbox_inches='tight')
# # plt.show()

# This finding is quite intriguing! Before the referral program test began, 
# we observed more unique devices than users, which is logical since a single user 
# may use multiple devices. However, after launching the program, we now have more users than unique devices. 
# This suggests that different users are sharing the same device, indicating potential fraudulent activity.

# Currently, it's challenging to accurately gauge the impact of the program on the site due to the messy 
# nature of the data. However, to illustrate how it would ideally be analyzed with cleaner data:

# There are several approaches to evaluate the effect of a change that wasn't rigorously A/B tested. 
# These approaches generally involve examining the time series of the metric of interest and 
# identifying any discontinuity points when the change was implemented. 
# One practical method involves using pre-test data to forecast what would have occurred if there were 
# no change, and then comparing these forecasts with the actual observed data. Essentially, 
# this approach simulates an A/B test between predicted outcomes and actual outcomes.

#load time series library prophet, we'll use it for the prediction
# import fbprophet

from prophet import Prophet  #New import

# from prophet.serialize import model_to_json, model_from_json
# from prophet.diagnostics import stan_backend
  
#prepare the before the change dataset. We use total transaction value as main metric
data_prediction = data.query('date<\'2015-10-31\'').groupby('date')['money_spent'].sum().reset_index()
#change column names and index
data_prediction['ds'] = data_prediction['date']
data_prediction.rename({'money_spent': 'y'}, axis=1, inplace=True)
data_prediction.set_index('date', inplace=True)

# Prophet expects a DataFrame with two regular columns: ds and y — not a datetime index.
data_prediction = data_prediction.reset_index()  # Moves 'date' index to a column
data_prediction = data_prediction[['ds', 'y']]   # Keep only the required columns
  
#Let's build the model using prophet. From previous plots, time series appear pretty straightforward 
# and flattish. Default values should do fine

# Create model and switch to PyStan backend

# ts = Prophet(interval_width=0.95)

# Use MCMC sampling (Bayesian full model), which avoids Stan's optimize crashes
ts = Prophet(interval_width=0.95, mcmc_samples=100)
# ts.stan_backend = stan_backend.get_backend_class("PystanBackend")(ts)

# Fit the model
ts.fit(data_prediction)
# ts.fit(data_prediction, algorithm='LBFGS', iter=1000)

# Make predictions until the max date we have in our dataset
days_predictions = (data['date'].max() - data_prediction['ds'].max()).days
future_data = ts.make_future_dataframe(periods=days_predictions)
predictions = ts.predict(future_data)

# # Let's plot the predictions
# ts.plot(predictions)
# plt.plot(data.query("date > '2015-10-30'").groupby('date')['money_spent'].sum(), 'o', color='red', label='revenue')
# plt.legend()
# plt.savefig("predictions.png", bbox_inches='tight')
# # plt.show()

# As we can see, actual values tend to be fairly consistently above our predictions, 
# often well above the 95% interval of the prediction. After all, we did see in the plot 
# the revenue seemed to have gone up compared to the trend.

#compare the means
print("Mean revenue per day after the launch is: ", 
      round(data.query('date>\'2015-10-30\'').groupby('date')['money_spent'].sum().mean()),
      "\n",
      "Mean revenue of our predictions is:",
      round(predictions.query('ds>\'2015-10-30\'')['yhat'].mean())
      )

# Mean revenue per day after the launch is:  83714
# Mean revenue of our predictions is: 79049

# As expected, average actual values are higher.
# Let’s do a t-test now:

#Let's do a paired t-test here where we are comparing day by day
test = stats.ttest_rel(data.query('date>\'2015-10-30\'').groupby('date')['money_spent'].sum(), predictions.query('ds>\'2015-10-30\'')['yhat'])
print("pvalue: ", round(test.pvalue,5))

# pvalue:  0.00242

# The difference looks significant. That being said, as we said above, 
# data was so messy that we can hardly trust these results.
