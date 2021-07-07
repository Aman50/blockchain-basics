# Creating a BlockChain

# Importing the required libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from urllib.parse import urlparse
from uuid import uuid4
import requests

# Step 1 - Creating the BlockChain - Basically a class
class Blockchain:
    """Class defining our blockchain"""
    def __init__(self):
        self.chain = []
        self.add_block_to_chain(proof=1, prev_hash='0') # Genesis Block

    # Add block is called after proof of work, block is mined.
    def add_block_to_chain(self, proof, prev_hash):
        block = {
            'proof': proof,
            'prev_hash': prev_hash,
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now())}

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

# Step - 2 Mining our Block and creating the flask app

# Creating the Flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an instance of the Blockchain
blockchain = Blockchain()

# Mining a new block and adding it to our blockchain
@app.route('/mine_block', methods=['GET'])
def mine_a_block():
    previous_block = blockchain.get_last_block()
    previous_proof = previous_block['proof']
    current_proof = blockchain.proof_of_work(previous_proof)
    hash_of_previous_block = blockchain.get_hash_of_block(previous_block)
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


# Step - 3 Decentralising our blockchain
# Running the app
app.run(port=9051, debug=True)
