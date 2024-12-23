# Define the file paths
rules_file = "rules.txt"
pages_file = "pages.txt"


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
    for row in pages:
        satisfies_all = row[len(row) // 2]
        for left, right in rules:
            try:
                left_index = row.index(left)
                right_index = row.index(right)
                if left_index > right_index:
                    satisfies_all = 0
                    break
            except ValueError:
                # If either left or right is not in the row, ignore this rule
                continue
        results.append(satisfies_all)
    return results


# Main logic
if __name__ == "__main__":
    rules = read_rules(rules_file)
    pages = read_pages(pages_file)
    results = check_rules(pages, rules)

    for i, result in enumerate(results):
        # print(f"Row {i + 1}: {'Pass' if result else 'Fail'}")
        print(f"Row {i + 1}: {result}")
    
    print(f"Total sum is {sum(results)}")
