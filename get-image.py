import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import os

# Your Earthdata Login username and password
username = 'rahul191300' 
password = 'Rahultemphackathon123*'

# NASA GIBS WMS request URL
wms_url = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'

# Define global bounding box
bbox = '-180,-90,180,90'  # Global bounding box

# Time range
start_date = datetime(2014, 1, 1)  # Start date (YYYY, MM, DD)
end_date = datetime(2023, 12, 31)  # End date (YYYY, MM, DD)

# Create directory for saving images
if not os.path.exists('images'):
    os.makedirs('images')

current_date = start_date

while current_date <= end_date:
    # Format date as required by WMS (e.g., 2024-08-01)
    date_str = current_date.strftime('%Y-%m-%d')
    
    # Define parameters for the WMS request
    params = {
        'service': 'WMS',
        'version': '1.3.0',
        'request': 'GetMap',
        'layers': 'MODIS_Terra_CorrectedReflectance_TrueColor',
        'bbox': bbox,
        'width': '1024',
        'height': '1024',
        'crs': 'EPSG:4326',
        'format': 'image/jpeg',
        'time': date_str
    }

    # Make the request with Basic HTTP Authentication using your credentials
    response = requests.get(wms_url, params=params, auth=HTTPBasicAuth(username, password), verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        # Check if the content type is correct
        if 'image/jpeg' in response.headers['Content-Type']:
            # Save the image with a timestamped filename
            filename = f'images/satellite_image_{current_date.strftime("%Y-%m-%d")}.jpg'
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Image for {date_str} downloaded successfully!")
        else:
            print("Unexpected content type:", response.headers['Content-Type'])
            print("Response content:", response.text)
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        print("Response content:", response.text)

    # Move to the next day
    current_date += timedelta(days=1)
