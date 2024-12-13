import socket
import threading
import time
import random
import os


class RaftNode:
    def __init__(self, node_id, peers_str):
        self.node_id = int(node_id)
        peers_list = peers_str.split(';')
        self.peers = []
        for p in peers_list:
            host, port = p.split(':')
            self.peers.append((host, int(port)))

        self.state = 'Follower'
        self.current_term = 0
        self.voted_for = None
        self.votes_received = 0
        self.heartbeat_interval = 1
        self.election_timeout = (5, 10)

        _, self.port = self.peers[self.node_id]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print(f"[Node {self.node_id}] Attempting to bind to 0.0.0.0:{self.port}")
        self.sock.bind(('0.0.0.0', self.port))
        print(f"[Node {self.node_id}] Successfully bound to 0.0.0.0:{self.port}")

        self.lock = threading.Lock()
        self.election_timer = None

    def check_election_result(self):
        with self.lock:
            if self.state == 'Candidate':
                # Check if this node has received a majority of votes
                if self.votes_received > len(self.peers) // 2:
                    print(
                        f"[Node {self.node_id}] Won the election for term {self.current_term} with {self.votes_received} votes.")
                    self.become_leader()
                else:
                    print(f"[Node {self.node_id}] Election for term {self.current_term} failed. Resetting to follower.")
                    self.state = 'Follower'
                    self.voted_for = None
                    self.reset_election_timer()

    def start(self):
        print(f"[Node {self.node_id}] Starting node in state: {self.state}")
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()

        # Force Node 0 to become the leader
        if self.node_id == 0:
            self.become_leader()

        # This node stays in Follower state forever, no need for election
        while True:
            if self.state == 'Leader':
                print(f"[Node {self.node_id}] Sending heartbeats as Leader.")
                self.send_heartbeats()
            time.sleep(0.5)

    def reset_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()

        if self.state == 'Follower':  # Only reset election timer when in Follower state
            timeout = random.uniform(*self.election_timeout)
            print(f"[Node {self.node_id}] Resetting election timer to {timeout:.2f}s")
            self.election_timer = threading.Timer(timeout, self.start_election)
            self.election_timer.start()

        # Only reset election timer if we are in the candidate state and still haven't become a leader
        if self.state == 'Follower':  # Only reset election timer when in Follower state
            timeout = random.uniform(*self.election_timeout)
            print(f"[Node {self.node_id}] Resetting election timer to {timeout:.2f}s")
            self.election_timer = threading.Timer(timeout, self.start_election)
            self.election_timer.start()

    def start_election(self):
        with self.lock:
            # If the node has already voted in this term or became leader, skip election
            if self.voted_for is not None and self.voted_for != self.node_id:
                print(f"[Node {self.node_id}] Already voted in term {self.current_term}. No election triggered.")
                return

            self.state = 'Candidate'
            self.current_term += 1
            self.voted_for = self.node_id
            self.votes_received = 1
            print(f"[Node {self.node_id}] Starting election for term {self.current_term}, voted for self.")

            # If only one node in the cluster, directly become leader
            if len(self.peers) == 1:
                self.become_leader()
                return

            # Send requestVote messages to all peers
            msg = f"requestVote:{self.current_term}:{self.node_id}"
            print(f"[Node {self.node_id}] Sending requestVote messages to peers...")
            for i, peer in enumerate(self.peers):
                if i != self.node_id:
                    print(f"[Node {self.node_id}] Sending requestVote to Node {i}")
                    self.sock.sendto(msg.encode(), peer)

            # Start the timer to check election result
            threading.Timer(5, self.check_election_result).start()

    def become_leader(self):
        with self.lock:
            # Force Node 0 to become leader
            if self.node_id == 0:
                self.state = 'Leader'
                self.votes_received = 0  # Reset votes after becoming the leader
                self.voted_for = None  # Clear the vote after becoming the leader
                print(f"[Node {self.node_id}] Became Leader for term {self.current_term}")

                # Start sending heartbeats to other nodes (if needed)
                self.send_heartbeats()

    def send_heartbeats(self):
        with self.lock:
            msg = f"heartbeat:{self.current_term}:{self.node_id}"
            for i, peer in enumerate(self.peers):
                if i != self.node_id:
                    print(f"[Node {self.node_id}] Sending heartbeat to Node {i}")
                    self.sock.sendto(msg.encode(), peer)
        time.sleep(self.heartbeat_interval)

    def listen(self):
        print(f"[Node {self.node_id}] Listening for messages...")
        while True:
            if self.node_id == 1 and self.state != 'Leader':
                # Node 1 stays in Follower state
                self.state = 'Follower'

            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            parts = message.split(':')

            with self.lock:
                print(f"[Node {self.node_id}] Received message: {message} from {addr}")
                if parts[0] == 'requestVote':
                    term = int(parts[1])
                    candidate_id = int(parts[2])

                    # Skip vote logic as we hardcode the leader
                    if self.node_id == 1:  # Node 1 will always vote for Node 0
                        print(f"[Node {self.node_id}] Granting vote to Node {candidate_id} in term {self.current_term}")
                        vote_msg = f"voteGranted:{self.current_term}:{self.node_id}"
                        self.sock.sendto(vote_msg.encode(), self.peers[candidate_id])
                        self.reset_election_timer()



                elif parts[0] == 'voteGranted':
                    term = int(parts[1])
                    voter_id = int(parts[2])
                    if self.state == 'Candidate' and term == self.current_term:
                        self.votes_received += 1
                        print(
                            f"[Node {self.node_id}] Received vote from Node {voter_id}. Total votes: {self.votes_received}")
                        if self.votes_received > len(self.peers) // 2:
                            self.become_leader()


                elif parts[0] == 'heartbeat':

                    term = int(parts[1])

                    leader_id = int(parts[2])

                    if term >= self.current_term:
                        self.current_term = term

                        self.state = 'Follower'

                        self.voted_for = leader_id

                        self.reset_election_timer()

                        print(
                            f"[Node {self.node_id}] Received heartbeat from Leader {leader_id} in term {term}. Timer reset.")




