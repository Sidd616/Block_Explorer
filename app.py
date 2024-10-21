from flask import Flask, render_template, request, jsonify
from hashlib import sha256
import random
from datetime import datetime

app = Flask(__name__)

# Define global variables
block_number = 0
chain = []  # Chain to store blocks


# Define classes and functions here
class Block:

    def __init__(self, block_number, nonce, data, prev_hash):
        self.block_number = block_number
        self.nonce = nonce
        self.data = data
        self.timestamp = datetime.now()
        self.prev_hash = prev_hash
        self.tx_root = self.calculate_tx_root()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.nonce}{self.tx_root}{self.prev_hash}{self.timestamp}".encode(
        )
        return sha256(block_string).hexdigest()

    def calculate_tx_root(self):
        dataList = list(self.data.split())
        hashList = []
        for data in dataList:
            hashList.append(sha256(data.encode()).hexdigest())
        return sha256("".join(hashList).encode()).hexdigest()


class Chain:
    instance = None

    @staticmethod
    def get_instance():
        if Chain.instance is None:
            Chain.instance = Chain()
        return Chain.instance

    def __init__(self):
        self.chain = []

    def create_genesis_block(self):
        return Block(
            999, "000000", "",
            "0000000000000000000000000000000000000000000000000000000000000000")

    @property
    def last_block(self):
        return self.chain[-1]

    def mine(self, nonce):
        solution = 1
        print('⛏️  mining...')
        while True:
            block_hash = sha256(str(nonce + solution).encode()).hexdigest()
            if block_hash[:4] == '0000':
                print(f'Solved: {solution}')
                return solution
            solution += 1

    def add_block(self, block):
        self.chain.append(block)

    def verify_transaction(self, transaction, sender_public_key, signature):
        # In this example, just assume transaction is always valid
        return True


chain_instance = Chain.get_instance()


# Define routes here
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reset_block_number", methods=["POST"])
def reset_block_number():
    global block_number
    block_number = 0  # Reset block number to 0
    chain_instance.chain.clear()  # Clear the chain
    return "Block number and chain reset successfully"


@app.route("/create_block", methods=["POST"])
def create_block():
    global block_number

    # Increment block number
    block_number += 1

    # Get previous block's hash
    prev_hash = chain_instance.last_block.hash if chain_instance.chain else "0000000000000000000000000000000000000000000000000000000000000000"

    data = ""
    # Create a new block
    new_block = Block(block_number, random.randint(0, 999999999), data,
                      prev_hash)

    # Add the new block to the chain
    chain_instance.add_block(new_block)

    # Construct HTML content for the new block
    block_html = f"""
    <div id="main-{new_block.block_number}" class="block">
        <p><strong>Block Number:</strong> {new_block.block_number}</p>
        <p><strong>Nonce:</strong> {new_block.nonce}</p>
        <label for="block-data-{new_block.nonce}"><strong>Data:</strong></label>
        <textarea id="block-data-{new_block.nonce}" class="block-data">{new_block.data}</textarea>
        <p id="prehash-{new_block.nonce}"><strong>Previous Hash:</strong> <br> <span class="hash-text greyfield">{new_block.prev_hash}</span></p>
        <p id="hash-{new_block.nonce}"><strong>Hash:</strong> <br> <span class="hash-text greyfield">{new_block.hash}</span></p>
        <p id="txhash-{new_block.nonce}"><strong>Tx_root:</strong> <br> <span class="hash-text greyfield">{new_block.tx_root}</span></p>
        <button class="mineBtn button-3" onclick="mineBlock({new_block.block_number}, {new_block.nonce})">Mine</button>
    </div>
    """

    return block_html


@app.route("/store_data", methods=["POST"])
def store_data():
    data = request.form.get("data")
    nonce = request.form.get("nonce")
    print(nonce)

    # Convert nonce to integer since nonce might be passed as a string from JavaScript
    if nonce is not None:
        nonce = int(nonce)
    else:
        print("nonce was found to be null")

    # Iterate through the blockchain to find the block with the matching nonce
    for i, block in enumerate(chain_instance.chain):
        # Convert block nonce to integer for comparison
        block_nonce = int(block.nonce)
        if block_nonce == nonce:
            # Update the data of the block with the matching nonce
            
            block.data = str(data)
            block.tx_root = block.calculate_tx_root()
            
            current_hash = block.hash
            
            # Recalculate the hash of the block
            block.hash = block.calculate_hash()

            # Fetch the previous block's hash
            prev_hash = chain_instance.chain[
                i -
                1].hash if i > 0 else "0000000000000000000000000000000000000000000000000000000000000000"

            block.prev_hash = prev_hash

            # Recalculate the hash of the block
            block.hash = block.calculate_hash()
            
            if(current_hash == block.hash):
                return jsonify("block up to date")

            return jsonify({
                "hash": block.hash,
                "data": block.data,
                "tx_root": block.tx_root,
                "prev": prev_hash
            })

    # If no block with the matching nonce is found, return an error message
    return jsonify("Block with the provided nonce not found")


if __name__ == "__main__":
    app.run(debug=True)
