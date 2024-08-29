import requests
from requests.auth import HTTPBasicAuth

# Your Earthdata Login username and password
username = 'rahul191300' 
password = 'Rahultemphackathon123*'

# NASA GIBS WMS request URL
wms_url = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'

# Define parameters for the WMS request
params = {
    'service': 'WMS',
    'version': '1.3.0',
    'request': 'GetMap',
    'layers': 'MODIS_Terra_CorrectedReflectance_TrueColor',
    'bbox': '68.1766451354,6.3200148724,97.4025614766,35.4940095078',  # Bounding box for India
    'width': '1024',  # Increased width
    'height': '1024',  # Increased height
    'crs': 'EPSG:4326',
    'format': 'image/jpeg',
    'time': '2024-08-01'
}

# Make the request with Basic HTTP Authentication using your credentials
response = requests.get(wms_url, params=params, auth=HTTPBasicAuth(username, password))

# Check if the request was successful
if response.status_code == 200:
    # Check if the content type is correct
    if 'image/jpeg' in response.headers['Content-Type']:
        with open('satellite_image_india.jpg', 'wb') as file:
            file.write(response.content)
        print("Image for India downloaded successfully!")
    else:
        print("Unexpected content type:", response.headers['Content-Type'])
        print("Response content:", response.text)
else:
    print("Failed to fetch data. Status code:", response.status_code)
    print("Response content:", response.text)
