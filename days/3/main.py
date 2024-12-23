import re

# Example with specific patterns
text = "There are 12 months and 30 days"
numbers = [int(num) for num in re.findall(r'\d+', text)]
if len(numbers) >= 2:
    result = numbers[0] * numbers[1]
    print(f"Found numbers {numbers[0]} and {numbers[1]}, product is {result}")


    if __name__ == "__main__":
    # Run test cases
    run_tests()
    
    # Process file if filename provided
    filename = "sequences.txt"  # Replace with your input file name
    results = process_file(filename)