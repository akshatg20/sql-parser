# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_index BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics



import YearIndex
import TrieIndex
import CollapsedTrieIndex

##################################################### STATS #################################################################



##################################################### STATS #################################################################


################################
# Non Editable Region Starting #
################################
def my_index( tuples ):
################################
#  Non Editable Region Ending  #
################################

	# Use this method to create indices and statistics
	# Each tuple has 3 values -- the id, name and year
	 
	ids = [ t[ 0 ] for t in tuples ]
	names = [ t[ 1 ] for t in tuples ] 
	years = [ t[ 2 ] for t in tuples ]
	
	# YEAR-INDEX CALCULATION
	 
	years_with_ids = [ (t[2], t[0]) for t in tuples ]
	 
	disc_year, idx_year_start  = YearIndex.index_graduation_year(years_with_ids) 
	ge_list, le_list = YearIndex.create_year_bounds(years)
	

	# NAME-INDEX CALCULATION
	
	names_with_ids = [ [ t[1], t[0] ] for t in tuples ]
	trie = TrieIndex.Trie()
	
	for node in names_with_ids:
		trie.insert(node[0], node[1])

	# assign rank to nodes present in the trie
	trie.rank_trie(trie.root, rank = len(ids))  

	# create the disk_layout based on names
	disc_name = trie.disk_records_map()  


	# COLLAPSED-NAME-INDEX CALCULATION

	# insert nodes of the form (name, (id, year)) in the trie
	collapsed_names_with_ids = [ [ t[1], (t[0], t[2]) ] for t in tuples ]
	collapsed_trie = CollapsedTrieIndex.CollapsedTrie()
	
	# print("Collapsed trie intiialized")

	# insert elements in the trie
	for node in collapsed_names_with_ids:
		collapsed_trie.insert(node[0], node[1])

	# print("Elements inserted in the collapsed trie")
	
	# create the less_than and greater_than dictionaries for the years at each node
	# collapsed_trie.set_valid_subtree_years(collapsed_trie.root)

	# print("Valid subtree years set")
		
	# # assign rank to nodes present in the trie
	collapsed_trie.rank_trie(collapsed_trie.root, rank = 2*len(ids))

	# print("Rank assigned to nodes in the collapsed trie")
		
	# # create the disk_layout based on collapsed names
	disc_name_collapsed = collapsed_trie.disk_records_map()

	# print("Disk layout created for collapsed trie")

	# STAT CALCULATION

	min_year = min(years)
	max_year = max(years) 
	num_ids = len(ids) 
	 
	basic_stats = [min_year, max_year, num_ids] 
	

	# SETTING UP DISK LAYOUT AND INX_STAT

	disk = disc_year + disc_name + disc_name_collapsed
	idx_stat = [idx_year_start, trie, collapsed_trie, ge_list, le_list, basic_stats] 
	
	# THE METHOD SHOULD RETURN A DISK MAP AND A VARIABLE PACKAGING INDICES AND STATS
	return disk, idx_stat