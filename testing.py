import sys
import os
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(sys.argv)
        print("Usage: python3 example.py <video> <duration> <data_dump>")
        print("Executing with default values: python3 example.py"
              " https://www.youtube.com/watch?v=dQw4w9WgXcQ 10 youtube_data")
        video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        duration = 10
        data_dump = "youtube_data"
    else:
        print(sys.argv)
        print("length is 4 and ok")
        video = sys.argv[1]
        duration = int(sys.argv[2])
        data_dump = sys.argv[3]
    print(video)
    video_id = video.split("=")[1]
    print(video_id)
    
    if not os.path.exists(data_dump):
        os.mkdir(data_dump)

    # create a unique directory for the session
    i = 0
    session_folder = os.path.join(data_dump, f"{video_id}_{i}")
    while os.path.exists(session_folder):
        i += 1
        session_folder = os.path.join(data_dump, f"{video_id}_{i}")
    os.mkdir(session_folder)

    os.chdir(session_folder)
