import cv2
import os
import numpy as np

# Directory where the images are stored
image_dir = 'images'

# Frame Interpolation Using Optical Flow
def interpolate_frames_optical_flow(image1_path, image2_path, num_interpolated_frames):
    img1 = cv2.imread(image1_path)
    img2 = cv2.imread(image2_path)
    
    # Ensure images have the same dimensions
    if img1.shape != img2.shape:
        raise ValueError("Images must have the same dimensions for interpolation.")
    
    # Convert images to grayscale for optical flow calculation
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Calculate the dense optical flow using Farneback method
    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    interpolated_frames = []

    for i in range(1, num_interpolated_frames + 1):
        alpha = i / (num_interpolated_frames + 1)
        
        # Interpolate the motion field by scaling the flow vector
        flow_interpolated = flow * alpha
        
        # Generate the interpolated frame by warping img1 towards img2 using the interpolated flow
        map_x, map_y = np.meshgrid(np.arange(img1.shape[1]), np.arange(img1.shape[0]))
        map_x = map_x.astype(np.float32) + flow_interpolated[..., 0]
        map_y = map_y.astype(np.float32) + flow_interpolated[..., 1]

        interpolated_frame = cv2.remap(img1, map_x, map_y, interpolation=cv2.INTER_LINEAR)

        frame_path = f'{image_dir}/interpolated_frame_{i}.jpg'
        cv2.imwrite(frame_path, interpolated_frame)
        interpolated_frames.append(frame_path)
        
        # Optional: Print out the current alpha value and show the frame for debugging
        print(f"Interpolating frame {i}/{num_interpolated_frames} with alpha={alpha}")
        cv2.imshow('Interpolated Frame', interpolated_frame)
        cv2.waitKey(500)  # Display the frame for 500 ms for visual inspection

    cv2.destroyAllWindows()
    return interpolated_frames

# Video Generation
def create_video(frame_paths, video_path, fps=30):
    # Read the first frame to get the size
    frame = cv2.imread(frame_paths[0])
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for frame_path in frame_paths:
        frame = cv2.imread(frame_path)
        frame = cv2.resize(frame, (width, height))  # Ensure the frame size matches
        video.write(frame)

    video.release()
    print(f"Video created successfully at {video_path}")

# Process images to create a video
def process_images(image_dir):
    # Get all image files sorted by timestamp
    image_files = sorted([f for f in os.listdir(image_dir) if f.startswith('satellite_image_')])

    # Create a list to hold all frame paths
    frame_paths = []

    # Interpolate frames between each pair of images using optical flow
    for i in range(len(image_files) - 1):
        frame_paths.extend(interpolate_frames_optical_flow(
            os.path.join(image_dir, image_files[i]),
            os.path.join(image_dir, image_files[i + 1]),
            num_interpolated_frames=9  # Interpolating 9 frames between each image for a total of 10 frames per transition
        ))

    # Add the original images to the video
    frame_paths.extend([os.path.join(image_dir, f) for f in image_files])

    # Create the final video
    create_video(frame_paths, 'satellite_video.mp4')

# Run the process
process_images(image_dir)
