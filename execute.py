# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_execute BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics

import YearIndex
import TrieIndex
import CollapsedTrieIndex


# Function to execute the year_index
def execute_year_index(year, comp, idx):
	# Reference the necessary indices and statistics
	idx_year, ge_list, le_list = idx[0], idx[3], idx[4]
	stats = idx[5]
	min_year, max_year, num_ids = int(stats[0]), int(stats[1]), int(stats[2])
	diskloc_list = []

	if comp == '<=':
		# If the year is less than the minimum year, return an empty list
		if year < min_year:
			return diskloc_list
		
		# If the year is greater than the maximum year, return all the indices
		if year >= max_year:
			for i in range(num_ids):
				diskloc_list.append(i)
			return diskloc_list
		
		# Otherwise calculate the valid year less than or equal to the given year
		valid_year = YearIndex.search_year(year, le_list)

		if valid_year is not None: 
			# Find the last occurence of the valid year using the index of the next valid year
			next_valid_year = YearIndex.search_year(valid_year+1, ge_list)

			# Find the appropiate index for the next valid year
			max_idx = 0
			if next_valid_year is None:
				max_idx = num_ids - 1
			else:
				max_idx = YearIndex.search_year(next_valid_year, idx_year) - 1

			# Append all the indices till the last occurence of the valid year
			for i in range(max_idx + 1):
				diskloc_list.append(i)

	elif comp == '>=':
		# If the year is greater than the maximum year, return an empty list
		if year > max_year:
			return diskloc_list

		# If the year is less than the minimum year, return all the indices
		if year <= min_year:
			for i in range(num_ids):
				diskloc_list.append(i)
			return diskloc_list
		
		# Otherwise calculate the valid year greater than or equal to the given year
		valid_year = YearIndex.search_year(year, ge_list)

		if valid_year is not None:
			# Find the first occurence of the valid year using the index of the valid year
			curr_idx = YearIndex.search_year(valid_year, idx_year)
			max_idx = num_ids - 1

			# Append all the indices from the first occurence of the valid year till the end
			for i in range(curr_idx, max_idx+1):
				diskloc_list.append(i)

	else:
		# Check if the given year is valid or not
		valid_year = YearIndex.search_year(year, ge_list)

		if valid_year is not None and valid_year == year :
			# Find the first occurence of the year using the index of the valid year
			start_idx = YearIndex.search_year(year, idx_year)

			# Find the last occurence of the year using the index of the next valid year
			next_valid_year = YearIndex.search_year(valid_year+1, ge_list)
			end_idx = YearIndex.search_year(next_valid_year, idx_year)

			# Append all the indices from the first occurence of the year till the last occurence of the year
			for i in range(start_idx,end_idx+1):
				diskloc_list.append(i)

	return diskloc_list


# Function to execute trie_index
def execute_name_index(name, comp, idx):
	# Reference the necessary indices and statistics
	trie, stats = idx[1] , idx[5]
	max_name_len, min_name_len = stats[3], stats[4]

	diskloc_list = []

	# Check if the given name length is valid or not
	if len(name) < min_name_len or len(name) > max_name_len:
		return diskloc_list
	
	if comp == 'LIKE':
		prefix_name = name[1:-2]
		diskloc_list = trie.disk_records_locations(prefix_name)
	else:
		prefix_name = name[1:-1]
		diskloc_list = trie.disk_records_locations_exact(prefix_name)

	return diskloc_list

# Function to execute collapsed_trie_index
def execute_collapsed_trie_index(name, year, comp1, comp2, idx):
	# Reference the necessary indices and statistics
	collapsedtrie = idx[2]
	diskloc_list = []

	if comp1 == 'LIKE':
		prefix_name = name[1:-2]
		diskloc_list = collapsedtrie.disk_records_locations(prefix_name, year, comp2, True)
	else:
		prefix_name = name[1:-1]
		diskloc_list = collapsedtrie.disk_records_locations(prefix_name, year, comp2, False)

	return diskloc_list

################################
# Non Editable Region Starting #
################################
def my_execute( clause, idx ):
################################
#  Non Editable Region Ending  #
################################

	diskloc_list = []

	# for simple query
	if len(clause) == 1:
		# In case of queries like "WHERE year [comp] [YEAR_VALUE]"
		if clause[0][0] == 'year':
			year = int(clause[0][2])
			diskloc_list = execute_year_index(year, clause[0][1],idx)

		# In case of queries like "WHERE name [comp] [NAME_VALUE]"
		elif clause[0][0] == 'name':
			name = clause[0][2]
			diskloc_list = execute_name_index(name, clause[0][1], idx)

	# for joint query
	else :
		# In case of queries like "WHERE name [comp] [NAME_VALUE] AND year [comp] [YEAR_VALUE]"
		name = clause[0][2]
		year = int(clause[1][2])
		diskloc_list = execute_collapsed_trie_index(name, year, clause[0][1], clause[1][1], idx)


	# Use this method to take a WHERE clause specification
	# and return results of the resulting query
	# clause is a list containing either one or two predicates

	# Each predicate is itself a list of 3 objects, column name, comparator and value
	# idx contains the packaged variable returned by the my_index method
	
	# THE METHOD MUST RETURN A SINGLE LIST OF INDICES INTO THE DISK MAP
	return diskloc_list