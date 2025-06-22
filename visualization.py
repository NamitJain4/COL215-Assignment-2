#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
import random
import tkinter.messagebox as messagebox
import math
import colorsys

# Function to parse the input data from input.txt
def parse_input(data):
    gates = {}
    pins = {}
    wires = []

    for line in data:
        tokens = line.split()

        if tokens[0].startswith('g'):
            # Parsing gate dimensions
            gate_name = tokens[0]
            width, height = int(tokens[1]), int(tokens[2])
            gates[gate_name] = {"width": width, "height": height}
        
        elif tokens[0] == "pins":
            # Parsing pin coordinates
            gate_name = tokens[1]
            pin_coords = [(int(tokens[i]), int(tokens[i+1])) for i in range(2, len(tokens), 2)]
            pins[gate_name] = pin_coords

        elif tokens[0] == "wire":
            # Parsing wire connections
            wire_from = tokens[1].split('.')
            wire_to = tokens[2].split('.')
            wires.append((wire_from, wire_to))
    
    return gates, pins, wires

# Function to parse the gate positions from output.txt
def parse_output(data):
    gate_positions = {}
    for line in data:
        tokens = line.split()
        if tokens[0].startswith('g'):
            gate_name = tokens[0]
            x, y = int(tokens[1]), int(tokens[2])
            gate_positions[gate_name] = {"x": x, "y": y}
    return gate_positions

# Function to create a connection matrix between pins
def create_connection_matrix(wires, pin_names):
    # Create a lookup from pin name to index
    pin_lookup = {name: idx for idx, name in enumerate(pin_names)}
    
    # Initialize connection matrix
    n = len(pin_names)
    connection_matrix = [[False for _ in range(n)] for _ in range(n)]
    
    # Fill the connection matrix
    for wire_from, wire_to in wires:
        from_name = f"{wire_from[0]}.p{wire_from[1][1:]}"
        to_name = f"{wire_to[0]}.p{wire_to[1][1:]}"
        
        # Check if pins exist in the lookup
        if from_name in pin_lookup and to_name in pin_lookup:
            from_idx = pin_lookup[from_name]
            to_idx = pin_lookup[to_name]
            
            # Set the connection in the matrix
            connection_matrix[from_idx][to_idx] = True
            connection_matrix[to_idx][from_idx] = True  # Bidirectional
    
    return connection_matrix

# Generate a visually distinct color
def generate_random_color():
    # Use HSV color space for better color distribution
    h = random.random()  # Random hue
    s = 0.7 + random.random() * 0.3  # High saturation (0.8-1.0)
    v = 0.7 + random.random() * 0.3  # High value (0.8-1.0)
    
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # Convert to hex format
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

