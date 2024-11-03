import YearIndex


class CollapsedTrieNode:
    def __init__(self, word=""):
        self.children = []
        self.word = word
        self.word_count = 0
        self.word_ids = []
        self.prefix_count = 0
        self.rank = -1
        self.year_start_index = []

# Note : 1. First sort the data based on name. This will help keep the dictionary sorted by keys always
# The intuition is that with collapsed tree number of nodes will decrease significantly and that will help during the
# composite query


class CollapsedTrie:
    # le_dict = {}
    # ge_dict = {}

    def __init__(self):
        self.root = CollapsedTrieNode()

    def longest_common_prefix(self, word1, word2):
        min_length = min(len(word1), len(word2))
        common_prefix_length = 0
        for i in range(min_length):
            if word1[i] == word2[i]:
                common_prefix_length += 1
            else:
                break
        return word1[:common_prefix_length]

    def index_graduation_year_collapsed(self, years_with_ids, gap=0):
        """
        Sorts the graduation years and returns two things:
        1. A list of student IDs sorted by graduation year.
        2. A list of triples where the first element are unique graduation years and the second, third elements are the start and end index of the corresponding year in the sorted list.

        This method can be used to create an index on graduation year for a list of students.

        :param years_with_ids: List of tuples in the form ( student_id, graduation_year)
        :return: sorted_ids, year_start_index
        """

        # Sort the list of tuples based on the graduation year (second element of the tuple)
        sorted_years_with_ids = sorted(years_with_ids, key=lambda x: x[1])

        # Extract the sorted IDs
        sorted_ids = [item[0] for item in sorted_years_with_ids]

        year_start_index = []
        year_encountered = set()

        for i, (_, year) in enumerate(sorted_years_with_ids):
            if year not in year_encountered:
                year_encountered.add(year)
                # Record the first occurrence of the graduation year as (year, first_index, last_index)
                year_start_index.append((year, i+gap))

        return sorted_ids, year_start_index

    def insert(self, inserted_word, inserted_word_id):
        current_node = self.root
        match_count = 0
        inserted_word_size = len(inserted_word)
        # To check if we made any progress in the current outer loop iteration
        last_match_count = 0
        while match_count < inserted_word_size:
            for child in current_node.children:
                current_word = child.word
                if inserted_word[match_count:] == child.word:
                    # print("complete match")
                    current_node = child
                    current_node.word_count += 1
                    current_node.word_ids.append(inserted_word_id)
                    match_count += len(child.word)
                    break
                elif inserted_word[match_count:].startswith(child.word):
                    # print("complete partial match")
                    current_node = child
                    match_count += len(child.word)
                    break

                elif child.word.startswith(inserted_word[match_count:]):
                    current_node = child

                    split_node = CollapsedTrieNode(
                        current_node.word[len(inserted_word[match_count:]):])
                    split_node.children = current_node.children
                    split_node.word_count = current_node.word_count
                    split_node.word_ids = current_node.word_ids

                    current_node.word = inserted_word[match_count:]
                    current_node.word_count = 1
                    current_node.word_ids = [inserted_word_id]
                    current_node.children = []
                    current_node.children.append(split_node)

                elif inserted_word[match_count] == child.word[0]:
                    # some part of the word is common while some end words dont match
                    # split the current node
                    prefix = self.longest_common_prefix(
                        inserted_word[match_count:], child.word)
                    match_count += len(prefix)
                    current_node = child

                    split_node = CollapsedTrieNode(
                        current_node.word[len(prefix):])
                    split_node.children = current_node.children
                    split_node.word_count = current_node.word_count
                    split_node.word_ids = current_node.word_ids
                    # print the split node

                    current_node.word = prefix
                    current_node.word_count = 0
                    current_node.word_ids = []
                    current_node.children = []
                    current_node.children.append(split_node)
                    inserted_node = CollapsedTrieNode(
                        inserted_word[match_count:])
                    inserted_node.word_count = 1
                    inserted_node.word_ids = [inserted_word_id]
                    current_node.children.append(inserted_node)
                    return

            # If we didn't make any progress, then insert a new node without splitting
            if match_count == last_match_count:
                # print("wtf")
                inserted_node = CollapsedTrieNode(inserted_word[match_count:])
                inserted_node.word_count = 1
                inserted_node.word_ids = [inserted_word_id]
                current_node.children.append(inserted_node)
                match_count += len(inserted_word[match_count:])
            last_match_count = match_count

    # function to create a less_than and greater_than dictionary for the years at each node
    def set_valid_subtree_years(self, node):
        if not node:
            return []

        year_list = list(node.year_start_index.keys())
        for child in node.children:
            year_list.extend(self.set_valid_subtree_years(child))
        year_list = list(set(year_list))
        node.le_dict, node.ge_dict = YearIndex.create_year_bounds(year_list)
        return year_list

    def search(self, word):
        current_node = self.root
        match_count = 0
        word_size = len(word)
        last_match_count = 0
        while match_count < word_size:
            for child in current_node.children:
                key = child.word
                if word[match_count:] == child.word:
                    current_node = child
                    match_count += len(child.word)
                    break
                elif word[match_count:].startswith(child.word):
                    current_node = child
                    match_count += len(child.word)
                    break
                elif word[match_count] == key[0]:
                    # some part of the word is common while some end words dont match
                    prefix = self.longest_common_prefix(
                        word[match_count:], child.word)
                    match_count += len(prefix)
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
    def disk_records_map(self, gap=0):
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
            # TODO: remove the year from the words ids list
            sorted_ids, year_start_index = self.index_graduation_year_collapsed(
                current_node.word_ids, gap)
            current_node.year_start_index = year_start_index
            word_ids.extend(sorted_ids)
            for child in reversed(current_node.children):
                stack.append(child)
        return word_ids

    def pre_order_traversal(self, node, year, comparator, isPrefixQuery):
        if not node:
            return []
        block_ids = []
        # print("Current node being tested", node.word)
        # print("Current year being tested", year)
        # print("Dictionary of years present at current node", node.year_start_index)

        if node.year_start_index:

            if comparator == '<=':
                # if year > list(node.year_start_index.keys())[-1]:
                if year > node.year_start_index[-1][0]:
                    block_ids.extend(
                        list(range(node.rank, node.rank + node.word_count)))
                # elif year < list(node.year_start_index.keys())[0]:
                elif year < node.year_start_index[0][0]:
                    pass
                else:
                    valid_year_idx = YearIndex.upper_bound(
                        node.year_start_index, year+1)
                    if valid_year_idx is None:
                        block_ids.extend(
                            list(range(node.rank, node.rank + node.word_count)))
                    else:
                        block_ids.extend(
                            list(range(node.rank, node.rank + valid_year_idx)))

                # for child in node.children:
                # 	block_ids.extend(self.pre_order_traversal(child, year, comparator))

            elif comparator == '>=':
                # if year < list(node.year_start_index.keys())[0]:
                if year < node.year_start_index[0][0]:
                    block_ids.extend(
                        list(range(node.rank, node.rank + node.word_count)))
                # elif year > list(node.year_start_index.keys())[-1]:
                elif year > node.year_start_index[-1][0]:
                    pass
                else:
                    valid_year_idx = YearIndex.upper_bound(
                        node.year_start_index, year)
                    block_ids.extend(
                        list(range(node.rank + valid_year_idx, node.rank + node.word_count)))

                # for child in node.children:
                # 	block_ids.extend(self.pre_order_traversal(child, year, comparator))

            else:
                valid_year_idx = YearIndex.search_year(
                    year, node.year_start_index)
                if valid_year_idx is not None:
                    next_valid_year_idx = YearIndex.upper_bound(
                        node.year_start_index, year + 1)
                    if next_valid_year_idx is None:
                        block_ids.extend(
                            list(range(node.rank + valid_year_idx, node.rank + node.word_count)))
                    else:
                        block_ids.extend(
                            list(range(node.rank + valid_year_idx, node.rank + next_valid_year_idx)))

        if isPrefixQuery:
            for child in node.children:
                block_ids.extend(self.pre_order_traversal(
                    child, year, comparator, isPrefixQuery))

        return block_ids

    # This method will return the disk locations of all the records matching the sql query with the name filter LIKE 'prefix%' and year filter <=
    def disk_records_locations(self, prefix, year, comparator, isPrefixQuery):
        start_node = self.search(prefix)
        if not start_node:
            return []
        block_ids = self.pre_order_traversal(
            start_node, year, comparator, isPrefixQuery)
        return block_ids

    # This method will return the disk locations of all the records matching the sql query with only the name filter LIKE 'prefix%'
    def disk_records_locations_name(self, prefix):
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

    # This method will return the disk locations of all the records matching the sql query with only the name filter = 'name'
    def disk_records_locations_exact_name(self, name):
        """
        For SQL queries using the = 'name' pattern, this function finds the block IDs on the disk
        that correspond to the records whose names exactly match the given name.

        It first locates the node matching the name in a prefix tree (Trie) structure. If the node exists,
        it returns the block IDs of the records associated with that name, based on the node's rank and prefix count.
        """
        node = self.search(name)
        if not node:
            return []
        block_ids = []
        for i in range(node.word_count):
            block_ids.append(node.rank + i)
        return block_ids

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
            print("  " * level + " ".join(
                [f"{node.word}({node.word_ids}, {node.word_count})" for node in level_nodes]))

            # Move to the next level
            queue = next_level_queue

            # Stop if there are no more nodes to process (no children)
            if not queue:
                break


