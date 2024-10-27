class CollapsedTrieNode:
	def __init__(self, word = ""):
		self.children  = []
		self.word = word
		self.word_count= 0
		self.word_ids = []
		self.prefix_count = 0
		self.rank = -1
		self.year_start_index = {}

# Note : 1. First sort the data based on name. This will help keep the dictionary sorted by keys always
# The intuition is that with collapsed tree number of nodes will decrease significantly and that will help during the
# composite query
class CollapsedTrie:
	# le_dict = {}
	# ge_dict = {}

	def __init__(self, le_dict, ge_dict):
		self.root = CollapsedTrieNode()
		self.le_dict = le_dict
		self.ge_dict = ge_dict

	def longest_common_prefix(self, word1, word2):
		min_length = min(len(word1), len(word2))  
		common_prefix_length = 0
		for i in range(min_length):
			if word1[i] == word2[i]:
				common_prefix_length += 1
			else:
				break 
		return word1[:common_prefix_length]

	def index_graduation_year_collapsed(self, years_with_ids):
		"""
		Sorts the graduation years and returns two things:
		1. A list of student IDs sorted by graduation year.
		2. A dictionary where the keys are unique graduation years and the values are the start index of the corresponding year in the sorted list.
	
		This method can be used to create an index on graduation year for a list of students.
	
		:param years_with_ids: List of tuples in the form ( student_id, graduation_year)
		:return: sorted_ids, year_start_index
		"""
	
		# Sort the list of tuples based on the graduation year (second element of the tuple)
		sorted_years_with_ids = sorted(years_with_ids, key=lambda x: x[1])
	
		# Extract the sorted IDs
		sorted_ids = [item[0] for item in sorted_years_with_ids]
	
		year_start_index = {}
		for i, (_, year) in enumerate(sorted_years_with_ids):
			if year not in year_start_index:
				year_start_index[year] = (i, i)  # Record the first occurrence of the graduation year as (first_index, last_index)
			else:
				year_start_index[year] = (year_start_index[year][0], i)  # Update the last occurrence of the graduation year
	
		return sorted_ids, year_start_index

	def insert(self, inserted_word, inserted_word_id):
		current_node = self.root
		match_count = 0
		inserted_word_size = len(inserted_word)
		last_match_count = 0 # To check if we made any progress in the current outer loop iteration
		while match_count < inserted_word_size:
			for child in current_node.children:
				current_word = child.word
				if inserted_word[match_count:]==child.word:
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
				elif inserted_word[match_count] == child.word[0]:
					# some part of the word is common while some end words dont match
					# split the current node
					prefix = self.longest_common_prefix(inserted_word[match_count:], child.word)
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
				# print("wtf")
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
					prefix = self.longest_common_prefix_length(word[match_count:], child.word)
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
			# TODO: remove the year from the words ids list
			sorted_ids, year_start_index = self.index_graduation_year_collapsed(current_node.word_ids)
			current_node.year_start_index = year_start_index
			word_ids.extend(sorted_ids)
			for child in reversed(current_node.children):
				stack.append(child)
		return word_ids

	def pre_order_traversal(self, node, year, comparator, isPrefixQuery):
		if not node:
			return []
		block_ids = []
		print(node.year_start_index)

		if node.year_start_index:

			if comparator == '<=':
				if year > list(node.year_start_index.keys())[-1]:
					block_ids.extend(list(range(node.rank, node.rank + node.word_count)))
				elif year < list(node.year_start_index.keys())[0]:
					pass
				else: 
					valid_year = self.ge_dict[year]
					block_ids.extend(list(range(node.rank, node.rank + node.year_start_index[valid_year][1] + 1)))

				# for child in node.children:
				# 	block_ids.extend(self.pre_order_traversal(child, year, comparator))

			elif comparator == '>=':
				if year < list(node.year_start_index.keys())[0]:
					block_ids.extend(list(range(node.rank, node.rank + node.word_count)))
				elif year > list(node.year_start_index.keys())[-1]:
					pass
				else: 
					valid_year = self.le_dict[year]
					block_ids.extend(list(range(node.year_start_index[valid_year][0], node.rank + node.word_count)))

				# for child in node.children:
				# 	block_ids.extend(self.pre_order_traversal(child, year, comparator))

			else:
				valid_year = self.le_dict[year]
				if valid_year is not None:
					if year in node.year_start_index.keys():
						block_ids.extend(list(range(node.year_start_index[year][0], node.rank + node.year_start_index[year][1] + 1)))

		if isPrefixQuery:
			for child in node.children:
				block_ids.extend(self.pre_order_traversal(child, year, comparator, isPrefixQuery))

		return block_ids

	# This method will return the disk locations of all the records matching the sql query with the name filter LIKE 'prefix%' and year filter <=
	def disk_records_locations(self, prefix, year, comparator, isPrefixQuery):
		start_node = self.search(prefix)
		if not start_node:
			return []
		block_ids = self.pre_order_traversal(start_node, year, comparator, isPrefixQuery)
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
			print("  " * level + " ".join([f"{node.word}({node.word_ids}, {node.word_count})" for node in level_nodes]))
			# Move to the next level
			queue = next_level_queue 

			# Stop if there are no more nodes to process (no children)
			if not queue:
				break