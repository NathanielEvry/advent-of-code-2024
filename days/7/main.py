from itertools import product

def evaluate_lines(file_path):
    total = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        result, elements = line.split(": ")
        result = int(result)
        elements = list(map(int, elements.split()))
        print(f"Processing line: result={result}, elements={elements}")

        # Generate all combinations of operators
        operators = list(product("+*", repeat=len(elements) - 1))

        for ops in operators:
            # Evaluate the expression left-to-right
            current_value = elements[0]
            for i, op in enumerate(ops):
                if op == '+':
                    current_value += elements[i + 1]
                elif op == '*':
                    current_value *= elements[i + 1]

            # Check if the evaluated value matches the result
            if current_value == result:
                print(f"Found that {' '.join(str(elements[0]) + ''.join(op + str(elements[i + 1]) for i, op in enumerate(ops)))} evals to {result}, adding to total: {total}")
                total += result
                break  # No need to check further for this line

    return total

# Input file path
file_path = "input.txt"

# Evaluate the lines and calculate the total
result = evaluate_lines(file_path)
print("Total:", result)
