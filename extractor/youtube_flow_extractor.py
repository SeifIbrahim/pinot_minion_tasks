"""
Module that filters the youtube traffic flow and saves multiple pcaps
"""

import pyshark
from returns.result import Result, Success


def ends_with(text: str, end: str) -> bool:
    """
    regexp for end with
    :param text: where to look for
    :param end: what to look for
    :return: True for ends and Fals for not ends
    """
    if len(end) > len(text):
        return False
    return text[-len(end):] == end


def extract(filepath: str) -> Result[list, str]:
    """
    Function that extracts the packets that belongs to the youtube video view
    :param filepath: where pcap is
    :param dump_path: where to store resulting files
    :return: list of names of resulting files
    """
    capture = pyshark.FileCapture(
        filepath, display_filter='tls.handshake.extension.type == 0')

    starts = []
    for packet in capture:
        if "TLS" in packet and hasattr(packet.tls,
                                       "handshake_extensions_server_name"):
            sni = packet.tls.handshake_extensions_server_name
            if ends_with(sni, ".googlevideo.com"):
                starts.append((packet.ip.src, packet.tcp.srcport,
                               packet.ip.dst, packet.tcp.dstport))
    capture.close()
    filenames = []
    for src, srcport, dst, dstport in starts:
        tshark_filter = f"(ip.src == {src} && tcp.srcport == {srcport} && " \
                        f"ip.dst == {dst} && tcp.dstport == {dstport}) || " \
                        f"(ip.src == {dst} && tcp.srcport == {dstport} && " \
                        f"ip.dst == {src} && tcp.dstport == {srcport}) || " \
                        f"(quic && udp.srcport == 443) || "\
                        f"(quic && udp.dstport == 443)"
        filename = f"{src}_{srcport}_{dst}_{dstport}.pcap"
        filenames.append(filename)
        capture = pyshark.FileCapture(filepath,
                                      display_filter=tshark_filter,
                                      output_file=filename)
        capture.load_packets()
        capture.close()

    return Success(filenames)


if __name__ == '__main__':
    extract(r"p.cap")
