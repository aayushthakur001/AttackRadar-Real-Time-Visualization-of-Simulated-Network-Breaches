import tkinter as tk
import pandas as pd
import random
from PIL import Image, ImageTk
import csv
from tkinter import filedialog
import winsound
import requests
import heapq

# === BFS Graph (Unweighted) ===
bfs_graph = {
    '192.168.1.1': ['192.168.1.2', '192.168.1.3'],
    '192.168.1.2': ['192.168.1.4'],
    '192.168.1.3': ['192.168.1.5'],
    '192.168.1.4': ['192.168.1.6'],
    '192.168.1.5': ['192.168.1.6'],
    '192.168.1.6': []
}

# === Dijkstra Graph (Weighted) ===
dijkstra_graph = {
    '192.168.1.1': {'192.168.1.2': 2, '192.168.1.3': 4},
    '192.168.1.2': {'192.168.1.4': 1},
    '192.168.1.3': {'192.168.1.5': 2},
    '192.168.1.4': {'192.168.1.6': 5},
    '192.168.1.5': {'192.168.1.6': 1},
    '192.168.1.6': {}
}

# === BFS Path ===
def bfs_path(graph, start, goal):
    visited = set()
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.get(vertex, []):
                if neighbor == goal:
                    return path + [neighbor]
                else:
                    queue.append((neighbor, path + [neighbor]))
    return None

# === Dijkstra Path ===
def dijkstra(graph, start, goal):
    queue = [(0, start, [start])]
    visited = set()
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node == goal:
            return path
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in graph.get(node, {}).items():
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
    return None

# === Load attack data ===
df = pd.read_csv("attack_data.csv")
df = df[['Timestamp', 'Source IP', 'Destination IP', 'Attack Type', 'Severity']]

current_index = 0

# === GUI Setup ===
root = tk.Tk()
root.title("Cyber Attack Visualizer")
root.geometry("1000x800")
root.configure(bg="#1e1e1e")

title_label = tk.Label(root, text="Cyber Attack Visualizer", font=("Helvetica", 24, "bold"), fg="cyan", bg="#1e1e1e")
title_label.pack(pady=10)

feed_frame = tk.Frame(root, bg="#1e1e1e")
feed_frame.pack(pady=10)

feed_label = tk.Label(feed_frame, text="Live Attack Feed", font=("Helvetica", 14, "bold"), fg="white", bg="#1e1e1e")
feed_label.pack(anchor="w")

feed_listbox = tk.Listbox(feed_frame, width=120, height=10, bg="black", fg="lime", font=("Courier", 10))
feed_listbox.pack()

canvas_label = tk.Label(root, text="Network Attack Map", font=("Helvetica", 14, "bold"), fg="white", bg="#1e1e1e")
canvas_label.pack(pady=(10, 0))

canvas = tk.Canvas(root, width=900, height=300, bg='black', highlightthickness=1, highlightbackground="gray")
canvas.pack(pady=10)

img = Image.open("assets/attack_chart.png")
img = img.resize((500, 300))
img_tk = ImageTk.PhotoImage(img)
img_label = tk.Label(root, image=img_tk, bg="#1e1e1e")
img_label.pack(pady=(20, 20), anchor="center")

# === Export Feed ===
def export_feed():
    export_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if export_path:
        with open(export_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Source IP", "Destination IP", "Attack Type", "Severity"])
            for i in range(feed_listbox.size()):
                parts = feed_listbox.get(i).split(" | ")
                time_ip = parts[0].split("] ")
                time = time_ip[0].strip("[")
                ip_info = time_ip[1].split(" → ")
                writer.writerow([time, ip_info[0], ip_info[1], parts[1], parts[2].split(": ")[1]])

# === Status Frame ===
status_frame = tk.Frame(root, bg="#1e1e1e")
status_frame.pack(pady=10)

status_label = tk.Label(status_frame, text="Status: Waiting", font=('Arial', 12), fg="white", bg="#1e1e1e")
status_label.pack(side=tk.LEFT, padx=10)

export_button = tk.Button(status_frame, text="Export Feed to CSV", command=export_feed, bg="#333", fg="white")
export_button.pack(side=tk.RIGHT, padx=10)

# === Sound Toggle ===
sound_enabled = tk.BooleanVar(value=True)

sound_toggle_button = tk.Checkbutton(status_frame, text="Enable Sound", variable=sound_enabled,
                                    onvalue=True, offvalue=False, bg="#1e1e1e", fg="white",
                                    selectcolor="#333", font=('Arial', 10))
sound_toggle_button.pack(side=tk.RIGHT, padx=10)

# === Algorithm Selector ===
algorithm_var = tk.StringVar(value="BFS")

algorithm_menu = tk.OptionMenu(status_frame, algorithm_var, "BFS", "Dijkstra", "A*")
algorithm_menu.config(bg="#1e1e1e", fg="white", font=('Arial', 10))
algorithm_menu.pack(side=tk.RIGHT, padx=10)

# === Draw Path ===
def draw_attack_path(path, severity):
    color = {"High": "red", "Medium": "orange", "Low": "green"}.get(severity, "white")
    points = []
    x_start, y_start = 100, 150
    x_gap = 100
    for i in range(len(path)):
        x = x_start + i * x_gap
        y = random.randint(100, 200)
        points.append((x, y))
        canvas.create_oval(x-4, y-4, x+4, y+4, fill="yellow")
        # Add labels for each node
        canvas.create_text(x, y-10, text=path[i], fill="white", font=("Arial", 8))
    for i in range(len(points)-1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

# === Fallback Draw ===
def draw_attack(source, target, severity):
    x1, y1 = random.randint(50, 350), random.randint(50, 250)
    x2, y2 = random.randint(450, 750), random.randint(50, 250)
    color = {"High": "red", "Medium": "orange", "Low": "green"}.get(severity, "white")
    canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
    canvas.create_oval(x1-3, y1-3, x1+3, y1+3, fill="blue")
    canvas.create_oval(x2-3, y2-3, x2+3, y2+3, fill="yellow")

# === Update Feed ===
def update_feed():
    global current_index
    if current_index < len(df):
        row = df.iloc[current_index]
        attack_str = f"[{row['Timestamp']}] {row['Source IP']} → {row['Destination IP']} | {row['Attack Type']} | Severity: {row['Severity']}"
        feed_listbox.insert(tk.END, attack_str)

        if algorithm_var.get() == "BFS":
            path = bfs_path(bfs_graph, row['Source IP'], row['Destination IP'])
        else:
            path = dijkstra(dijkstra_graph, row['Source IP'], row['Destination IP'])

        if path:
            draw_attack_path(path, row['Severity'])
        else:
            draw_attack(row['Source IP'], row['Destination IP'], row['Severity'])

        if row['Severity'] == "High" and sound_enabled.get():
            winsound.Beep(1000, 500)
        status_label.config(text=f"Status: Showing attack {current_index + 1}/{len(df)}")
        current_index += 1
        root.after(1500, update_feed)
    else:
        status_label.config(text="Status: No more attacks.")

# === Start Button ===
tk.Button(root, text="Start Simulation", command=update_feed).pack(pady=10)

update_feed()
root.mainloop()
