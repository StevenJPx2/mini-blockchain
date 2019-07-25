import hashlib as hl
import datetime as dt
from flask import Flask, request
import requests
import json

node = Flask(__name__)

class Block:
	def __init__(self, index, timestamp, data, previous_hash):
		self.index = index
		self.timestamp = timestamp
		self.data = data
		self.previous_hash = previous_hash
		self.hash = self.hash_update()

	def hash_update(self):
		sha = hl.sha256((
			str(self.index)
		+ str(self.timestamp)
		+ str(self.data)
		+ str(self.previous_hash)).encode())

		return sha.hexdigest()
	
	def get_dict(self):
		dict_of_block = dict(self.__dict__)
		dict_of_block['index'] = str(dict_of_block['index'])
		dict_of_block['timestamp'] = str(dict_of_block['timestamp'])
		dict_of_block['data'] = str(dict_of_block['data'])

		return dict_of_block

create_first_block = lambda : Block(
	0, 
	dt.datetime.now(), 
	{"proof-of-work": 9,
	"transactions": None}, 
	"0"
)

miner_address = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"

blockchain = [create_first_block()]

this_nodes_transactions = []
peer_nodes = []
mining = True

@node.route('/txion', methods=['POST'])
def transaction():
	new_txion = request.get_json()
	this_nodes_transactions.append(new_txion)
	print("New transaction", 
	f"FROM: {new_txion['from'].encode('ascii', 'replace')}",
	f"TO: {new_txion['to'].encode('ascii', 'replace')}",
	f"AMOUNT: {new_txion['amount']}", sep='\n')
	
	return "Transaction submission successful\n"


@node.route('/blocks', methods=['GET'])
def get_blocks():
	chain_to_send = blockchain
	chain_to_send = list(map(lambda x: x.get_dict(), chain_to_send))
	chain_to_send = json.dumps(chain_to_send)
	return chain_to_send

def find_new_chains():
	other_chains = []
	for node_url in peer_nodes:
		block = requests.get(f'{node_url}/blocks').content
		block = json.loads(block)
		other_chains.append(block)

	return other_chains

def consensus():
	other_chains = find_new_chains()
	longest_chain = blockchain
	for chain in other_chains:
		if len(longest_chain) < len(chain):
			longest_chain = chain
	
	blockchain = longest_chain

def p_o_w(last_proof):
	incrementor = last_proof + 1
	if not (incrementor % 9 and incrementor % last_proof):
		incrementor += 1
	
	return incrementor 


@node.route('/mine', methods=['GET'])
def mine():
	last_block = blockchain[len(blockchain) - 1]
	last_proof = last_block.data['proof-of-work']
	proof = p_o_w(last_proof)
	this_nodes_transactions.append(
		{"from": "network", "to": miner_address, "amount": 1}
	)
	new_block_data = {
		"proof-of-work": proof,
		"transactions": list(this_nodes_transactions)
	}
	new_block_index = last_block.index + 1
	new_block_timestamp = this_timestamp = dt.datetime.now()
	last_block_hash = last_block.hash

	this_nodes_transactions[:] = []
	mined_block = Block(
		new_block_index,
		new_block_timestamp,
		new_block_data,
		last_block_hash
	)
	blockchain.append(mined_block)

	return json.dumps({
		"index": new_block_index,
		"timestamp": str(new_block_timestamp),
		"data": new_block_data,
		"hash": last_block_hash}) + "\n"

node.run()