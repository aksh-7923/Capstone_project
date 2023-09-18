import os
import time
from azure.storage.filedatalake import DataLakeServiceClient


connection_string = "DefaultEndpointsProtocol=https;AccountName=capstonesecondcars;AccountKey=XdumWQRlJuB2QQFUEpuCq/2oEIiXioOPmvCO1oM0ulR92UZ4UaAKnMAMC9l05tL42bG0LAIoXAy8+AStIRCJMw==;EndpointSuffix=core.windows.net"
file_system_name = 'capstone-filesystem\\bronze'

# Creating a DataLakeServiceClient using the connection string
service_client = DataLakeServiceClient.from_connection_string(connection_string)

# Getting the file system client
file_system_client = service_client.get_file_system_client('capstone-filesystem\\bronze')

#path of files in local storage
local_folder_path = (
    r"C:\One Drive\OneDrive - Tredence\Desktop\project\cars"
)


for file in os.listdir(local_folder_path):
    if file.endswith(".csv"):
        file_name = os.path.splitext(file)[0]
        directory_path = os.path.join(file_system_name, file_name)

        # Creating the directory with filename
        directory_client = file_system_client.get_directory_client(file_name)
        directory_client.create_directory()

        # creating a file client 
        file_client = directory_client.get_file_client(file)
        local_file_path = os.path.join(local_folder_path, file)
        
        # Uploading the local CSV file to Azure Data Lake Storage
        with open(local_file_path, "rb") as local_file:
            file_client.upload_data(local_file, overwrite=True)

        print(f"Uploaded {file} to {directory_path}")
        
        time.sleep(10)






