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
def execute_year_index(year, comp, idx_year, ge_list, le_list, stats, disp=0):

    min_year, max_year, num_ids = int(stats[0]), int(stats[1]), int(stats[2])
    diskloc_list = []

    if comp == '<=':
        # If the year is less than the minimum year, return an empty list
        if year < min_year:
            return diskloc_list

        # If the year is greater than the maximum year, return all the indices
        if year >= max_year:
            for i in range(num_ids):
                diskloc_list.append(i + disp)
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
                diskloc_list.append(i + disp)

    elif comp == '>=':
        # If the year is greater than the maximum year, return an empty list
        if year > max_year:
            return diskloc_list

        # If the year is less than the minimum year, return all the indices
        if year <= min_year:
            for i in range(num_ids):
                diskloc_list.append(i + disp)
            return diskloc_list

        # Otherwise calculate the valid year greater than or equal to the given year
        valid_year = YearIndex.search_year(year, ge_list)

        if valid_year is not None:
            # Find the first occurence of the valid year using the index of the valid year
            curr_idx = YearIndex.search_year(valid_year, idx_year)
            max_idx = num_ids - 1

            # Append all the indices from the first occurence of the valid year till the end
            for i in range(curr_idx, max_idx+1):
                diskloc_list.append(i + disp)

    else:
        # Check if the given year is valid or not
        valid_year = YearIndex.search_year(year, ge_list)

        if valid_year is not None and valid_year == year:
            # Find the first occurence of the year using the index of the valid year
            start_idx = YearIndex.search_year(year, idx_year)

            # Find the last occurence of the year using the index of the next valid year
            next_valid_year = YearIndex.search_year(valid_year+1, ge_list)
            end_idx = YearIndex.search_year(next_valid_year, idx_year)

            # Append all the indices from the first occurence of the year till the last occurence of the year
            for i in range(start_idx, end_idx+1):
                diskloc_list.append(i + disp)

    return diskloc_list

# Function to execute trie_index


def execute_name_index(name, comp, trie, stats):

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

# Function to execute year_trie_index


def execute_year_trie_index(name, year, comp1, comp2, year_trie_index, ge_list, le_list, stats, onlyYearQuery=False):

    min_year, max_year, num_ids = int(stats[0]), int(stats[1]), int(stats[2])
    diskloc_list = []
    # base_addr = year_trie_index[0][2]

    if comp2 == '<=':
        # If the year is less than the minimum year, return an empty list
        if year < min_year:
            return diskloc_list

        # If the year is greater than the maximum year, check for the name condition on all the tries
        if year >= max_year:
            if onlyYearQuery:
                diskloc_list = list(range(num_ids))
                return diskloc_list
            else:
                for (_, trie, _) in year_trie_index:
                    diskloc_list.extend(
                        execute_name_index(name, comp1, trie, stats))
                return diskloc_list

        # Otherwise calculate the valid year less than or equal to the given year
        valid_year = YearIndex.search_year(year, le_list)

        if valid_year is not None:
            # Find the index of this valid year
            end_idx = YearIndex.search_year(valid_year, year_trie_index, True)

            # Iteratre through the tries and append the disk locations
            for i in range(end_idx+1):
                if onlyYearQuery:
                    diskloc_list.extend(
                        year_trie_index[i][1].disk_records_locations_all())
                else:
                    diskloc_list.extend(execute_name_index(
                        name, comp1, year_trie_index[i][1], stats))

    elif comp2 == '>=':
        # If the year is greater than the maximum year, return an empty list
        if year > max_year:
            return diskloc_list

        # If the year is less than the minimum year, return all the indices
        if year <= min_year:
            if onlyYearQuery:
                diskloc_list = list(range(num_ids))
                return diskloc_list
            else:
                for (_, trie, _) in year_trie_index:
                    diskloc_list.extend(
                        execute_name_index(name, comp1, trie, stats))
                return diskloc_list

        # Otherwise calculate the valid year greater than or equal to the given year
        valid_year = YearIndex.search_year(year, ge_list)
        # print("Valid year: ",valid_year)

        if valid_year is not None:
            # Find the index of this valid year
            start_idx = YearIndex.search_year(
                valid_year, year_trie_index, True)
            end_idx = year_trie_index[-1][2]

            # Iteratre through the tries and append the disk locations
            for i in range(start_idx, end_idx+1):
                if onlyYearQuery:
                    diskloc_list.extend(
                        year_trie_index[i][1].disk_records_locations_all())
                else:
                    diskloc_list.extend(execute_name_index(
                        name, comp1, year_trie_index[i][1], stats))

    else:
        # Check if the given year is valid or not
        valid_year = YearIndex.search_year(year, ge_list)

        if valid_year is not None and valid_year == year:
            # Find the index of this valid year
            year_idx = YearIndex.search_year(year, year_trie_index, True)

            # Append the disk locations for the valid year
            if onlyYearQuery:
                diskloc_list = year_trie_index[year_idx][1].disk_records_locations_all(
                )
            else:
                diskloc_list = execute_name_index(
                    name, comp1, year_trie_index[year_idx][1], stats)

    return diskloc_list

