# Define the file paths
rules_file = "rules.txt"
pages_file = "fails.csv"


# Step 1: Read the rules
def read_rules(file_path):
    rules = []
    with open(file_path, "r") as file:
        for line in file:
            left, right = map(int, line.strip().split("|"))
            rules.append((left, right))
    return rules


# Step 2: Read the pages
def read_pages(file_path):
    pages = []
    with open(file_path, "r") as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:  # Skip empty lines
                pages.append(list(map(int, stripped_line.split(","))))
    return pages


# Step 3: Check rules for each row
def check_rules(pages, rules):
    results = []
    sums = []
    
    for row in pages:
        satisfies_all = False
        middle_value = 0
        
        while not satisfies_all:
            satisfies_all = True  # Assume all rules are satisfied until proven otherwise
            
            for left, right in rules:
                try:
                    left_index = row.index(left)
                    right_index = row.index(right)
                    
                    if left_index > right_index:
                        # If the rule is not satisfied, swap the values
                        left_value = row[left_index]
                        right_value = row[right_index]
                        row[left_index] = right_value
                        row[right_index] = left_value
                        
                        satisfies_all = False  # Rule not satisfied, need to check again
                        break  # Restart the rules from the beginning after a swap
                except ValueError:
                    # If either left or right is not in the row, ignore this rule
                    continue
            
        results.append(satisfies_all)
        sums.append(row[len(row) // 2])
    
    return results, sums



# Main logic
if __name__ == "__main__":
    rules = read_rules(rules_file)
    pages = read_pages(pages_file)
    results, sums = check_rules(pages, rules)

    for i, result in enumerate(results):
        # print(f"Row {i + 1}: {'Pass' if result else 'Fail'}")
        print(f"Row {i + 1}: {result}")
    
    print(f"Total sum is {sum(sums)}")
