"""
Example of youtube data collection
"""
import multiprocessing
import os
import sys

from returns.result import Result, Success, Failure

import QoE_youtube.fastapicollector as fastapic
import QoE_youtube.watcher as watcher
import extractor.youtube_flow_extractor as utubee
import pcap.pcapcollector as pcapc
import meta.ping as ping

BORDER_ROUTER_ADDRESS = "csworld52.cs.ucsb.edu"


def run(video: str, duration: int, pcap_name: str,
        ping_name: str) -> Result[str, str]:
    """
    Example youtube traffic collection run
    :param video:
    :param duration:
    :param pcap_name:
    :param ping_name:
    :return:
    """

    result = ping.start_collecting(ping_name, BORDER_ROUTER_ADDRESS)
    if isinstance(result, Failure):
        return result
    ping_pid = result.unwrap()

    result = pcapc.start_collecting(pcap_name)
    if isinstance(result, Failure):
        return result

    pid = result.unwrap()
    pid = pid[pid.find("<") + 1:pid.find(">")]
    pid = int(pid)

    result = watcher.watch(video, duration)
    if isinstance(result, Failure):
        pcapc.stop_collecting()
        return result

    result = pcapc.stop_collecting(pid)
    if isinstance(result, Failure):
        return result

    result = ping.stop_collecting(ping_pid)
    if isinstance(result, Failure):
        return result

    result = utubee.extract(pcap_name)
    if isinstance(result, Failure):
        return result

    return Success("All done")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 example.py <video> <duration> <data_dump>")
        print("Executing with default values: python3 example.py"
              " https://www.youtube.com/watch?v=dQw4w9WgXcQ 10 youtube_data")
        video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        duration = 10
        data_dump = "youtube_data"
    else:
        video = sys.argv[1]
        duration = int(sys.argv[2])
        data_dump = sys.argv[3]
    print(f'The file we are extracting is {video} with duration {duration} and location as {data_dump}')
    

    video_id = video.split("=")[1]

    pcap_name = "raw_capture.pcap"
    ping_name = "ping.txt"

    # create the user data dump directory if it doesn't exist
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

    fa_c = multiprocessing.Process(target=fastapic.run, args=(".", ))
    fa_c.start()

    try:
        result = run(video, duration, pcap_name, ping_name)
    except Exception:
        raise
    finally:
        fa_c.terminate()

    print(result)
