import hashlib
import random
from collections import defaultdict

class Block:
    def __init__(self, previous_hash, transactions, miner_id):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.miner_id = miner_id
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = str(self.previous_hash) + str(self.transactions) + str(self.miner_id)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self):
        return f"Block(miner: {self.miner_id}, hash: {self.hash[:10]}, prev_hash: {self.previous_hash[:10]})"

class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo_dict = defaultdict(list)  # To track unspent transaction outputs (UTXO)

    def add_block(self, block):
        self.chain.append(block)
        self.update_utxo(block.transactions)
        print(f"Added block by Miner {block.miner_id} to blockchain. Hash: {block.hash[:10]}")

    def update_utxo(self, transactions):
        for tx in transactions:
            for input_utxo in tx['inputs']:
                self.utxo_dict[input_utxo].append(tx['id'])

    def compare_utxo(self, private_chain):
        print("\nComparing UTXOs of private and public chains for double spending...")
        for block in private_chain.chain:
            for tx in block.transactions:
                for input_utxo in tx['inputs']:
                    if input_utxo in self.utxo_dict and self.utxo_dict[input_utxo][0] != tx['id']:
                        print(f"Double spending detected! UTXO {input_utxo} spent twice.")
                        return False  # Double spending detected
        print("No double spending detected.")
        return True

class Miner:
    def __init__(self, id):
        self.id = id

    def mine_block(self, previous_block, transactions):
        new_block = Block(previous_block.hash, transactions, self.id)
        print(f"Miner {self.id} mined a new block. Block Hash: {new_block.hash[:10]}")
        return new_block

class Network:
    def __init__(self, miners):
        self.public_blockchain = Blockchain()
        self.private_chain = Blockchain()
        self.miners = miners
        self.double_spend_utxo = None  # Store the UTXO for double spending

    def perform_mining(self, is_attacker=False, is_double_spend=False, short_chain=False):
        if is_attacker:
            print("\n--- Miner 2 is the attacker, performing 51% attack ---")
            return self.perform_51_attack(self.miners[2], is_double_spend, short_chain)
        else:
            print("\n--- No attacker in the network, miners mining honestly ---")
            return self.perform_honest_mining()

    def perform_honest_mining(self):
        previous_block = self.public_blockchain.chain[-1] if self.public_blockchain.chain else Block("0", [], "genesis")
        for i in range(5):  # Honest miners mine 5 blocks
            if i == 0 and self.double_spend_utxo:  # Use the same UTXO for double spending
                print("Honest miners spending the same UTXO as attacker for double spending!")
                transactions = [{'id': random.randint(1000, 9999), 'inputs': [self.double_spend_utxo]}]
            else:
                transactions = self.generate_honest_transactions()
            new_block = random.choice(self.miners).mine_block(previous_block, transactions)
            self.public_blockchain.add_block(new_block)
            previous_block = new_block

        print("\nPublic chain:")
        for block in self.public_blockchain.chain:
            print(block)

    def perform_51_attack(self, attacker_miner, is_double_spend=False, short_chain=False):
        previous_block = self.public_blockchain.chain[-1] if self.public_blockchain.chain else Block("0", [], "genesis")
        print(f"Attacker (Miner {attacker_miner.id}) starts creating private chain...")

        # Generate transactions, possibly with double spending
        num_blocks = 3 if short_chain else 6  # Short chain if the flag is set

        for i in range(num_blocks):  # Attacker mines a short or long chain
            if i == 0 and is_double_spend:
                # Introduce double spending in the first block of the private chain
                print("Attacker is performing double spending!")
                transactions = self.generate_double_spending_transactions()
            else:
                transactions = self.generate_fake_transactions()
            new_block = attacker_miner.mine_block(previous_block, transactions)
            self.private_chain.add_block(new_block)
            previous_block = new_block

        print("\nAttacker's private chain:")
        for block in self.private_chain.chain:
            print(block)

        # Honest miners mine only 3 blocks
        print("\nHonest miners are mining on the public chain...")
        previous_block = self.public_blockchain.chain[-1] if self.public_blockchain.chain else Block("0", [], "genesis")
        for i in range(3):  # Honest miners mine only 3 blocks
            if i == 0 and self.double_spend_utxo:  # Use the same UTXO for double spending
                print("Honest miners spending the same UTXO as attacker for double spending!")
                transactions = [{'id': random.randint(1000, 9999), 'inputs': [self.double_spend_utxo]}]
            else:
                transactions = self.generate_honest_transactions()
            new_block = random.choice(self.miners).mine_block(previous_block, transactions)
            self.public_blockchain.add_block(new_block)
            previous_block = new_block

        print("\nPublic chain:")
        for block in self.public_blockchain.chain:
            print(block)

    def safe_mode_detection(self):
        print("\n--- Safe Mode Detection ---")

        if len(self.private_chain.chain) >= 6:
            miner_ids = [block.miner_id for block in self.private_chain.chain[-6:]
                         ]
            if len(set(miner_ids)) == 1:
                print("51% Attack detected: Miner 2 created 6 consecutive blocks.")

        # Check for double spending by comparing UTXO
        if not self.public_blockchain.compare_utxo(self.private_chain):
            print("Attack rejected due to double spending.")
            return False

        print("No attack detected. System is in safe mode.")
        return True

    def generate_fake_transactions(self):
        return [{'id': random.randint(1000, 9999), 'inputs': [random.randint(100, 999)]}]

    def generate_honest_transactions(self):
        return [{'id': random.randint(1000, 9999), 'inputs': [random.randint(100, 999)]}]

    def generate_double_spending_transactions(self):
        # Generate a UTXO that will be double spent
        if not self.double_spend_utxo:
            self.double_spend_utxo = random.randint(100, 999)
        
        # Double spending transaction
        return [{'id': random.randint(1000, 9999), 'inputs': [self.double_spend_utxo]}]

# Simulate 51% Attack and Honest Mining Based on User Input

def main():
    # Setup the network with miners
    miners = [Miner(i) for i in range(5)]  # 5 miners
    network = Network(miners)

    print("Choose an option:")
    print("1) Case 1: No Attacker")
    print("2) Case 2: Miner 2 is the Attacker")
    print("3) Case 3: Miner 2 is the Attacker with Double Spending")
    print("4) Case 4: Miner 2 is the Attacker with Short Private Chain and Double Spending")

    user_choice = input("Enter your choice (1, 2, 3, or 4): ")

    if user_choice == "1":
        network.perform_mining(is_attacker=False)
        print("\nSafe Mode Detection:")
        network.safe_mode_detection()

    elif user_choice == "2":
        network.perform_mining(is_attacker=True, is_double_spend=False)
        print("\nSafe Mode Detection:")
        network.safe_mode_detection()

    elif user_choice == "3":
        network.perform_mining(is_attacker=True, is_double_spend=True)
        print("\nSafe Mode Detection:")
        network.safe_mode_detection()

    elif user_choice == "4":
        network.perform_mining(is_attacker=True, is_double_spend=True, short_chain=True)
        print("\nSafe Mode Detection:")
        network.safe_mode_detection()

    else:
        print("Invalid choice, please select either 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
