import pyshark
import json
import re
import statistics
import scipy.stats
from collections import deque

WINDOW_SIZE = 2
WINDOW_SHIFT = 1


def idle_time(packet_window, window_start):
    # divide the data into 100ms intervals, a window with no packets is idle
    IDLE_SIZE = .1
    cur_time = window_start
    end_time = window_start + WINDOW_SIZE
    packet_idx = 0
    idle = 0
    while cur_time < end_time:
        idle += 1
        if cur_time > packet_window[packet_idx]['timestamp']:
            # we just skipped over some packets
            idle -= 1
            while cur_time > packet_window[packet_idx]['timestamp']:
                packet_idx += 1
        cur_time += IDLE_SIZE
    return idle


def array_stats(array):
    # mean, min, max, median, standard deviation, skewness, kurtosis.
    return {
        'mean': statistics.mean(array),
        'min': min(array),
        'max': max(array),
        'median': statistics.median(array),
        'standard_deviation': scipy.stats.tstd(array),
        'skewness': scipy.stats.skew(array),
        'kurtosis': scipy.stats.kurtosis(array)
    }


def shift_window(window, start_time, data, data_idx):
    """
    shift the window right
    :param window: the window to shift
    :param start_time: the timestamp that the window should start at
    :param data: the data array to populate the window with
    :param data_idx: the next index in the data array (not in window)
    :return: the updated data_index or throws exception if reached end
    """
    # move left side
    while not window or window[0]['timestamp'] < start_time:
        if not window:
            window.append(data[data_idx])
            data_idx += 1
        else:
            window.popleft()

    # move right side
    while window[-1]['timestamp'] < start_time + WINDOW_SIZE:
        window.append(data[data_idx])
        data_idx += 1

    return data_idx


def youtube_stats_extractor():
    # pcap_file = "../youtube_data/dQw4w9WgXcQ_0/169.231.179.199_43828_173.194.166.91_443.pcap"
    pcap_file = "../youtube_data/dQw4w9WgXcQ_0/169.231.179.199_43830_173.194.166.91_443.pcap"
    state_file = "../youtube_data/dQw4w9WgXcQ_0/state.txt"
    report_file = "../youtube_data/dQw4w9WgXcQ_0/report.txt"
    ping_file = "../youtube_data/dQw4w9WgXcQ_0/ping.txt"
    meta_file = "../youtube_data/dQw4w9WgXcQ_0/meta.txt"

    video_start = 0
    with open(state_file, 'r') as f:
        for line in f:
            state = json.loads(line)
            if state['new_state'] == 1:
                video_start = state['timestamp'] / 1000
                break

    startup_delay = 0
    with open(meta_file, 'r') as f:
        startup_delay = json.loads(f.read())['startup_delay']

    # read application layer report
    report = None
    with open(report_file, 'r') as f:
        report = [json.loads(line) for line in f]

    # read network layer capture (we only use timestamp and packet size)
    packets = [{
        'timestamp': float(packet.sniff_timestamp),
        'size': int(packet.data.len)
    } for packet in pyshark.FileCapture(pcap_file)]

    # read last mile latency ping
    pings = []
    ping_stats = {}
    with open(ping_file, 'r') as f:
        for line in f:
            match = re.match(r'\[(.*)\].*time=(.*) ms', line)
            if match:
                pings.append({
                    'timestamp': float(match.group(1)),
                    'ping': float(match.group(2)) / 1000
                })
            match = re.match(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms',
                             line)
            if match:
                ping_stats = {
                    'rtt': float(match.group(1)) / 1000,
                    'avg': float(match.group(2)) / 1000,
                    'max': float(match.group(3)) / 1000,
                    'mdev': float(match.group(4)) / 1000,
                }

    # window pointers
    window_start = video_start
    report_idx = 0
    report_window = deque()
    packet_idx = 0
    packet_window = deque()
    ping_idx = 0
    ping_window = deque()

    # collect window stats
    window_stats = []

    while True:
        try:
            shift_window(report_window, window_start, report, report_idx)
        except IndexError:
            print('Ran out of stats for nerds')
            break
        try:
            shift_window(packet_window, window_start, packets, packet_idx)
        except IndexError:
            # we expect to run out of packet caps first since we typically
            # finish downloading the video before we finish watching it
            print('Ran out of packet data')
            break
        try:
            shift_window(ping_window, window_start, pings, ping_idx)
        except IndexError:
            print('Ran out of ping data')
            break

        byte_count = sum(packet['size'] for packet in packet_window)
        packet_count = len(packet_window)
        throughput = byte_count / WINDOW_SIZE
        # example resolution str "640x360@25 / 854x480@25"
        median_resolution = int(
            statistics.median(
                int(re.match(r'\d+x(\d+).*', r['resolution']).group(1))
                for r in report))
        mean_ping = statistics.mean(ping['ping'] for ping in ping_window)

        window_stats.append({
            'network': {
                'byte_count': byte_count,
                'packet_count': packet_count,
                'throughput': throughput,
                'idle_time': idle_time(packet_window, window_start),
            },
            'QoE': {
                'median_resolution': median_resolution,
            },
            'ping': {
                'mean': mean_ping,
            },
        })

        window_start += WINDOW_SHIFT

    # collect summary statistics
    summary_stats = {
        'ping': ping_stats,
        'startup_delay': startup_delay,
        'network': {
            'bytes_per_packet':
            array_stats([packet['size'] for packet in packets]),
            'inter_arrival_time':
            array_stats([
                packets[i]['timestamp'] - packets[i - 1]['timestamp']
                for i in range(1, len(packets))
            ]),
        },
    }

    print(window_stats)
    print(summary_stats)


youtube_stats_extractor()
