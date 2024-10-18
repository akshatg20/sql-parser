class TrieNode:
    def __init__(self):
        self.children = {}
        self.word_count = 0  # Tracks words ending at this node
        self.word_ids = []  # Stores word IDs of words that end at this node
        self.prefix_count = 0 # Tracks the number of words that share the prefix ending at the current node
        self.rank = -1 # Tracks the rank of the word in the trie, starting from 0 for the first word.

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, word_id):
        current_node = self.root
        for char in word:
            if char not in current_node.children:
                current_node.children[char] = TrieNode()
            current_node = current_node.children[char]
        current_node.word_count += 1  # Word ends at this node
        current_node.word_ids.append(word_id)  # Store the word ID

    def search(self, word):
        current_node = self.root
        for char in word:
            if char not in current_node.children:
                return None
            current_node = current_node.children[char]
        return current_node

    # This method will be used to find the layout of records on the disk 
    def disk_records_map(self):
        """
        Performs a preorder traversal starting from the node reached by the given prefix.
        Returns a list of word IDs encountered during traversal.
        """
        node = self.root
        if not node:
            return []  # Prefix not found

        word_ids = []
        stack = [node]

        while stack:
            current_node = stack.pop()
            if current_node.word_count > 0:
                word_ids.extend(current_node.word_ids)
            # TODO: To get rid of the sorted step here, we need to sort the records by name in the beginning before starting the insertions
            for char in sorted(current_node.children.keys(), reverse=True):
                stack.append(current_node.children[char])

        return word_ids

    # This method will assign a rank to each prefix in the trie based on their order in the dictionary of all preixes present in the trie
    def rank_trie(self, node, rank=0):
        """
        Performs a DFS to calculate prefix_count and assign a rank to each node in the Trie.
        The rank represents the order of the word in the Trie, starting from 0 for the first word.
        """
        count = node.word_count
        next_rank = rank + count
        # TODO: To get rid of the sorted step here, we need to sort the records by name in the beginning before starting the insertions
        for key in sorted(node.children.keys()):
            child_node = node.children[key]
            next_rank += self.rank_trie(child_node, next_rank) 
            count += child_node.prefix_count

        node.prefix_count = count
        node.rank = rank 
        return count
    
    # This method will return the disk locations of all the records matching the sql query with only the name filter LIKE 'prefix%'
    def disk_records_locations(self, prefix):
        """
        For SQL queries using the LIKE 'prefix%' pattern, this function finds the block IDs on the disk
        that correspond to the records whose names begin with the given prefix.
        
        It first locates the node matching the prefix in a prefix tree (Trie) structure. If the node exists,
        it returns the block IDs of the records associated with that prefix, based on the node's rank and prefix count.
        """
        node = self.search(prefix)
        if not node:
            return []
        block_ids = []
        for i in range(node.prefix_count):
            block_ids.append(node.rank + i)
        return block_ids



# Example usage
trie = Trie()
trie.insert("apple", 1)
trie.insert("appke", 2)
trie.insert("appket", 6)
trie.insert("appl", 3)
trie.insert("app", 4)
trie.insert("ape",5)
trie.insert("zoho", 10)
trie.rank_trie(trie.root)
# print the prefix count and rank of apple
def print_word_rank(trie, word):
    node = trie.search(word)
    if node:
        print(f"{word}: {node.rank}")

print_word_rank(trie, "app")
print_word_rank(trie, "apple")
print_word_rank(trie, "appke")
print_word_rank(trie, "appket")
print_word_rank(trie, "ape")
print_word_rank(trie, "zoho")
print(trie.disk_records_map())
# print(trie.disk_records_locations("app"))
# print(trie.disk_records_locations("ape"))