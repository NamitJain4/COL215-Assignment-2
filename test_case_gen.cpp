#include <algorithm>
#include <iostream>
#include <fstream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <vector>

using namespace std;

int main() {
  // Use a seeded random number generator with current time
  std::random_device rd;  // Used to obtain a seed for the random number engine
  std::mt19937 gen(rd()); // Seed the generator with a random device

  // Create a distribution for generating random integers in the range [min,
  // max]
  std::uniform_int_distribution<> dist(
      1, 10000000); // Random integers between 1 and 10000000

  // Variables for storing maximum dimensions and number of gates
  int max_num_gates = 50; // Example value, you can set it to the actual required value
  int max_gate_height = 10;
  int max_gate_width = 10;
  int max_pin_per_edge_overall = 2;

  int total_pins = 1;

  // Create a stringstream to temporarily store the output
  bool wire_on_same_gate = true;
  std::ostringstream output_buffer;
  int fin_num_gate = 0;
  int fin_num_pin = 0;
  int fin_num_wire = 0;
  
  while (wire_on_same_gate || total_pins % 2) {
    // Reset the stringstream to clear its contents
    output_buffer.str("");
    output_buffer.clear(); // This resets error flags, but not the buffer. We
                           // reset the buffer above.

    total_pins = 0;
    int num_gates = 1 + dist(gen) % max_num_gates;
    std::vector<int> num_pin_on_gate(
        num_gates); // Store pin count for each gate

    for (int gate_idx = 1; gate_idx <= num_gates; gate_idx++) {
      int gate_height = 1 + dist(gen) % max_gate_height;
      int gate_width = 1 + dist(gen) % max_gate_width;

      output_buffer << 'g' << gate_idx << " " << gate_width << " "
                    << gate_height << std::endl;

      int first_pin_cond = dist(gen) % 4;
      set<pair<int, int>> pins;

      if (first_pin_cond == 0)
        pins.insert({0, dist(gen) % (gate_height + 1)});
      else if (first_pin_cond == 1)
        pins.insert({dist(gen) % (gate_width + 1), 0});
      else if (first_pin_cond == 2)
        pins.insert({gate_width, dist(gen) % (gate_height + 1)});
      else
        pins.insert({dist(gen) % (gate_width + 1), gate_height});

      int num_pin = 1;

      // Add pins to different edges
      int max_pin_per_edge = min(gate_width, min(gate_height, 1 + dist(gen) % max_pin_per_edge_overall));
      int pin_on_edge = dist(gen) % max_pin_per_edge;
      for (int pin_idx = 0; pin_idx < pin_on_edge;)
        if (pins.insert({0, dist(gen) % (gate_height + 1)}).second == true) {
          pin_idx++;
          num_pin++;
        }

      pin_on_edge = dist(gen) % max_pin_per_edge;
      for (int pin_idx = 0; pin_idx < pin_on_edge;)
        if (pins.insert({dist(gen) % (gate_width + 1), 0}).second == true) {
          pin_idx++;
          num_pin++;
        }

      pin_on_edge = dist(gen) % max_pin_per_edge;
      for (int pin_idx = 0; pin_idx < pin_on_edge;)
        if (pins.insert({gate_width, dist(gen) % (gate_height + 1)}).second ==
            true) {
          pin_idx++;
          num_pin++;
        }

      pin_on_edge = dist(gen) % max_pin_per_edge;
      for (int pin_idx = 0; pin_idx < pin_on_edge;)
        if (pins.insert({dist(gen) % (gate_width + 1), gate_height}).second ==
            true) {
          pin_idx++;
          num_pin++;
        }

      num_pin_on_gate[gate_idx - 1] = num_pin;

      output_buffer << "pins g" << gate_idx << " ";
      for (auto x : pins)
        output_buffer << x.first << " " << x.second << " ";
      output_buffer << std::endl;

      total_pins += num_pin;
    }

    if (total_pins % 2) {
      continue; // If odd number of pins, go to next iteration
    }

    // Step 1: Create a sorted set in descending order of the gates and their
    // pin counts
    set<pair<int, int>, greater<pair<int, int>>> pin_gate_pair;
    for (int i = 0; i < num_gates; i++) {
      pin_gate_pair.insert({num_pin_on_gate[i], i});
    }

    // Map to track which pin number we're currently at for each gate
    map<int, int> start_pin;
    for (int i = 1; i <= num_gates; i++)
      start_pin[i] = 0; // Start counting pins from 0 (increment before use)

    // Step 2: Ensure the largest gate does not have more than half the total
    // pins
    if (pin_gate_pair.begin()->first > total_pins / 2) {
      wire_on_same_gate = true;
    //   cout << "Wire on same gate (too many pins in one gate)" << endl;
      continue; // Too many pins in one gate, retry
    } else {
      wire_on_same_gate = false;
    }

    // Step 3: Pair pins between gates
    while (!pin_gate_pair.empty()) {
      // Take the largest gate (it1)
      auto it1 = pin_gate_pair.begin();
      int gate_idx1 = it1->second + 1; // Gate indices are 1-based
      int num_pins1 = it1->first;
      pin_gate_pair.erase(it1); // Remove from set

      // Take the smallest gate (it2)
      auto it2 = prev(pin_gate_pair.end());
      int gate_idx2 = it2->second + 1; // Gate indices are 1-based
      int num_pins2 = it2->first;
      pin_gate_pair.erase(it2); // Remove from set

      // Increment and output the pin connections (use start_pin before
      // incrementing)
      output_buffer << "wire g" << gate_idx1 << ".p" << ++start_pin[gate_idx1]
                    << " g" << gate_idx2 << ".p" << ++start_pin[gate_idx2]
                    << endl;

      // Decrement pin counts and reinsert into the set if they have pins left
      num_pins1--;
      num_pins2--;
      if (num_pins1 > 0)
        pin_gate_pair.insert({num_pins1, gate_idx1 - 1});
      if (num_pins2 > 0)
        pin_gate_pair.insert({num_pins2, gate_idx2 - 1});
    }    std::ofstream outgugu("temp.txt");
    fin_num_gate = num_gates;
    fin_num_pin = total_pins;
    fin_num_wire = total_pins / 2;

    // Check if the file is open
    if (outgugu.is_open()) {
        // Write the values to the file
        outgugu << "Number of Gates: " << fin_num_gate << std::endl;
        outgugu << "Number of Pins: " << fin_num_pin << std::endl;
        outgugu << "Number of Wires: " << fin_num_wire << std::endl;

        // Close the file after writing
        outgugu.close();
    } else {
        std::cerr << "Unable to open file temp.txt" << std::endl;
    }

    // Write the contents of the stringstream to input.txt
    //std::ofstream input_file("input.txt");
    std::cout << output_buffer.str();
    
    break;
  }

  return 0;
}