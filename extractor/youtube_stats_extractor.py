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
    while window and window[0]['timestamp'] < start_time:
        window.popleft()

    # find the first element to add
    if not window:
        while data[data_idx]['timestamp'] < start_time:
            data_idx += 1
        if data[data_idx]['timestamp'] < start_time + WINDOW_SIZE:
            window.append(data[data_idx])
        else:
            return data_idx

    # move right side
    while window[-1]['timestamp'] < start_time + WINDOW_SIZE:
        window.append(data[data_idx])
        data_idx += 1

    return data_idx


def get_network_summary_stats(packets):
    return {
        'bytes_per_packet':
        array_stats([packet['size'] for packet in packets]),
        'inter_arrival_time':
        array_stats([
            packets[i]['timestamp'] - packets[i - 1]['timestamp']
            for i in range(1, len(packets))
        ]),
    }


def get_network_window_stats(packet_window, window_start):
    packet_count = len(packet_window)
    byte_count = sum(packet['size'] for packet in packet_window)
    packet_count = len(packet_window)
    throughput = byte_count / WINDOW_SIZE

    return {
        'byte_count': byte_count,
        'packet_count': packet_count,
        'throughput': throughput,
        'idle_time': idle_time(packet_window, window_start),
    }


def get_QoE_window_stats(report, window_start):
    return {
        'median_resolution':
        int(
            statistics.median(
                int(re.match(r'\d+x(\d+).*', r['resolution']).group(1))
                for r in report))
    }


def get_ping_window_stats(ping_window, window_start):
    return {'mean': statistics.mean(ping['ping'] for ping in ping_window)}


def get_window_stats(data, window_start, extract_func):
    get_window_stats = []
    data_idx = 0
    window = deque()

    while True:
        try:
            data_idx = shift_window(window, window_start, data, data_idx)
        except IndexError:
            break

        if window:
            get_window_stats.append(extract_func(window, window_start))
        else:
            # empty window
            get_window_stats.append(None)

        window_start += WINDOW_SHIFT

    return get_window_stats


def youtube_stats_extractor():
    report_dir = "/home/seif/Documents/CS293N/project/pinot_minion_tasks/youtube_data/dQw4w9WgXcQ_0"
    pcap_file = "169.231.178.179_35416_198.189.66.16_443.pcap"
    pcap_path = f"{report_dir}/{pcap_file}"
    state_path = f"{report_dir}/state.json"
    report_path = f"{report_dir}/report.json"
    ping_path = f"{report_dir}/ping.txt"
    meta_path = f"{report_dir}/meta.json"

    src_ip = pcap_file.split('_')[0]

    video_start = 0
    with open(state_path, 'r') as f:
        for line in f:
            state = json.loads(line)
            if state['new_state'] == 1:
                video_start = state['timestamp'] / 1000
                break

    startup_delay = 0
    with open(meta_path, 'r') as f:
        startup_delay = json.loads(f.read())['startup_delay']

    # read application layer report
    report = None
    with open(report_path, 'r') as f:
        report = [json.loads(line) for line in f]
    for r in report:
        r['timestamp'] /= 1000

    # read network layer capture (we only use timestamp and packet size)
    capture = pyshark.FileCapture(pcap_path)
    upstream = []
    downstream = []
    for packet in capture:
        if packet.ip.src == src_ip:
            upstream.append({
                'timestamp': float(packet.sniff_timestamp),
                'size': int(packet.ip.len)
            })
        else:
            downstream.append({
                'timestamp': float(packet.sniff_timestamp),
                'size': int(packet.ip.len)
            })
    upstream.sort(key=lambda packet: packet['timestamp'])
    downstream.sort(key=lambda packet: packet['timestamp'])

    # read last mile latency ping
    pings = []
    ping_stats = {}
    with open(ping_path, 'r') as f:
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

    # collect window stats
    upstream_window_stats = get_window_stats(upstream, video_start,
                                             get_network_window_stats)
    downstream_window_stats = get_window_stats(downstream, video_start,
                                               get_network_window_stats)
    QoE_window_stats = get_window_stats(report, video_start,
                                        get_QoE_window_stats)
    ping_window_stats = get_window_stats(pings, video_start,
                                         get_ping_window_stats)

    window_stats = [{
        'network': {
            'upstream': upstream,
            'downstream': downstream,
        },
        'QoE': QoE,
        'ping': ping,
    }
                    for upstream, downstream, QoE, ping in zip(
                        upstream_window_stats, downstream_window_stats,
                        QoE_window_stats, ping_window_stats)]

    # collect summary statistics
    summary_stats = {
        'network': {
            'upstream': get_network_summary_stats(upstream),
            'downstream': get_network_summary_stats(downstream),
        },
        'ping': ping_stats,
        'startup_delay': startup_delay / 1000,
    }

    print(window_stats)
    print(summary_stats)


youtube_stats_extractor()
