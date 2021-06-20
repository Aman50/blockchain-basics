# Creating a BlockChain

# Importing the required libraries
import datetime
import hashlib
import json
import flask
import Flask, jsonify


# Creating the BlockChain - Basically a class
class Blockchain:

    def __init__():
        self.chain = []
        self.add_block(proof=1, prev_hash='0') // Genesis
        block

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
            hash_value = hashlib.sha256(str(current_proof ** 3 - prev_proof ** 2).encode()).hexdigest()
            if (hash_value[:4] == '0000'):
                solution_found = True
            else:
                current_proof += 1
        return current_proof

    def get_hash_of_block(self, block):
        current_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(current_block.encode()).hexdigest()

    def check_valid_chain(self, chain):
        prev_block = chain[0]
        is_valid = true
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            prev_block_hash = self.get_hash_of_block(prev_block)
            if prev_block_hash != current_block['prev_hash']:
                return false

            prev_proof = prev_block['proof']
            current_proof = block['proof']
            hashed_proof = hashlib.sha256(str(current_proof ** 3 - prev_proof ** 2).encode()).hexdigest()
            if (hashed_proof[:4] != '0000'):
                return false
            prev_block = block
            block_index += 1
        return true