# Function to execute collapsed_trie_index


def execute_collapsed_trie_index(name, year, comp1, comp2, collapsedtrie, onlyNameQuery=False):

    diskloc_list = []

    if comp1 == 'LIKE':
        prefix_name = name[1:-2]
        if onlyNameQuery:
            diskloc_list = collapsedtrie.disk_records_locations_name(
                prefix_name)
        else:
            diskloc_list = collapsedtrie.disk_records_locations(
                prefix_name, year, comp2, True)
    else:
        prefix_name = name[1:-1]
        if onlyNameQuery:
            diskloc_list = collapsedtrie.disk_records_locations_exact_name(
                prefix_name)
        else:
            diskloc_list = collapsedtrie.disk_records_locations(
                prefix_name, year, comp2, False)

    return diskloc_list

################################
# Non Editable Region Starting #
################################


def my_execute(clause, idx):
    ################################
    #  Non Editable Region Ending  #
    ################################

    diskloc_list = []
    year_index, trie_index, year_trie_index, collapsedtrie = idx[0], idx[1], idx[2], idx[3]
    ge_list, le_list, stats = idx[4], idx[5], idx[6]

    # print("Max year: ", stats[1], " Min year: ", stats[0])

    # for simple query
    if len(clause) == 1:
        # In case of queries like "WHERE year [comp] [YEAR_VALUE]"
        if clause[0][0] == 'year':
            year = int(clause[0][2])
            diskloc_list = execute_year_index(
                year, clause[0][1], year_index, ge_list, le_list, stats)
            # diskloc_list = execute_year_trie_index("", year, "", clause[0][1], year_trie_index, ge_list, le_list, stats, True)

        # In case of queries like "WHERE name [comp] [NAME_VALUE]"
        elif clause[0][0] == 'name':
            name = clause[0][2]
            # diskloc_list = execute_name_index(
            #     name, clause[0][1], trie_index, stats)
            diskloc_list = execute_collapsed_trie_index(
                name, 0, clause[0][1], "", collapsedtrie, True)

    # for joint query
    else:
        # In case of queries like "WHERE name [comp] [NAME_VALUE] AND year [comp] [YEAR_VALUE]"
        name = clause[0][2]
        year = int(clause[1][2])
        diskloc_list = execute_collapsed_trie_index(name, year, clause[0][1], clause[1][1], collapsedtrie)
        # diskloc_list = execute_year_trie_index(
        #     name, year, clause[0][1], clause[1][1], year_trie_index, ge_list, le_list, stats)

    # Use this method to take a WHERE clause specification
    # and return results of the resulting query
    # clause is a list containing either one or two predicates

    # Each predicate is itself a list of 3 objects, column name, comparator and value
    # idx contains the packaged variable returned by the my_index method

    # THE METHOD MUST RETURN A SINGLE LIST OF INDICES INTO THE DISK MAP
    return diskloc_list
