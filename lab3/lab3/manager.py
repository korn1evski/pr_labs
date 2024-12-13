import os
import threading
import time
from raft_node import RaftNode
from consumer import consume_messages
from ftp_fetcher import fetch_and_send_file_periodically

if __name__ == "__main__":
    print("[Manager] manager.py started...", flush=True)
    node_id = os.environ.get('RAFT_NODE_ID', '0')
    peers_str = os.environ.get('RAFT_PEERS', 'manager_node_1:5005;manager_node_2:5006')

    raft_node = RaftNode(node_id, peers_str)
    raft_thread = threading.Thread(target=raft_node.start, daemon=True)
    raft_thread.start()

    stop_flag = {'stop': False}
    ftp_thread = None

    # Periodically check if this node is the leader. If leader, consume messages and run ftp_thread
    while True:
        if raft_node.state == 'Leader':
            print("[Manager] Node is leader, starting to consume messages...")
            consume_messages()  # Make sure this function connects to RabbitMQ and posts to LAB2

            # Start FTP thread if not started
            if not ftp_thread or not ftp_thread.is_alive():
                ftp_thread = threading.Thread(target=fetch_and_send_file_periodically, args=(stop_flag,), daemon=True)
                ftp_thread.start()
        else:
            # Not leader, ensure ftp_thread is stopped
            stop_flag['stop'] = True
            if ftp_thread and ftp_thread.is_alive():
                ftp_thread.join()
            stop_flag['stop'] = False
        time.sleep(5)
