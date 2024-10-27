# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_index BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics


##################################################### INDEX BASED ON YEAR #################################################################

def index_graduation_year(years_with_ids):
    """
    Sorts the graduation years and returns three things:
    1. A list of student IDs sorted by graduation year.
    2. A dictionary where the keys are unique graduation years and the values are the start index of the corresponding year in the sorted list.
    3. A dictionary where the keys are unique graduation years and the values are the last occurrence (end index) of the corresponding year in the sorted list.

    This method can be used to create an index on graduation year for a list of students.

    :param years_with_ids: List of tuples in the form (graduation_year, student_id)
    :return: sorted_ids, year_start_index, year_end_index
    """
    
    # Sort the list of tuples based on the graduation year (first element of the tuple)
    sorted_years_with_ids = sorted(years_with_ids, key=lambda x: x[0])
    
    # Extract the sorted IDs
    sorted_ids = [item[1] for item in sorted_years_with_ids]
    
    # Create dictionaries to track the start and end index of each unique graduation year
    year_start_index = {}
    year_end_index = {}
    
    for i, (year, _) in enumerate(sorted_years_with_ids):
        # Record the first occurrence of the graduation year
        if year not in year_start_index:
            year_start_index[year] = i
        
        # Always update the end index with the current occurrence
        year_end_index[year] = i

    return sorted_ids, year_start_index, year_end_index

##################################################### INDEX BASED ON YEAR #################################################################

##################################################### INDEX BASED ON NAMES #################################################################

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
        return block_ids

##################################################### INDEX BASED ON NAMES #################################################################

##################################################### STATS #################################################################


def create_year_bounds(years):
    """
    Given a list of years, create two dictionaries:
    1. One that stores the smallest year >= the given year for each year between 1900 and 2100.
    2. One that stores the largest year <= the given year for each year between 1900 and 2100.
    
    :param years: List of years
    :return: greater_equal_dict, less_equal_dict
    """
    # Sort the list of years
    sorted_years = sorted(years)
    
    # Define the range from 1900 to 2100
    full_range = list(range(1900, 2101))
    
    greater_equal_dict = {}
    less_equal_dict = {}
    
    for year in full_range:
        # Find the smallest year >= the given year
        greater_equal_dict[year] = next((y for y in sorted_years if y >= year), None)
        
        # Find the largest year <= the given year
        less_equal_dict[year] = next((y for y in reversed(sorted_years) if y <= year), None)

    return greater_equal_dict, less_equal_dict

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
     
	disc_year, idx_year_start, idx_year_end  = index_graduation_year(years_with_ids) 
    

	# NAME-INDEX CALCULATION
    
	names_with_ids = [ [ t[1], t[0] ] for t in tuples ]
	trie = Trie()
    
	for node in names_with_ids:
		trie.insert(node[0], node[1])

	# assign rank to nodes present in the trie
	trie.rank_trie(trie.root, rank = len(ids))  

	# create the disk_layout based on names
	disc_name = trie.disk_records_map()  

	# STAT CALCULATION

	ge_dict, le_dict = create_year_bounds(years)
     
	min_year = min(years)
	max_year = max(years) 
	num_ids = len(ids) 
     
	basic_stats = [min_year, max_year, num_ids] 
    

	# SETTING UP DISK LAYOUT AND INX_STAT

	disk = disc_year + disc_name
	idx_stat = [idx_year_start, trie, ge_dict, le_dict, basic_stats] 
	
	# THE METHOD SHOULD RETURN A DISK MAP AND A VARIABLE PACKAGING INDICES AND STATS
	return disk, idx_stat