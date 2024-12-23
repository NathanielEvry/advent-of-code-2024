def evaluate_lines(file_path):
    """
    Reads a file containing target values and sequences of numbers, then determines if the target
    can be achieved using a combination of addition, multiplication, or concatenation operations
    applied left-to-right on the numbers.

    Args:
        file_path (str): Path to the input file.

    Returns:
        int: Sum of all target values that can be achieved.
    """
    total = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()

    equations = []
    # Parse the input file into target values and sequences of numbers
    for line in lines:
        test_value, numbers = line.split(":")
        equations.append((int(test_value), [*map(int, numbers.strip().split())]))

    result = []

    for test_value, numbers in equations:
        # Initialize possibles with the first number in the sequence
        possibles = [numbers.pop(0)]
        while numbers:
            curr = numbers.pop(0)
            temp = []
            for p in possibles:
                next_values = [  # Generate possible results using +, *, and concatenation (||)
                    p + curr,
                    p * curr,
                    int(str(p) + str(curr)),
                ]
                # Filter out values exceeding the target
                temp.extend([v for v in next_values if v <= test_value])
            possibles = temp

        # Check if the target value can be achieved
        if test_value in possibles:
            result.append(test_value)

    return sum(result)

# Input file path
file_path = "input.txt"

# Evaluate the lines and calculate the total
result = evaluate_lines(file_path)
print("Total:", result)
