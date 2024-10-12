import os
import cv2
from tqdm import tqdm

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def process_video(video_path, output_folder):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = os.path.join(output_folder, video_name)
    create_folder(video_output_folder)
    
    vidcap = cv2.VideoCapture(video_path)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Processing video: {video_name} ({total_frames} frames)")

    count = 0
    progress_bar = tqdm(total=total_frames, desc=f"Extracting frames from {video_name}", unit='frame')

    while True:
        success, image = vidcap.read()
        if not success:
            break
        frame_filename = f"{video_name}_frame{count}.jpg"
        cv2.imwrite(os.path.join(video_output_folder, frame_filename), image)
        count += 1
        progress_bar.update(1)
    
    progress_bar.close()
    vidcap.release()
    print(f"\n{count} images are extracted in {video_output_folder}.")

def process_all_videos_in_directory(directory_path, output_folder):
    create_folder(output_folder)
    for filename in os.listdir(directory_path):
        if filename.endswith(".mp4") or filename.endswith(".avi") or filename.endswith(".mov"):
            video_path = os.path.join(directory_path, filename)
            process_video(video_path, output_folder)

# Example usage
input_directory = 'videos/'             # Directory containing video files
output_directory = 'output_frames'              # Directory to save extracted frames
process_all_videos_in_directory(input_directory, output_directory)

print("Converting video to frames is completed.")