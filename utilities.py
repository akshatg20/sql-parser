class TrieNode:
    def __init__(self):
        self.children = {}
        self.end_of_word_count = 0  # Tracks words ending at this node
        self.word_ids = []  # Stores word IDs of words that end at this node
        self.prefix_count = 0 # Tracks the number of words that share the prefix ending at the current node
        self.rank = 0 # Tracks the rank of the word in the trie, starting from 0 for the first word.

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, word_id):
        current_node = self.root
        for char in word:
            if char not in current_node.children:
                current_node.children[char] = TrieNode()
            current_node = current_node.children[char]
        current_node.end_of_word_count += 1  # Word ends at this node
        current_node.word_ids.append(word_id)  # Store the word ID

    def search(self, word):
        current_node = self.root
        for char in word:
            if char not in current_node.children:
                return None
            current_node = current_node.children[char]
        return current_node

    def prefix_preorder_traversal(self, prefix):
        """
        Performs a preorder traversal starting from the node reached by the given prefix.
        Returns a list of word IDs encountered during traversal.
        """
        node = self.search(prefix)
        if not node:
            return []  # Prefix not found

        word_ids = []
        stack = [node]

        while stack:
            current_node = stack.pop()
            if current_node.end_of_word_count > 0:
                word_ids.extend(current_node.word_ids)

            for char in sorted(current_node.children.keys(), reverse=True):
                stack.append(current_node.children[char])

        return word_ids


    def dfs(self, node, rank=0):
        """
        Performs a DFS to calculate prefix_count and assign a rank to each node in the Trie.
        The rank represents the order of the word in the Trie, starting from 0 for the first word.
        """
        count = node.end_of_word_count
        next_rank = rank + count
        for key in sorted(node.children.keys()):
            child_node = node.children[key]
            next_rank += self.dfs(child_node, next_rank) 
            count += child_node.prefix_count

        node.prefix_count = count
        node.rank = rank 
        return count
    
    def find_names_with_prefix(self, prefix):
        """
        For sql queries with name name filter, this function finds the block ids on the disk of the names that share the prefix given in the query
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
trie.dfs(trie.root)
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

print(trie.find_names_with_prefix("app"))
print(trie.find_names_with_prefix("ape"))