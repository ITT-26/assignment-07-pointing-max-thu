import json
import argparse
import pyglet
import time
import csv
import pyautogui
from collections import deque
import random

PARTICIPANT = 3
TRIALS = 2

parser = argparse.ArgumentParser()
parser.add_argument("--participant", type=int)
parser.add_argument("--trials", type=int)
parser.add_argument("--config", type=str, default="steering_config.json")
parser.add_argument("--output", type=str)
parser.add_argument("--input", type=str, default="mouse")
parser.add_argument("--latency", type=int, default=0)
args = parser.parse_args()

if args.participant is not None:
    PARTICIPANT = args.participant

if args.trials is not None:
    TRIALS = args.trials

if args.output is not None:
    OUTPUT_FILE = args.output
else:
    OUTPUT_FILE = f"steering_law_{args.input}_latency_{args.latency}_participant_{PARTICIPANT}.csv"

with open(args.config, "r") as f:
    config = json.load(f)

PATH_LENGTH = config["path_length"]
PATH_WIDTH = config["path_width"]


class SteeringLawApp:
    def __init__(self, participant, trials, output_file):
        self.last_x = None
        self.last_y = None
        self.participant = participant
        self.trials = trials
        self.output_file = output_file
        self.current_trial = 1
        self.window = pyglet.window.Window(800, 600)
        self.window.set_mouse_visible(False)
        self.cursor = pyglet.shapes.Circle(0, 0, radius=5, color=(0, 0, 255))
        self.path = None
        self.current_path_index = 0
        self.combinations = [(length, width)
                             for length in PATH_LENGTH for width in PATH_WIDTH]
        random.shuffle(self.combinations)
        self.current_combination_index = 0
        self.create_path()
        self.run_started = False
        self.start_timestamp = None
        self.results = []
        self.cursor_queue = deque()
        self.cursor_latency = args.latency / 1000.0
        self.trial_label = pyglet.text.Label(
            f"Trial: {self.current_trial}/{self.trials} | Combination: {self.current_combination_index + 1}/{len(self.combinations)}",
            font_name='Arial',
            font_size=14,
            x=10,
            y=self.window.height - 20,
            anchor_x='left',
            anchor_y='top',
            color=(255, 255, 255, 255)
        )
        self.feedback_label = pyglet.text.Label(
            "",
            font_name='Arial',
            font_size=14,
            x=self.window.width // 2,
            y=self.window.height // 2,
            anchor_x='center',
            anchor_y='center',
            color=(255, 0, 0, 255)
        )
        self.feedback_timer = 0

    def create_path(self):
        length, width = self.combinations[self.current_combination_index]
        starting_x = self.window.width // 2 - length // 2
        starting_y = self.window.height // 2 - width // 2

        self.path = {
            "x": starting_x,
            "y": starting_y,
            "length": length,
            "width": width,
        }

    def on_draw(self):
        self.window.clear()
        line_width = 2

        pyglet.shapes.Rectangle(
            self.path["x"], self.path["y"], self.path["length"], self.path["width"], color=(128, 128, 128)).draw()
        pyglet.shapes.Rectangle(self.path["x"]-line_width, self.path["y"],
                                line_width, self.path["width"], color=(255, 0, 0)).draw()
        pyglet.shapes.Rectangle(self.path["x"] + self.path["length"], self.path["y"],
                                line_width, self.path["width"], color=(0, 255, 0)).draw()
        self.cursor.draw()
        self.trial_label.draw()
        if time.time() < self.feedback_timer:
            self.feedback_label.draw()

    def check_inside_path(self, x, y):
        if (self.path["x"] <= x <= self.path["x"] + self.path["length"] and
                self.path["y"] <= y <= self.path["y"] + self.path["width"]):
            return True
        return False

    def check_crossed_start(self, old_x, new_x, new_y):
        if old_x < self.path["x"] <= new_x and self.path["y"] <= new_y <= self.path["y"] + self.path["width"]:
            return True
        return False

    def check_crossed_end(self, old_x,  new_x, new_y):
        end_line_x = self.path["x"] + self.path["length"]
        end_line_y = self.path["y"] + self.path["width"]
        if old_x < end_line_x <= new_x and self.path["y"] <= new_y <= end_line_y:
            return True
        return False

    def update_cursor(self, _dt):

        if not self.cursor_queue:
            return
        # print(len(self.cursor_queue))
        """
        q_x, q_y, q_time = self.cursor_queue[0]
        now = time.time()
        if now - q_time >= self.cursor_latency:
        """
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
        delay = now - q_time
        print(delay * 1000)

        self.cursor.x = x
        self.cursor.y = y
        """
        x, y = q_x, q_y
        self.cursor_queue.popleft()
        """
        # Mid-Air Pointing delivers no dx and dy, so we need to calculate them ourselves
        if self.last_x is None:
            self.last_x = x
            self.last_y = y
            return

        old_x = self.last_x
        old_y = self.last_y
        self.last_x = x
        self.last_y = y

        # old_x= x - dx

        if self.check_crossed_start(old_x, x, y):
            if not self.run_started:
                self.run_started = True
                self.start_timestamp = time.time()

        if self.run_started:
            if self.check_crossed_end(old_x, x, y):
                self.handle_successful_run(self.start_timestamp, time.time())
                return

            if not self.check_inside_path(x, y):
                self.feedback_label.text = "Failure!"
                self.feedback_timer = time.time() + 1.0
                self.log_results(False, self.start_timestamp, time.time())
                self.run_started = False
                self.start_timestamp = None

    def handle_mouse_motion(self, x, y, dx, dy):
        self.cursor_queue.append((x, y, time.time()))

    def log_results(self, success, start_time, end_time):
        self.results.append({
            "iteration": self.current_trial,
            "pid": self.participant,
            "path_length": self.path["length"],
            "path_width": self.path["width"],
            "start_time": int(start_time * 1000),
            "end_time": int(end_time * 1000),
            "success": success,
            "input_method": args.input,
            "latency": args.latency,
        })

    def handle_successful_run(self, start_time, end_time):
        self.log_results(True, start_time, end_time)
        self.run_started = False
        self.start_timestamp = None
        self.feedback_label.text = "Success!"
        self.feedback_timer = time.time() + 1.0
        # window_x, window_y = self.window.get_location()
        # start_x = window_x + self.window.width * 0.05
        # start_y = window_y + self.path["y"] + self.path["width"] // 2
        # pyautogui.moveTo(start_x, start_y)
        self.cursor_queue.clear()
        self.last_x = None
        self.last_y = None
        if self.current_combination_index < len(self.combinations) - 1:
            self.current_combination_index += 1
            self.create_path()
            self.trial_label.text = f"Trial: {self.current_trial}/{self.trials} | Combination: {self.current_combination_index + 1}/{len(self.combinations)}"
        else:
            if self.current_trial < self.trials:
                self.current_trial += 1
                self.current_combination_index = 0
                self.trial_label.text = f"Trial: {self.current_trial}/{self.trials} | Combination: {self.current_combination_index + 1}/{len(self.combinations)}"
                random.shuffle(self.combinations)
                self.create_path()
            else:
                self.save_results()
                pyglet.app.exit()

    def save_results(self):
        filename = self.output_file
        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.results[0].keys())
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)


def main():
    app = SteeringLawApp(PARTICIPANT, TRIALS, OUTPUT_FILE)
    pyglet.clock.schedule_interval(app.update_cursor, 1/1000)

    @app.window.event
    def on_draw():
        app.on_draw()

    @app.window.event
    def on_mouse_motion(x, y, dx, dy):
        app.handle_mouse_motion(x, y, dx, dy)

    pyglet.app.run()


if __name__ == "__main__":
    main()
