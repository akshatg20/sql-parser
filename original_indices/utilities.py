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



