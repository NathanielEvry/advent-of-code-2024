def is_valid_sequence(numbers):
    """
    Check if a sequence is valid (all increasing or all decreasing by 1-3)
    without any duplicates.
    """
    if len(numbers) < 2:
        return True
    
    # First check for any duplicates
    for i in range(len(numbers) - 1):
        if numbers[i] == numbers[i + 1]:
            return False
    
    # Determine direction from first pair
    first_diff = numbers[1] - numbers[0]
    increasing = first_diff > 0
    
    if abs(first_diff) > 3:
        return False
    
    # Check remaining differences
    for i in range(1, len(numbers) - 1):
        curr_diff = numbers[i + 1] - numbers[i]
        if increasing:
            if curr_diff <= 0 or curr_diff > 3:
                return False
        else:
            if curr_diff >= 0 or abs(curr_diff) > 3:
                return False
    
    return True

def analyze_sequence(numbers):
    """
    Analyze a sequence and return details about violations.
    Returns (violation_count, removed_index, resulting_sequence) if single violation,
    or (violation_count, None, None) otherwise.
    """
    # First check if sequence is already valid
    if is_valid_sequence(numbers):
        return 0, None, None
    
    # Try removing each number and check if remaining sequence is valid
    for i in range(len(numbers)):
        subsequence = numbers[:i] + numbers[i+1:]
        if is_valid_sequence(subsequence):
            return 1, i, subsequence
    
    return 2, None, None

def process_file(filename):
    """
    Process a file line by line and print details about sequences with single violations.
    """
    total_lines = 0
    perfect_passes = 0
    single_violation = 0
    multiple_violations = 0
    
    try:
        with open(filename, 'r') as file:
            print("\nSequences with single violations:")
            print("-" * 50)
            
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                try:
                    numbers = [int(x) for x in line.strip().split()]
                    violations, removed_idx, valid_sequence = analyze_sequence(numbers)
                    
                    if violations == 0:
                        perfect_passes += 1
                    elif violations == 1:
                        single_violation += 1
                        print(f"Line {line_num}: {numbers}")
                        print(f"  Removing index {removed_idx} (value {numbers[removed_idx]}) makes valid: {valid_sequence}")
                        print()
                    else:
                        multiple_violations += 1
                        
                except ValueError:
                    multiple_violations += 1
                    
        return {
            'total_lines': total_lines,
            'perfect_passes': perfect_passes,
            'single_violation': single_violation,
            'multiple_violations': multiple_violations
        }
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

# Test cases
def run_tests():
    test_cases = [
        [1, 3, 2, 4, 5],  # single violation (remove 2)
        [3, 2, 2, 1, 0],  # multiple violations (duplicate 2)
        [66, 66, 66, 64, 63, 62, 60, 57],  # multiple violations (duplicate 66s)
        [95, 95, 94, 90, 92],  # multiple violations (duplicates and pattern break)
        [1, 2, 5, 6, 7],  # single violation (remove 5 for valid increasing)
        [7, 6, 3, 2, 1],  # single violation (remove 3 for valid decreasing)
        [1, 1, 2, 3, 4],  # multiple violations (duplicate 1s)
        [5, 4, 1, 0],  # single violation (remove 1)
    ]
    
    print("\nAnalyzing test cases:")
    print("-" * 50)
    for sequence in test_cases:
        violations, removed_idx, valid_sequence = analyze_sequence(sequence)
        status = "PERFECT" if violations == 0 else f"{violations} violation(s)"
        print(f"Sequence: {sequence}")
        print(f"Status: {status}")
        if violations == 1:
            print(f"  Removing index {removed_idx} (value {sequence[removed_idx]}) makes valid: {valid_sequence}")
        print()

if __name__ == "__main__":
    # Run test cases
    run_tests()
    
    # Process file if filename provided
    filename = "sequences.txt"  # Replace with your input file name
    results = process_file(filename)
    
    if results:
        print("\nSummary:")
        print("-" * 50)
        print(f"Total lines processed: {results['total_lines']}")
        print(f"Perfect sequences: {results['perfect_passes']}")
        print(f"Sequences with single violation: {results['single_violation']}")
        print(f"Sequences with multiple violations: {results['multiple_violations']}")