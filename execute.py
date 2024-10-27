# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_execute BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics

##################################################### TRIE DEFINITION #################################################################

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
		# print(prefix)
		# print(block_ids)
		return block_ids
	
	# This method will return the disk locations of all the records matching the sql query with only the name filter = 'name'
	def disk_records_locations_exact(self, name):
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

def longest_common_prefix(word1, word2):
	min_length = min(len(word1), len(word2))  
	common_prefix_length = 0
	for i in range(min_length):
		if word1[i] == word2[i]:
			common_prefix_length += 1
		else:
			break 
	return word1[:common_prefix_length]

def index_graduation_year(years_with_ids):
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
					print("complete match")
					current_node = child
					current_node.word_count += 1
					current_node.word_ids.append(inserted_word_id)
					match_count += len(child.word)
					break
				elif inserted_word[match_count:].startswith(child.word):
					print("complete partial match")
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
				print("wtf")
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
			# TODO: remove the year from the words ids list
			sorted_ids, year_start_index = index_graduation_year(current_node.word_ids)
			current_node.year_start_index = year_start_index
			word_ids.extend(sorted_ids)
			for child in reversed(current_node.children):
				stack.append(child)
		return word_ids

	def pre_order_traversal(self, node, year):
		if not node:
			return []
		block_ids = []
		print(node.year_start_index)
		if year > list(node.year_start_index.keys())[-1]:
			block_ids.extend(list(range(node.rank, node.rank + node.word_count)))
		elif year < list(node.year_start_index.keys())[0]:
			pass
		else: 
			block_ids.extend(list(range(node.rank, node.rank + node.year_start_index[year][1] + 1)))

		for child in node.children:
			block_ids.extend(self.pre_order_traversal(child, year))
		return block_ids

	# This method will return the disk locations of all the records matching the sql query with the name filter LIKE 'prefix%' and year filter <=
	def disk_records_locations(self, prefix, year):
		start_node = self.search(prefix)
		if not start_node:
			return []
		block_ids = self.pre_order_traversal(start_node, year)
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


##################################################### TRIE DEFINITION #################################################################


################################
# Non Editable Region Starting #
################################
def my_execute( clause, idx ):
################################
#  Non Editable Region Ending  #
################################
	# print(clause)
	# print("done with printing the joint clause")
	idx_year_start = idx[0]  
	trie = idx[1]
	ge_dict = idx[2]
	le_dict = idx[3]
	basic_stats = idx[4]

	min_year = int(basic_stats[0])
	max_year = int(basic_stats[1])
	num_ids = int(basic_stats[2])
	  
	# print(type(trie))

	diskloc_list = []

	# for predicate in clause:
	if len(clause) == 1:
		predicate = clause[0]
		# print(predicate)
		# print(f"length of predicate = {len(predicate)}")
		if len(predicate) == 1:
			if predicate[0] == 'year':

				year = int(predicate[2])

				if predicate[1] == '<=':
					valid_year = le_dict[year]
					if valid_year is not None: 
						# continue
					# else:
						next_valid_year = ge_dict[valid_year+1]
						max_idx = 0

						if next_valid_year is None:
							max_idx = num_ids - 1
						else:
							max_idx = idx_year_start[next_valid_year] - 1

						for i in range(max_idx + 1):
							diskloc_list.append(i)

				elif predicate[1] == '>=':
					valid_year = ge_dict[year]
					if valid_year is not None:
						# continue
					# else:
						curr_idx = idx_year_start[valid_year]
						max_idx = num_ids - 1
						for i in range(curr_idx, max_idx+1):
							diskloc_list.append(i)

				else :
					valid_year = ge_dict[year]
					if valid_year is not None and valid_year == year :
						# continue
						next_valid_year = ge_dict[year+1]
						start_idx = idx_year_start[year]
						end_idx = idx_year_start[next_valid_year]
						for i in range(start_idx,end_idx+1):
							diskloc_list.append(i)

			elif predicate[0] == 'name':

				name = predicate[2]

				if predicate[1] == 'LIKE':
					prefix_name = name[1:-2]
					diskloc_list = trie.disk_records_locations(prefix_name)
					# print(prefix_name)
					# print(diskloc_list)
				else:
					prefix_name = name[1:-1]
					diskloc_list = trie.disk_records_locations_exact(prefix_name)

	else :
		name = clause[0][2]
		year = int(clause[1][2])
		
		# print(clause)
		# print("Done with printing the predicate")
		# name = predicate[2]
		# continue

	# Use this method to take a WHERE clause specification
	# and return results of the resulting query
	# clause is a list containing either one or two predicates

	# Each predicate is itself a list of 3 objects, column name, comparator and value
	# idx contains the packaged variable returned by the my_index method
	
	# THE METHOD MUST RETURN A SINGLE LIST OF INDICES INTO THE DISK MAP
	return diskloc_list