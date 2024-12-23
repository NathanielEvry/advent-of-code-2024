def is_valid_sequence(numbers):
    """
    Validate if a sequence of numbers is consistently increasing or decreasing
    with differences between 1 and 3.
    """
    if len(numbers) < 2:
        return False
    
    # Check first difference to determine if sequence should increase or decrease
    diff = numbers[1] - numbers[0]
    increasing = diff > 0
    
    # If first difference is 0 or greater than 3, sequence is invalid
    if abs(diff) == 0 or abs(diff) > 3:
        return False
    
    # Check remaining differences
    for i in range(1, len(numbers) - 1):
        curr_diff = numbers[i + 1] - numbers[i]
        
        # Check if direction changes or difference is invalid
        if increasing and curr_diff <= 0:
            return False
        if not increasing and curr_diff >= 0:
            return False
        if abs(curr_diff) == 0 or abs(curr_diff) > 3:
            return False
    
    return True

def process_file(filename):
    """
    Process a file line by line and count valid/invalid sequences.
    """
    total_lines = 0
    pass_count = 0
    fail_count = 0
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                total_lines += 1
                
                # Convert line to list of integers
                try:
                    numbers = [int(x) for x in line.strip().split()]
                    if is_valid_sequence(numbers):
                        pass_count += 1
                    else:
                        fail_count += 1
                except ValueError:
                    # If conversion fails, count as failed line
                    fail_count += 1
                    
        return {
            'total_lines': total_lines,
            'pass_count': pass_count,
            'fail_count': fail_count
        }
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

# Example usage
if __name__ == "__main__":
    filename = "sequences.txt"  # Replace with your input file name
    results = process_file(filename)
    
    if results:
        print(f"Total lines processed: {results['total_lines']}")
        print(f"Passing sequences: {results['pass_count']}")
        print(f"Failing sequences: {results['fail_count']}")