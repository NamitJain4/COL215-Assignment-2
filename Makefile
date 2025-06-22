all:
	@g++ -o test_case_gen test_case_gen.cpp
	@./test_case_gen > input.txt
	@echo "Test case generated in input.txt"
	@rm test_case_gen
	@python3 main.py
	@python3 visualization.py output.txt input.txt

generate:
	@g++ -o test_case_gen test_case_gen.cpp
	@./test_case_gen > input.txt
	@echo "Test case generated in input.txt"
	@rm test_case_gen

run:
	@python3 main.py

visualize:
	@python3 visualization.py output.txt input.txt