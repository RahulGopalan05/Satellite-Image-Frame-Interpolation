import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import cv2
import os

# Your Earthdata Login username and password
username = 'rahul191300' 
password = 'Rahultemphackathon123*'

# NASA GIBS WMS request URL
wms_url = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'

# Define bounding box for India
bbox = '68.1766451354,6.3200148724,97.4025614766,35.4940095078'

# Time range and interval
start_time = datetime(2024, 8, 17, 0, 0)  # Start time (YYYY, MM, DD, HH, MM)
end_time = datetime(2024, 8, 27, 0, 0)  # End time (YYYY, MM, DD, HH, MM)
interval = timedelta(minutes=30)  # Interval between images

current_time = start_time

# Create directory for saving images
if not os.path.exists('images'):
    os.makedirs('images')

while current_time <= end_time:
    # Format time as required by WMS (e.g., 2024-08-28)
    time_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
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
        'time': time_str
    }

    # Make the request with Basic HTTP Authentication using your credentials
    response = requests.get(wms_url, params=params, auth=HTTPBasicAuth(username, password), verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        # Check if the content type is correct
        if 'image/jpeg' in response.headers['Content-Type']:
            # Save the image with a timestamped filename
            filename = f'images/satellite_image_{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Image for {time_str} downloaded successfully!")
        else:
            print("Unexpected content type:", response.headers['Content-Type'])
            print("Response content:", response.text)
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        print("Response content:", response.text)

    # Move to the next time interval
    current_time += interval

# Frame Interpolation
def interpolate_frames(image1_path, image2_path, num_interpolated_frames):
    img1 = cv2.imread(image1_path)
    img2 = cv2.imread(image2_path)
    interpolated_frames = []

    for i in range(1, num_interpolated_frames + 1):
        alpha = i / (num_interpolated_frames + 1)
        interpolated_frame = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
        frame_path = f'images/interpolated_frame_{i}.jpg'
        cv2.imwrite(frame_path, interpolated_frame)
        interpolated_frames.append(frame_path)

    return interpolated_frames

# Video Generation
def create_video(frame_paths, video_path, fps=30):
    frame = cv2.imread(frame_paths[0])
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for frame_path in frame_paths:
        frame = cv2.imread(frame_path)
        video.write(frame)

    video.release()
    print(f"Video created successfully at {video_path}")

# Create interpolated frames between downloaded images
image_files = sorted([f for f in os.listdir('images') if f.startswith('satellite_image_')])
frame_paths = []

for i in range(len(image_files) - 1):
    frame_paths.extend(interpolate_frames(
        os.path.join('images', image_files[i]),
        os.path.join('images', image_files[i + 1]),
        num_interpolated_frames=29  # Interpolating 29 frames between each image
    ))

# Add the original images to the video
frame_paths.extend([os.path.join('images', f) for f in image_files])

# Create the final video
create_video(frame_paths, 'satellite_video.mp4')
