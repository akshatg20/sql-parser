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
		if len(predicate) == 3:
			if predicate[0] == 'year':

				year = int(predicate[2])

				if predicate[1] == '<=':
					valid_year = YearIndex.search_year(year, le_dict)
					# valid_year = le_dict[year]
					if valid_year is not None: 
						# continue
					# else:
						next_valid_year = YearIndex.search_year(valid_year+1, ge_dict)
						# next_valid_year = ge_dict[valid_year+1]
						max_idx = 0

						if next_valid_year is None:
							max_idx = num_ids - 1
						else:
							max_idx = YearIndex.search_year(next_valid_year, idx_year_start) - 1
							# max_idx = idx_year_start[next_valid_year] - 1

						for i in range(max_idx + 1):
							diskloc_list.append(i)

				elif predicate[1] == '>=':
					valid_year = YearIndex.search_year(year, ge_dict)
					# valid_year = ge_dict[year]
					if valid_year is not None:
						# continue
					# else:
						curr_idx = YearIndex.search_year(valid_year, idx_year_start)
						# curr_idx = idx_year_start[valid_year]
						max_idx = num_ids - 1
						for i in range(curr_idx, max_idx+1):
							diskloc_list.append(i)

				else :
					valid_year = YearIndex.search_year(year, ge_dict)
					# valid_year = ge_dict[year]
					if valid_year is not None and valid_year == year :
						# continue
						next_valid_year = YearIndex.search_year(valid_year+1, ge_dict)
						# next_valid_year = ge_dict[year+1]
						start_idx = YearIndex.search_year(year, idx_year_start)
						# start_idx = idx_year_start[year]
						end_idx = YearIndex.search_year(next_valid_year, idx_year_start)
						# end_idx = idx_year_start[next_valid_year]
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