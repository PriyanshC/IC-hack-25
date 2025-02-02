import multiprocessing as mp
import time
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

# Node process
def node_process(node_id, state_queue, ui_queue):
    state = "safe"  # Default state
    while True:
        # Mock other nodes (assume they are safe unless told otherwise)
        if not state_queue.empty():
            state = state_queue.get()
        
        # Send state to UI
        ui_queue.put((node_id, state))
        time.sleep(1)  # Simulate process delay

# Edge process
def edge_process(edge_id, state_queue, ui_queue):
    state = "safe route"  # Default state
    while True:
        if not state_queue.empty():
            state = state_queue.get()
        
        # Send state to UI
        ui_queue.put((edge_id, state))
        time.sleep(1)  # Simulate process delay

# UI process
def ui_process(node_ui_queues, edge_ui_queues):
    root = tk.Tk()
    root.title("Node and Edge States")
    canvas = Canvas(root, width=800, height=600)
    canvas.pack()

    # Load images for UI
    fire_img = ImageTk.PhotoImage(Image.open("fire.png").resize((50, 50)))
    trapped_img = ImageTk.PhotoImage(Image.open("triangle.png").resize((50, 50)))
    safe_img = ImageTk.PhotoImage(Image.open("exit.png").resize((50, 50)))
    go_faster_img = ImageTk.PhotoImage(Image.open("running_man.png").resize((50, 50)))

    # Create UI sections for nodes and edges
    node_sections = {}
    edge_sections = {}

    # Initialize node sections
    for i, queue in enumerate(node_ui_queues):
        x = (i % 4) * 200
        y = (i // 4) * 200
        node_sections[i] = canvas.create_rectangle(x, y, x + 100, y + 100, fill="white")
        canvas.create_text(x + 50, y + 50, text=f"Node {i}")

    # Initialize edge sections
    for i, queue in enumerate(edge_ui_queues):
        x = (i % 4) * 200 + 100
        y = (i // 4) * 200 + 100
        edge_sections[i] = canvas.create_rectangle(x, y, x + 100, y + 100, fill="white")
        canvas.create_text(x + 50, y + 50, text=f"Edge {i}")

    # Update UI based on node and edge states
    def update_ui():
        for i, queue in enumerate(node_ui_queues):
            if not queue.empty():
                node_id, state = queue.get()
                if state == "fire":
                    canvas.itemconfig(node_sections[node_id], image=fire_img)
                elif state == "trapped":
                    canvas.itemconfig(node_sections[node_id], image=trapped_img)
                else:
                    canvas.itemconfig(node_sections[node_id], image=safe_img)

        for i, queue in enumerate(edge_ui_queues):
            if not queue.empty():
                edge_id, state = queue.get()
                if state == "fire ahead":
                    canvas.itemconfig(edge_sections[edge_id], image=fire_img)
                elif state == "trapped":
                    canvas.itemconfig(edge_sections[edge_id], image=trapped_img)
                elif state == "go faster":
                    canvas.itemconfig(edge_sections[edge_id], image=go_faster_img)
                else:
                    canvas.itemconfig(edge_sections[edge_id], image=safe_img)

        root.after(100, update_ui)  # Update UI every 100ms

    update_ui()
    root.mainloop()

# Main function
if __name__ == "__main__":
    # Create queues for communication
    node_state_queues = [mp.Queue() for _ in range(12)]  # 12 nodes
    edge_state_queues = [mp.Queue() for _ in range(24)]  # 24 edges
    node_ui_queues = [mp.Queue() for _ in range(12)]
    edge_ui_queues = [mp.Queue() for _ in range(24)]

    # Start node processes
    node_processes = []
    for i in range(12):
        p = mp.Process(target=node_process, args=(i, node_state_queues[i], node_ui_queues[i]))
        p.start()
        node_processes.append(p)

    # Start edge processes
    edge_processes = []
    for i in range(24):
        p = mp.Process(target=edge_process, args=(i, edge_state_queues[i], edge_ui_queues[i]))
        p.start()
        edge_processes.append(p)

    # Start UI process
    ui_process = mp.Process(target=ui_process, args=(node_ui_queues, edge_ui_queues))
    ui_process.start()

    # Simulate state changes
    time.sleep(2)
    node_state_queues[0].put("fire")  # Set node 0 on fire
    edge_state_queues[0].put("fire ahead")  # Set edge 0 to "fire ahead"
    time.sleep(2)
    node_state_queues[1].put("trapped")  # Set node 1 as trapped
    edge_state_queues[1].put("trapped")  # Set edge 1 as trapped
    time.sleep(2)
    edge_state_queues[2].put("go faster")  # Set edge 2 to "go faster"

    # Wait for processes to finish
    for p in node_processes:
        p.join()
    for p in edge_processes:
        p.join()
    ui_process.join()