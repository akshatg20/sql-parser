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

def index_graduation_year(years_with_ids):
    """
    Sorts the graduation years and returns two things:
    1. A list of student IDs sorted by graduation year.
    2. A dictionary where the keys are unique graduation years and the values are the start index of the corresponding year in the sorted list.

    This method can be used to create an index on graduation year for a list of students.

    :param years_with_ids: List of tuples in the form (graduation_year, student_id)
    :return: sorted_ids, year_start_index
    """
    
    # Sort the list of tuples based on the graduation year (first element of the tuple)
    sorted_years_with_ids = sorted(years_with_ids, key=lambda x: x[0])
    
    # Extract the sorted IDs
    sorted_ids = [item[1] for item in sorted_years_with_ids]
    
    # Create a dictionary to track the start index of each unique graduation year
    year_start_index = {}
    for i, (year, _) in enumerate(sorted_years_with_ids):
        if year not in year_start_index:
            year_start_index[year] = i  # Record the first occurrence of the graduation year

    return sorted_ids, year_start_index


# Example usage:
years_with_ids = [(2023, 1), (2022, 2), (2023, 3), (2021, 4), (2022, 5)]
sorted_ids, year_start_index = index_graduation_year(years_with_ids)

print("Sorted IDs:", sorted_ids)
print("Year Start Index:", year_start_index)



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