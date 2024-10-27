def index_graduation_year(years_with_ids):
	"""
	Sorts the graduation years and returns two things:
	1. A list of student IDs sorted by graduation year.
	2. A list of tuples where the first element of the tuple is the graduation year and the second element is the index of the first occurrence of that year in the sorted list of years.

	This method can be used to create an index on graduation year for a list of students.

	:param years_with_ids: List of tuples in the form (graduation_year, student_id)
	:return: sorted_ids, year_start_index, year_end_index
	"""
	
	# Sort the list of tuples based on the graduation year (first element of the tuple)
	sorted_years_with_ids = sorted(years_with_ids, key=lambda x: x[0])

	# Extract the sorted IDs
	sorted_ids = [item[1] for item in sorted_years_with_ids]
	
	# Create list of tuples to track the start index of each unique graduation year
	year_start_index = []

	# Create a set of encountered years
	encountered_years = set()
	
	for i, (year, _) in enumerate(sorted_years_with_ids):
		# Check if the year has not been encountered before
		if year not in encountered_years:
			# Add the year to the set of encountered years
			encountered_years.add(year)
			# Record the first occurrence of the graduation year
			year_start_index.append((year, i))
		
	return sorted_ids, year_start_index

def create_year_bounds(years):
	"""
	Given a list of years, create two lists of tuples:
	1. One that stores the smallest year >= the given year for each year between 1900 and 2100.
	2. One that stores the largest year <= the given year for each year between 1900 and 2100.
	
	:param years: List of years
	:return: greater_equal_dict, less_equal_dict
	"""
	# Sort the list of years
	sorted_years = sorted(years)
	
	# Define the range from 1900 to 2100
	full_range = list(range(1900, 2101))
	
	greater_equal_list = []
	less_equal_list = []
	
	for year in full_range:
		# Find the smallest year >= the given year
		next_smallest_year = next((y for y in sorted_years if y >= year), None)
		greater_equal_list.append((year, next_smallest_year))
		
		# Find the largest year <= the given year
		next_largest_year = next((y for y in reversed(sorted_years) if y <= year), None)
		less_equal_list.append((year, next_largest_year))

	return greater_equal_list, less_equal_list

def search_year(year, tuple_list_of_years):
	"""
	Searches for the given graduation year in the given tuple_list_of_years list using binary search and returns the corresponding id
	"""

	low = 0
	high = len(tuple_list_of_years) - 1

	while(low <= high):
		mid = low + (high - low) // 2
		if tuple_list_of_years[mid][0] == year:
			return tuple_list_of_years[mid][1]
		elif tuple_list_of_years[mid][0] < year:
			low = mid + 1
		else:
			high = mid - 1
		
	return None

def lower_bound(sorted_tuples, target):
	left, right = 0, len(sorted_tuples) - 1
	result = None

	while left <= right:
		mid = (left + right) // 2

		# Check if the first element of the tuple at mid is < target
		if sorted_tuples[mid][0] <= target:
			result = sorted_tuples[mid][1]  # Potential lower bound found
			if sorted_tuples[mid][0] == target:
				break
			left = mid + 1  # Continue searching in the right half for a larger valid tuple
		else:
			right = mid - 1  # Search the left half

	return result  # Will be None if no valid tuple is found


def upper_bound(sorted_tuples, target):
	left, right = 0, len(sorted_tuples) - 1
	result = None

	while left <= right:
		mid = (left + right) // 2

		# Check if the first element of the tuple at mid is > target
		if sorted_tuples[mid][0] >= target:
			result = sorted_tuples[mid][1]
			if sorted_tuples[mid][0] == target:
				break
			right = mid - 1  # Continue searching in the left half for a smaller valid tuple
		else:
			left = mid + 1  # Continue searching in the right half

	return result  # Will be None if no upper bound is found