class GateVisualizer(Tk):
    def __init__(self, gate_dimensions, gate_positions, pins, bounding_box, connection_matrix, pin_names, pin_coordinates):
        super().__init__()
        
        self.title("Gate Placement Visualization")
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set the canvas size based on the screen size
        canvas_width = min(int(screen_width * 0.9), 1200)
        canvas_height = min(int(screen_height * 0.9), 800)
        
        # Calculate scaling factor based on bounding box
        if bounding_box:
            scale_x = canvas_width / bounding_box[0]
            scale_y = canvas_height / bounding_box[1]
            self.scale = min(scale_x, scale_y) * 0.85  # 85% of the available space for better margins
        else:
            self.scale = 30  # Default scale
        
        # Create a frame with scrollbars
        self.frame = Frame(self)
        self.frame.pack(fill=BOTH, expand=True)
        
        # Create canvas with scrollbars
        self.canvas_width = max(canvas_width, int(bounding_box[0] * self.scale * 1.2))
        self.canvas_height = max(canvas_height, int(bounding_box[1] * self.scale * 1.2))
        
        # Create horizontal and vertical scrollbars
        h_scrollbar = Scrollbar(self.frame, orient=HORIZONTAL)
        v_scrollbar = Scrollbar(self.frame)
        
        # Place the scrollbars
        h_scrollbar.pack(side=BOTTOM, fill=X)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Create the canvas with scrollbars
        self.canvas = Canvas(self.frame, width=canvas_width, height=canvas_height,
                             xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Configure the scrollbars
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Set the scrollregion
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
        
        # Draw the gates, pins, and wires
        self.draw_everything(gate_dimensions, gate_positions, pins, connection_matrix, pin_names, pin_coordinates)
        
        # Create a legend
        self.create_legend()
        
        # Add zoom controls
        self.create_zoom_controls()
    
    def create_zoom_controls(self):
        zoom_frame = Frame(self)
        zoom_frame.pack(side=BOTTOM, fill=X)
        
        zoom_in_btn = Button(zoom_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=LEFT, padx=5, pady=5)
        
        zoom_out_btn = Button(zoom_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=LEFT, padx=5, pady=5)
        
        reset_btn = Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom)
        reset_btn.pack(side=LEFT, padx=5, pady=5)
    
    def zoom_in(self):
        self.scale *= 1.2
        self.redraw()
    
    def zoom_out(self):
        self.scale /= 1.2
        self.redraw()
    
    def reset_zoom(self):
        # Calculate scaling factor based on bounding box
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if hasattr(self, 'bounding_box') and self.bounding_box:
            scale_x = canvas_width / self.bounding_box[0]
            scale_y = canvas_height / self.bounding_box[1]
            self.scale = min(scale_x, scale_y) * 0.85
        else:
            self.scale = 30
            
        self.redraw()
    
    def redraw(self):
        # Store the current bounding box
        if hasattr(self, 'gate_dimensions') and hasattr(self, 'gate_positions'):
            self.canvas.delete("all")
            self.draw_everything(self.gate_dimensions, self.gate_positions, self.pins, 
                                self.connection_matrix, self.pin_names, self.pin_coordinates)
            self.create_legend()
    
    def create_legend(self):
        # Create a legend frame in the top-right corner
        legend_frame = Frame(self.canvas, bg="white", bd=1, relief=SOLID)
        legend_window = self.canvas.create_window(self.canvas_width - 150, 20, 
                                                anchor=NE, window=legend_frame)
        
        # Add legend title
        legend_title = Label(legend_frame, text="Legend", font=("Arial", 10, "bold"), bg="white")
        legend_title.pack(side=TOP, padx=5, pady=2)
        
        # Gate representation
        gate_frame = Frame(legend_frame, bg="white")
        gate_frame.pack(side=TOP, fill=X, padx=5, pady=2)
        
        gate_canvas = Canvas(gate_frame, width=20, height=20, bg="white", highlightthickness=0)
        gate_canvas.pack(side=LEFT)
        gate_canvas.create_rectangle(2, 2, 18, 18, fill="lightblue", outline="black")
        
        gate_label = Label(gate_frame, text="Gate", bg="white", anchor=W)
        gate_label.pack(side=LEFT, padx=5)
        
        # Pin representation
        pin_frame = Frame(legend_frame, bg="white")
        pin_frame.pack(side=TOP, fill=X, padx=5, pady=2)
        
        pin_canvas = Canvas(pin_frame, width=20, height=20, bg="white", highlightthickness=0)
        pin_canvas.pack(side=LEFT)
        pin_canvas.create_oval(5, 5, 15, 15, fill="black", outline="black")
        pin_canvas.create_oval(7, 7, 13, 13, fill="white", outline="black")
        
        pin_label = Label(pin_frame, text="Pin", bg="white", anchor=W)
        pin_label.pack(side=LEFT, padx=5)
        
        # Wire representation
        wire_frame = Frame(legend_frame, bg="white")
        wire_frame.pack(side=TOP, fill=X, padx=5, pady=2)
        
        wire_canvas = Canvas(wire_frame, width=20, height=20, bg="white", highlightthickness=0)
        wire_canvas.pack(side=LEFT)
        wire_canvas.create_line(2, 10, 18, 10, fill="purple", width=3)
        
        wire_label = Label(wire_frame, text="Wire", bg="white", anchor=W)
        wire_label.pack(side=LEFT, padx=5)
        
        # Wire overlap representation
        # overlap_frame = Frame(legend_frame, bg="white")
        # overlap_frame.pack(side=TOP, fill=X, padx=5, pady=2)
        
        # overlap_canvas = Canvas(overlap_frame, width=20, height=20, bg="white", highlightthickness=0)
        # overlap_canvas.pack(side=LEFT)
        # # Draw two overlapping semi-transparent lines
        # overlap_canvas.create_line(2, 7, 18, 7, fill="#FF0000", width=3)
        # overlap_canvas.create_line(2, 13, 18, 13, fill="#0000FF", width=3)
        
        # overlap_label = Label(overlap_frame, text="Overlapping Wires", bg="white", anchor=W)
        # overlap_label.pack(side=LEFT, padx=5)   

    def draw_everything(self, gate_dimensions, gate_positions, pins, connection_matrix, pin_names, pin_coordinates):
        # Store parameters for redrawing
        self.gate_dimensions = gate_dimensions
        self.gate_positions = gate_positions
        self.pins = pins
        self.connection_matrix = connection_matrix
        self.pin_names = pin_names
        self.pin_coordinates = pin_coordinates
        
        # Calculate the bounding box
        self.bounding_box = calculate_bounding_box(gate_dimensions, gate_positions)
        
        margin = 50  # Margin in pixels
        gate_pin_positions = {gate: [] for gate in gate_positions}
        
        # Create a PIL image for drawing transparent wires
        self.wire_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.wire_draw = ImageDraw.Draw(self.wire_image)
        
        # Draw gates with their pins
        for gate_name, position in gate_positions.items():
            if gate_name in gate_dimensions:
                gate_width = gate_dimensions[gate_name]["width"]
                gate_height = gate_dimensions[gate_name]["height"]
                
                # Scale the coordinates
                x = margin + position["x"] * self.scale
                y = margin + position["y"] * self.scale
                width = gate_width * self.scale
                height = gate_height * self.scale
                
                # Draw the gate
                self.canvas.create_rectangle(
                    x, y, x + width, y + height, 
                    fill="lightblue", outline="black", width=2
                )
                
                # Add the gate name
                self.canvas.create_text(
                    x + width/2, y + height/2, 
                    text=gate_name, font=("Arial", max(8, int(self.scale/5)))
                )
                
                # Draw pins if available
                if gate_name in pins:
                    pin_size = max(3, min(5, self.scale / 10))
                    
                    for i, (px_rel, py_rel) in enumerate(pins[gate_name]):
                        # Convert relative pin coordinates to absolute coordinates
                        px = x + px_rel * self.scale
                        py = y + py_rel * self.scale
                        
                        # Draw pin with a white center for better visibility
                        self.canvas.create_oval(px - pin_size, py - pin_size, 
                                                px + pin_size, py + pin_size, 
                                                fill="black", outline="black")
                        self.canvas.create_oval(px - pin_size/2, py - pin_size/2, 
                                                px + pin_size/2, py + pin_size/2, 
                                                fill="white", outline="black")
                        
                        # Add pin number for clearer identification
                        if self.scale > 15:  # Only show numbers if scale is large enough
                            self.canvas.create_text(px, py + pin_size + 8,
                                                  text=f"p{i+1}", font=("Arial", 7))
                        
                        # Store the scaled pin position
                        gate_pin_positions[gate_name].append((px, py, f"{gate_name}.p{i+1}"))
        
        # Generate all wire connections
        all_wires = []
        
        for i in range(len(connection_matrix)):
            for j in range(i+1, len(connection_matrix[i])):  # Only process each wire once (i < j)
                if connection_matrix[i][j]:
                    # Get the pin coordinates
                    start_x, start_y = pin_coordinates[i]
                    end_x, end_y = pin_coordinates[j]
                    
                    # Scale the coordinates
                    start_x = margin + start_x * self.scale
                    start_y = margin + start_y * self.scale
                    end_x = margin + end_x * self.scale
                    end_y = margin + end_y * self.scale
                    
                    # Calculate the intermediate point for horizontal-then-vertical routing
                    mid_x = start_x
                    mid_y = end_y
                    
                    # Store the wire with its two segments
                    wire = {
                        'segments': [
                            (start_x, start_y, mid_x, mid_y),
                            (mid_x, mid_y, end_x, end_y)
                        ],
                        'pins': (pin_names[i], pin_names[j])  # Store connected pin names for reference
                    }
                    all_wires.append(wire)
        
        # Draw all wires with unique colors and transparency
        WIRE_WIDTH = 6  # Consistent width for all wires
        WIRE_ALPHA = 150  # Alpha transparency (0-255, where 0 is fully transparent, 255 is opaque)
        
        for wire in all_wires:
            # Generate a random color for this wire
            color = generate_random_color()
            
            # Convert hex to RGB
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Draw each segment of this wire with the same color and transparency
            for segment in wire['segments']:
                x1, y1, x2, y2 = segment
                # Draw on the PIL image with transparency
                self.wire_draw.line(
                    [(x1, y1), (x2, y2)], 
                    fill=(r, g, b, WIRE_ALPHA), 
                    width=WIRE_WIDTH
                )
        
        # Convert the PIL image to a PhotoImage and display it on the canvas
        self.wire_tk_image = ImageTk.PhotoImage(self.wire_image)
        self.canvas.create_image(0, 0, image=self.wire_tk_image, anchor="nw")

