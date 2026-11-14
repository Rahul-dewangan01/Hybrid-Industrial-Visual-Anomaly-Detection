"""
Forwarding wrapper for backward compatibility.
The Computer Networks compression module now lives in `02_Code/network/compression_network.py`.
"""

import sys, os
_net_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "network"))
if _net_dir not in sys.path:
    sys.path.insert(0, _net_dir)

from network.compression_network import *
