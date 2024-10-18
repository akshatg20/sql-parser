def longest_common_prefix(word1, word2):
    min_length = min(len(word1), len(word2))  
    common_prefix_length = 0
    for i in range(min_length):
        if word1[i] == word2[i]:
            common_prefix_length += 1
        else:
            break 
    return word1[:common_prefix_length]

class CollapsedTrieNode:
    def __init__(self, word = ""):
        self.children  = []
        self.word = word
        self.word_count= 0
        self.word_ids = []
        self.prefix_count = 0
        self.rank = -1

# Note : 1. First sort the data based on name. This will help keep the dictionary sorted by keys always
# The intuition is that with collapsed tree number of nodes will decrease significantly and that will help during the
# composite query
class CollapsedTrie:
    def __init__(self):
        self.root = CollapsedTrieNode()

    def insert(self, inserted_word, inserted_word_id):
        current_node = self.root
        match_count = 0
        inserted_word_size = len(inserted_word)
        last_match_count = 0 # To check if we made any progress in the current outer loop iteration
        while match_count < inserted_word_size:
            for child in current_node.children:
                current_word = child.word
                if inserted_word[match_count:]==child.word:
                    current_node = child
                    current_node.word_count += 1
                    current_node.word_ids.append(inserted_word_id)
                    match_count += len(child.word)
                    break
                elif inserted_word[match_count:].startswith(child.word):
                    current_node = child
                    match_count += len(child.word)
                    break
                elif inserted_word[match_count] == child.word[0]:
                    # some part of the word is common while some end words dont match
                    # split the current node
                    prefix = longest_common_prefix(inserted_word[match_count:], child.word)
                    match_count+=len(prefix)
                    current_node = child

                    split_node = CollapsedTrieNode(current_node.word[len(prefix):])
                    split_node.children = current_node.children
                    split_node.word_count = current_node.word_count
                    split_node.word_ids = current_node.word_ids
                    # print the split node
 

                    current_node.word = prefix
                    current_node.word_count = 0
                    current_node.word_ids = []
                    current_node.children = []
                    current_node.children.append(split_node)
                    inserted_node = CollapsedTrieNode(inserted_word[match_count:])
                    inserted_node.word_count = 1
                    inserted_node.word_ids = [inserted_word_id]
                    current_node.children.append(inserted_node)
                    return

            # If we didn't make any progress, then insert a new node without splitting
            if match_count == last_match_count:
                inserted_node = CollapsedTrieNode(inserted_word[match_count:])
                inserted_node.word_count = 1
                inserted_node.word_ids = [inserted_word_id]
                current_node.children.append(inserted_node)
                match_count += len(inserted_word[match_count:])
            last_match_count = match_count

    def search(self, word):
        current_node = self.root
        match_count = 0
        word_size = len(word)
        last_match_count = 0
        while match_count < word_size:
            for child in current_node.children:
                key = child.word
                if word[match_count:]==child.word:
                    current_node = child
                    match_count += len(child.word)
                    break
                elif word[match_count:].startswith(child.word):
                    current_node = child
                    match_count += len(child.word)
                    break
                elif word[match_count] == key[0]:
                    # some part of the word is common while some end words dont match
                    prefix = longest_common_prefix_length(word[match_count:], child.word)
                    match_count+=len(prefix)
                    current_node = child
                    return current_node

            # If we didn't make any progress, then return None
            if last_match_count == match_count:
                return current_node if current_node == self.root else None
            last_match_count = match_count
        return current_node

    # This method will assign a rank to each prefix in the trie based on their order in the dictionary of all preixes present in the trie
    def rank_trie(self, node, rank=0):
        """
        Performs a DFS to calculate prefix_count and assign a rank to each node in the Trie.
        The rank represents the order of the word in the Trie, starting from 0 for the first word.
        """
        word_count = node.word_count
        next_rank = rank + word_count
        for child_node in node.children:
            next_rank += self.rank_trie(child_node, next_rank) 
            word_count += child_node.prefix_count

        node.prefix_count = word_count
        node.rank = rank 
        return word_count

    # This method can be used to find the layout of records on the disk 
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
            word_ids.extend(current_node.word_ids)
            # TODO: To get rid of the sorted step here, we need to sort the records by name in the beginning before starting the insertions
            for child in reversed(current_node.children):
                stack.append(child)
        return word_ids


    # This method will return the disk locations of all the records matching the sql query with only the name filter LIKE 'prefix%'
    # def disk_records_locations(self, prefix):

    def print(self):
        if not self.root:
            return

        queue = [(self.root, 0)] 
        while queue:
            level_nodes = []  # Store nodes at the current level
            next_level_queue = []  # Queue for the next level

            while queue:
                node, level = queue.pop(0)
                level_nodes.append(node)

                # Check if the node has children before enqueuing for the next level
                if node.children: 
                    for child in node.children:
                        next_level_queue.append((child, level + 1))

            # Print nodes at the current level
            print("  " * level + " ".join([f"{node.word}({node.word_ids})" for node in level_nodes]))


            # Move to the next level
            queue = next_level_queue 

            # Stop if there are no more nodes to process (no children)
            if not queue:
                break








# Example usage
trie = CollapsedTrie()
words = [["apple",1] , ["appke", 2], ["appket", 6], ["app", 4], ["ape", 5 ], ["appl", 3], ["zoho", 10] ]
words.sort()
for word in words:
    trie.insert(word[0], word[1])
    # trie.print()
    # print("------------")

# trie.print()
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

print("Disk layout: ")
print(trie.disk_records_map())

# print(trie.find_names_with_prefix("app"))
# print(trie.find_names_with_prefix("ape"))