def calculate_bounding_box(gate_dimensions, gate_positions):
    max_x, max_y = 0, 0
    
    for gate_name, position in gate_positions.items():
        if gate_name in gate_dimensions:
            gate_width = gate_dimensions[gate_name]["width"]
            gate_height = gate_dimensions[gate_name]["height"]
            
            max_x = max(max_x, position["x"] + gate_width)
            max_y = max(max_y, position["y"] + gate_height)
    
    return (max_x, max_y)

def main():
    parser = argparse.ArgumentParser(description="Visualize gate placement with wires.")
    parser.add_argument("coordinates_file", help="Path to the output file with gate positions")
    parser.add_argument("dimensions_file", help="Path to the input file with gate dimensions and pins")
    
    args = parser.parse_args()
    
    try:
        # Read input and output files
        with open(args.dimensions_file, 'r') as f:
            input_data = f.readlines()
        
        with open(args.coordinates_file, 'r') as f:
            output_data = f.readlines()
        
        # Parse data
        gate_dimensions, pins, wires = parse_input(input_data)
        gate_positions = parse_output(output_data)
        
        # Calculate absolute pin coordinates and create a list of pin names
        pin_coordinates = []
        pin_names = []
        
        for gate_name, position in gate_positions.items():
            if gate_name in pins:
                gate_x = position["x"]
                gate_y = position["y"]
                
                for i, (px_rel, py_rel) in enumerate(pins[gate_name]):
                    # Calculate absolute pin position
                    px_abs = gate_x + px_rel
                    py_abs = gate_y + py_rel
                    
                    # Store the pin coordinates and name
                    pin_coordinates.append((px_abs, py_abs))
                    pin_names.append(f"{gate_name}.p{i+1}")
        
        # Create connection matrix
        connection_matrix = create_connection_matrix(wires, pin_names)
        
        # Calculate bounding box
        bounding_box = calculate_bounding_box(gate_dimensions, gate_positions)
        
        # Launch visualization
        app = GateVisualizer(gate_dimensions, gate_positions, pins, bounding_box, 
                           connection_matrix, pin_names, pin_coordinates)
        app.mainloop()
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
