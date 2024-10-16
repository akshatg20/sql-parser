class TrieNode:
    def __init__(self):
        self.children = {}
        self.end_of_word_count = 0  # Tracks words ending at this node
        self.word_ids = []  # Stores word IDs of words that end at this node

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

# Example usage
trie = Trie()
trie.insert("apple", 1)
trie.insert("appke", 2)
trie.insert("appket", 6)
trie.insert("appl", 3)
trie.insert("app", 4)
trie.insert("ape",5)

print(trie.prefix_preorder_traversal("app"))  
