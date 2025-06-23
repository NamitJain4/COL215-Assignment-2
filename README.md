# Wiring Aware Gate Positioning

This project implements a simulated annealing algorithm for optimizing gate placement in electronic circuit designs, minimizing wire length while preventing gate overlaps.

## Files

- **main.py**: Core implementation of the simulated annealing algorithm for gate placement.
- **test_case_gen.cpp**: C++ program that generates random test cases with gates, pins, and wires.
- **visualization.py**: Python script to visualize the gate placement and wiring.
- **input.txt**: Contains the input specification of gates, pins, and their connections.
- **output.txt**: Contains the results of gate placement optimization.
- **sample_inputs/**: Directory containing example input files for testing.

## Usage

The project includes a Makefile with the following commands:

- `make generate`: Compiles and runs the test case generator to create a random input
- `make run`: Runs the gate placement optimization algorithm on the input
- `make visualize`: Generates a visualization of the final placement
- `make`: Runs all the above commands in sequence

## Quick Start

```bash
# Generate a random test case
make generate

# Run the optimization algorithm
make run

# Visualize the results
make visualize

# Or run the complete pipeline
make
```
