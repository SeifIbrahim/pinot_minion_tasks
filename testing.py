import sys
if __name__ == '__main__':
    if len(sys.argv) != 4:
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
