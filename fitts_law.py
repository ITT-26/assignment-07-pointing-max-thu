import json
import argparse
import pyglet
import math
import time
import csv
from collections import deque

PARTICIPANT = 1
TRIALS = 2

parser = argparse.ArgumentParser()
parser.add_argument("--participant", type=int)
parser.add_argument("--trials", type=int)
parser.add_argument("--config", type=str, default="fitts_config.json")
parser.add_argument("--output", type=str)
parser.add_argument("--input", type=str, default="mouse")
parser.add_argument("--latency", type=int, default=500)
args = parser.parse_args()


if args.participant is not None:
    PARTICIPANT = args.participant

if args.trials is not None:
    TRIALS = args.trials
    
if args.output is not None:
    OUTPUT_FILE = args.output
else:
    OUTPUT_FILE = f"fitts_law_{args.input}latency_{args.latency}_participant_{PARTICIPANT}.csv"    

with open("fitts_config.json", "r") as f:
    config = json.load(f)

TARGET_AMOUNT = config["target_amount"]
TARGET_SIZES = config["target_sizes"]
TARGET_DISTANCES = config["target_distances"]


class FittsLawApp:
    def __init__(self, participant, trials, output_file):
        self.participant = participant
        self.trials = trials
        self.output_file = output_file
        self.current_trial = 1
        self.window = pyglet.window.Window(800, 600)
        self.window.set_mouse_visible(False)
        self.cursor = pyglet.shapes.Circle(0, 0, radius=5, color=(0, 0, 255))
        self.targets = []
        self.current_target_index = 0
        self.combinations = [(size, distance)
                             for size in TARGET_SIZES for distance in TARGET_DISTANCES]
        self.current_combination_index = 0
        self.create_targets()
        self.hit_count = 0
        self.hits = []
        self.cursor_queue = deque()
        self.cursor_latency = args.latency / 1000.0
        self.click_queue = deque()

    def create_targets(self):
        size, distance = self.combinations[self.current_combination_index]
        radius = distance // 2

        for i in range(TARGET_AMOUNT):
            angle = 2 * math.pi * i / TARGET_AMOUNT
            x = self.window.width // 2 + radius * math.cos(angle)
            y = self.window.height // 2 + radius * math.sin(angle)
            self.targets.append({
                "x": x,
                "y": y,
                "size": size,
                "distance": distance,
                "color": (128, 128, 128)
            })
        self.targets[0]["color"] = (255, 0, 0)

    def handle_mouse_press(self, x, y, button, modifiers):
        self.click_queue.append((x, y, time.time(), button))

    def update_clicks(self, _dt):
        if not self.click_queue:
            return
        selected = None
        now = time.time()
        
        while self.click_queue:
            q_x, q_y, q_time, q_button = self.click_queue[0]
            if now - q_time < self.cursor_latency:
                break
            selected = self.click_queue.popleft()
        
        if selected is None:
            return
        
        current_target = self.targets[self.current_target_index]
        size, distance, target_x, target_y = current_target["size"], current_target["distance"], current_target["x"], current_target["y"]

        dx = self.cursor.x - target_x
        dy = self.cursor.y - target_y
        distance_to_target = math.hypot(dx, dy)

        if distance_to_target <= size // 2:
            self.hit_count += 1
            self.hits.append({
                "iteration": self.current_trial,
                "pid": self.participant,
                "num_targets": TARGET_AMOUNT,
                "target_w": size,
                "target_d": distance,
                "target_id": self.hit_count,
                "timestamp": int(time.time() * 1000)
            })
            if self.hit_count >= TARGET_AMOUNT:
                if self.current_trial < self.trials:
                    self.current_trial += 1
                    self.reset()
                else:
                    if self.current_combination_index + 1 < len(self.combinations):
                        self.current_combination_index += 1
                        self.current_trial = 1
                        self.reset()
                    else:
                        print("All trials completed.")
                        self.save_results()
                        pyglet.app.exit()
            else:
                prev_index = self.current_target_index
                next_index = self.get_next_target_index()
                self.current_target_index = next_index
                self.update_target_color(prev_index)

    def reset(self):
        self.current_target_index = 0
        self.hit_count = 0
        self.targets.clear()
        self.create_targets()

    def update_target_color(self, prev_index):
        self.targets[prev_index]["color"] = (128, 128, 128)
        self.targets[self.current_target_index]["color"] = (255, 0, 0)

    def get_next_target_index(self):
        # Made with ChatGPT
        half = TARGET_AMOUNT // 2
        if self.current_target_index < half:
            return self.current_target_index + half
        else:
            return self.current_target_index - half + 1

    def on_draw(self):
        self.window.clear()
        for target in self.targets:
            pyglet.shapes.Circle(
                target["x"], target["y"], target["size"] // 2, color=target["color"]).draw()
        self.cursor.draw()
        
    def handle_mouse_motion(self, x, y, dx, dy):
        self.cursor_queue.append((x, y, time.time()))
    
    def update_cursor_position(self, _dt):
        if not self.cursor_queue:
            return

        selected = None
        now = time.time()

        while self.cursor_queue:
            q_x, q_y, q_time = self.cursor_queue[0]
            if now - q_time < self.cursor_latency:
                break
            selected = self.cursor_queue.popleft()

        if selected is None:
            return

        x, y, q_time = selected
        self.cursor.x = x
        self.cursor.y = y

    def save_results(self):
        filename = self.output_file
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.hits[0].keys())
            writer.writeheader()
            writer.writerows(self.hits)

def main():
    app = FittsLawApp(PARTICIPANT, TRIALS, OUTPUT_FILE)

    @app.window.event
    def on_draw():
        app.on_draw()

    @app.window.event
    def on_mouse_press(x, y, button, modifiers):
        app.handle_mouse_press(x, y, button, modifiers)
        pass
    
    @app.window.event
    def on_mouse_motion(x, y, dx, dy):
        app.handle_mouse_motion(x, y, dx, dy)

    pyglet.clock.schedule_interval(app.update_cursor_position, 1/500)
    pyglet.clock.schedule_interval(app.update_clicks, 1/500)
    pyglet.app.run()


if __name__ == "__main__":
    main()
