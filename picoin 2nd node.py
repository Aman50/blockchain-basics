# Creating a simple Cryptocurrency = PiCoin

# Importing the required libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from urllib.parse import urlparse
from uuid import uuid4
import requests

# Step 1 - Creating the BlockChain - Basically a class
# For Cryptocurrency, we need to include 2 main pillars into our Blockchain class
# 1. Concept of transactions - Cryptocurrencies are basically based on movement of some currency
# 2. Consensus - To ensure each of the nodes in our network are on the same page i.e. have same main chain.
class Blockchain:
    """Class defining our blockchain"""
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.add_block_to_chain(proof=1, prev_hash='0')  # Genesis Block
        self.nodes = set()

    # Add block is called after proof of work, block is mined.
    def add_block_to_chain(self, proof, prev_hash):
        block = {
            'proof': proof,
            'prev_hash': prev_hash,
            'index': len(self.chain) + 1,
            'transactions': self.transactions,
            'timestamp': str(datetime.datetime.now())}

        self.transactions = []
        self.chain.append(block)
        return block

    # Get Last block in our BlockChain
    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        current_proof = 0
        solution_found = False
        while not solution_found:
            hash_value = hashlib.sha256(str(current_proof**10 - prev_proof**5).encode()).hexdigest()
            if hash_value[:6] == '000000':
                solution_found = True
            else:
                current_proof += 1
        return current_proof

    def get_hash_of_block(self, block):
        current_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(current_block.encode()).hexdigest()

    def check_valid_chain(self, chain):
        prev_block = chain[0]
        is_valid = True
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            prev_block_hash = self.get_hash_of_block(prev_block)
            if prev_block_hash != current_block['prev_hash']:
                return False
            prev_proof = prev_block['proof']
            current_proof = current_block['proof']
            hashed_proof = hashlib.sha256(str(current_proof**10 - prev_proof**5).encode()).hexdigest()
            if hashed_proof[:6] != '000000':
                return False
            prev_block = current_block
            block_index += 1
        return True

    def insert_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        prev_block = self.get_last_block()
        return prev_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        longest_chain = None
        longest_chain_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                chain = response.json()['chain']
                length_chain = response.json()['Number of blocks']
                if self.check_valid_chain(chain) and length_chain > longest_chain_length:
                    longest_chain = chain
                    longest_chain_length = length_chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# Step - 2 Mining our Block and creating the flask app

# Creating the Flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an instance of the Blockchain
blockchain = Blockchain()

# Node Address
node_address = str(uuid4()).replace('-', '')

# Mining a new block and adding it to our blockchain
@app.route('/mine_block', methods=['GET'])
def mine_a_block():
    previous_block = blockchain.get_last_block()
    previous_proof = previous_block['proof']
    current_proof = blockchain.proof_of_work(previous_proof)
    hash_of_previous_block = blockchain.get_hash_of_block(previous_block)
    blockchain.insert_transaction('Coinbase', node_address, 10)
    newly_added_block = blockchain.add_block_to_chain(current_proof, hash_of_previous_block)
    response = {'message': 'Congratulations, you\'ve successfully mined a block!', **newly_added_block}
    return jsonify(response), 200

# Getting our blockchain
@app.route('/get_chain', methods=['GET'])
def get_blockchain():
    response = {
        'chain': blockchain.chain,
        'Number of blocks': len(blockchain.chain)
    }
    return jsonify(response), 200

# Checking if our Blockchain is valid, i.e. not hasn't been tampered with
@app.route('/is_valid', methods=['GET'])
def check_if_valid():
    response = {'Is Blockchain Valid' : blockchain.check_valid_chain(blockchain.chain)}
    return jsonify(response), 200

# Endpoint to add a transaction to our list of transactions
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    valid = True
    keys = ['sender', 'receiver', 'amount']
    # Checking if the json if in correct format
    for key in data:
        if key not in keys:
            valid = False
            break
    if not valid:
        response = {'message': 'Please check the transaction again!'}
        return jsonify(response), 400
    else:
        index = blockchain.insert_transaction(**data)
        response = {'message': f'Your transaction would be added to block {index}'}
        return jsonify(response), 201


# Step - 3 Decentralizing our blockchain

# Adding nodes to our network
@app.route('/add_nodes', methods=['POST'])
def add_node_to_network():
    json = request.get_json()
    if 'nodes' in json and len(json['nodes']) > 0:
        nodes = json['nodes']
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'The nodes have been added to the Blockchain. Currently, connected nodes are: ',
                    'nodes': list(blockchain.nodes)}
        return jsonify(response), 201
    else:
        response = {'message': 'No nodes specified'}
        return jsonify(response), 400

# Replacing the chain with the longest chain in the network
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_replace_required = blockchain.replace_chain()
    if is_replace_required:
        response = {'message': 'The blockchain was replaced by the longest chain in the network',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The chain is the updated chain',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(port=5002, debug=True)
