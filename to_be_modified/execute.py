# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_execute BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics

##################################################### TRIE DEFINITION #################################################################

# global le_dict, ge_dict

import CollapsedTrieIndex

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
	collapsedtrie = idx[2]
	ge_dict = idx[3]
	le_dict = idx[4]
	basic_stats = idx[5]

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

		if clause[0][1] == 'LIKE':
			prefix_name = name[1:-2]
			diskloc_list = collapsedtrie.disk_records_locations(prefix_name, year, clause[1][1], True)
		else:
			prefix_name = name[1:-1]
			diskloc_list = collapsedtrie.disk_records_locations(prefix_name, year, clause[1][1], False)

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