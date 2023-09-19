#!/usr/bin/env python
# coding: utf-8

# In[2]:


pip install azure-storage-file-datalake


# In[4]:


pip list


# In[3]:


pip install pyarrow


# In[4]:


pip install fastparquet


# In[59]:


import os
import time
import pandas as pd
from io import BytesIO
from azure.storage.filedatalake import DataLakeServiceClient

connection_string = "DefaultEndpointsProtocol=https;AccountName=capstonesecondcars;AccountKey=XdumWQRlJuB2QQFUEpuCq/2oEIiXioOPmvCO1oM0ulR92UZ4UaAKnMAMC9l05tL42bG0LAIoXAy8+AStIRCJMw==;EndpointSuffix=core.windows.net"
file_system_name = 'capstone-filesystem'

# Creating a DataLakeServiceClient using the connection string
service_client = DataLakeServiceClient.from_connection_string(connection_string)

# Getting the file system
file_system_client = service_client.get_file_system_client('capstone-filesystem')


# In[60]:


file_path = file_system_client.get_paths()

for file in file_path:
    print(file.name)


# In[61]:


dfs = {}

files_path = file_system_client.get_paths()

for file in files_path:
    if(file.name.endswith('.parquet')):
        file_client = file_system_client.get_file_client(file.name)
        file_data = file_client.download_file().readall()
        
        df = pd.read_parquet(BytesIO(file_data))
        dfs[file.name] = df


# In[62]:


print('Number of dataframes: ',len(dfs))

for name,df in dfs.items():
    print('Name of dataframe:',name)


# In[63]:


cars_df = dfs['silver/cars/part-00000-fdc5a7f7-1048-4a27-97ca-8039054bda1e-c000.snappy.parquet']
cars_df.head()


# In[65]:


customers_df = dfs['silver/customers/part-00000-8dde0b55-291c-4539-a439-95cac25a72eb-c000.snappy.parquet']
customers_df.head()


# In[66]:


policy_df = dfs['silver/policy/part-00000-2bbc4a75-b093-4fcd-a18d-ea577a2bebac-c000.snappy.parquet']
policy_df.head()


# In[67]:


sales_df = dfs['silver/sales/part-00000-60e14114-2119-459e-a55b-e77d9d3baf62-c000.snappy.parquet']
sales_df.head()


# In[68]:


# Insight 1: Top Selling Car Models
top_selling_models = sales_df['car_id'].value_counts().reset_index()
top_selling_models.columns = ['CarModel', 'Sales_Count']


merged_df = pd.merge(sales_df,cars_df,on='car_id')

top_selling_models = merged_df.groupby('model')['sales_id'].count().reset_index()
top_selling_models = top_selling_models.rename(columns={'sales_id': 'Sales_Count'})

top_selling_models = top_selling_models.sort_values(by='Sales_Count', ascending=False).reset_index()
top_selling_models.drop('index',axis=1)


# In[69]:


# Insight 2: Customer Demographics
customer_demographics = customers_df.groupby(['Region', 'State', 'City']).size().reset_index(name='Customer_Count')
customer_demographics


# In[70]:


# Insight 3: Customer Ownership Patterns
customer_ownership_patterns = customers_df['owner'].value_counts().reset_index()
customer_ownership_patterns.columns = ['Ownership_Type', 'Ownership_Count']
customer_ownership_patterns


# In[79]:


# Insight 4: Policy Durations
policy_df['policy_bind_date'] = pd.to_datetime(policy_df['policy_bind_date'])
sales_df['sold_on'] = pd.to_datetime(sales_df['sold_on'])

policy_durations = pd.merge(customers_df[['CustomerID']], policy_df[['customer_id', 'policy_bind_date']], left_on='CustomerID', right_on='customer_id')
policy_durations['Policy_Duration_In_Days'] = (sales_df['sold_on'] - policy_durations['policy_bind_date']).dt.days
policy_durations = policy_durations.drop(columns=['customer_id'])
policy_durations


# In[72]:


# Insight 5: Policies by State
merged_df = pd.merge(sales_df,policy_df,on='car_id')
popular_policies_by_state = merged_df.groupby(['State','policy_csl']).size().reset_index(name='Policy_Count')
popular_policies_by_state


# In[73]:


# Insight 6: Total Sales by Region
total_sales_by_region = sales_df.groupby('Region')['selling_price'].sum().reset_index()

total_sales_by_region


# In[74]:


# Insight 7: Sales Frequency
sales_frequency = sales_df.groupby(['Region', 'State', 'City']).size().reset_index(name='Sales_Count')
sales_frequency


# In[75]:


# Insight 8: Most Common Seller Types
common_seller_types = sales_df['seller_type'].value_counts().reset_index()
common_seller_types.columns = ['seller_type', 'count']
common_seller_types


# In[76]:


# Insight 9: sold vehicles
sold_vehicles = sales_df.groupby(['sold']).size().reset_index(name='No_of_vehicles')
sold_vehicles


# In[77]:


# Insight 10: Average Selling Price by Car Model
merged_df = pd.merge(sales_df, cars_df, on = 'car_id')
avg_selling_price = merged_df.groupby(['model'])['selling_price'].mean().reset_index(name='Average_Selling_price')
avg_selling_price


# In[82]:


# Insight 11: Annual Premium by job type
merged_df = pd.merge(customers_df, policy_df,left_on='CustomerID', right_on='customer_id')
annual_premium_by_job = merged_df.groupby(['Job'])['policy_annual_premium'].mean().reset_index(name='Average_annual_premium')
annual_premium_by_job


# In[93]:


# Insight 12: Total Sales by Year/Month
sales_df_new = sales_df.dropna(subset=['sold_on']) 
sales_df_new['Year'] = pd.to_datetime(sales_df_new['sold_on']).dt.year
sales_df_new['Month'] = pd.to_datetime(sales_df_new['sold_on']).dt.month

sales_df_new = sales_df_new.groupby(['Year','Month'])['selling_price'].sum().reset_index(name='Total_Sales')
sales_df_new


# In[96]:


# Insight 13: No of cars sold by customers
merged_df_1 = pd.merge(sales_df,cars_df,on='car_id')
merged_df_2 = pd.merge(merged_df_1,policy_df,how="left",on='car_id')
merged_df_3 = pd.merge(merged_df_2,customers_df,how="right",right_on='CustomerID', left_on='customer_id')
ans = merged_df_3.groupby(['customer_id'])['car_id'].size().reset_index(name='No_of_cars_sold')
ans


# In[97]:


ans = ans.sort_values(by='No_of_cars_sold', ascending=False).reset_index()
ans


# In[101]:


# Insight 14: Number of Cars by Transmission Type
cars_by_transmission = cars_df['transmission'].value_counts().reset_index()
cars_by_transmission.columns = ['transmission', 'num_of_cars']
cars_by_transmission


# In[110]:


# Insight 15:  Number of Cars by Fuel Type
cars_by_fuel = cars_df['fuel'].value_counts().reset_index()
cars_by_fuel.columns = ['fuel', 'num_of_cars']
cars_by_fuel


# In[ ]:




