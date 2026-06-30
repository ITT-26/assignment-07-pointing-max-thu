[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KfEU5Azw)
# Assignment 7 - Task 1: Pose-Based Pointing Technique

## Description

This application uses MediaPipe Hand Landmarker to control the mouse cursor using hand gestures captured by a webcam.

The index fingertip is mapped to the mouse cursor position. A pinch gesture between the thumb and index finger is used for clicking. The application also supports double-clicking and drag-and-drop interactions.

To improve usability, the implementation includes:

* Cursor smoothing
* Dead-zone filtering to reduce jitter
* Pinch gesture detection
* Single click
* Double click
* Drag-and-drop

## Requirements

Install all required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python pointing_input.py
```

A webcam is required.

Press **Q** to quit the application.

## Controls

| Gesture                               | Action        |
| ------------------------------------- | ------------- |
| Move index finger                     | Move cursor   |
| Short pinch (thumb + index finger)    | Left click    |
| Two short pinches in quick succession | Double click  |
| Hold pinch for at least 0.5 seconds   | Drag and drop |

For stable cursor movement, keep the thumb clearly away from the index finger. Pinch only when clicking or dragging.

## Notes

The original MediaPipe sample code provided in the course was written for MediaPipe 0.10.35. Because MediaPipe 0.10.35 could not be installed on my Intel-based MacBook, the helper file `mediapipe_sample_code/hand_landmark_drawer.py` was slightly modified to work with MediaPipe 0.10.21. The changes only affect landmark visualization and compatibility with the older MediaPipe version. The hand tracking functionality and interaction logic remain unchanged.


# Task 2 & Task 3 – Fitts' Law & Steering Law

## Requirements

Before running the applications, install all required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Applications

Run either application directly:

```bash
python fitts_law.py
```

or

```bash
python steering_law.py
```

The experiment starts immediately after launching the application. No additional input is required to begin.

---

## Configuration Files

Both applications can be configured using a JSON configuration file.

### Fitts' Law

The default configuration file is:

```
fitts_config.json
```

The following parameters can be changed:

- `target_amount`
- `target_sizes`
- `target_distances`

### Steering Law

The default configuration file is:

```
steering_config.json
```

The following parameters can be changed:

- `path_length`
- `path_width`

---

## Command Line Arguments

Both applications support the same command line arguments.

| Argument | Type | Description |
|----------|------|-------------|
| `--participant` | Integer | Participant ID stored in the output file. |
| `--trials` | Integer | Number of trials to perform. |
| `--config` | String | Path to a custom configuration file. If omitted, the default configuration is used. |
| `--output` | String | Output CSV filename. If omitted, a default filename is generated automatically. |
| `--input` | String | Name of the input device used (stored in the logged data). |
| `--latency` | Integer | Adds an artificial cursor latency in milliseconds. |

Example:

```bash
python fitts_law.py --participant 1 --trials 3 --input mouse --latency 150
```

---

## Experiment Procedure

Both applications automatically start with the first trial after launching.

A status label in the upper left corner continuously displays:

- the current trial
- the current parameter combination

The applications automatically iterate through all parameter combinations. The order of the parameter combinations is randomized for every trial.

After all trials and parameter combinations have been completed, the application automatically closes and stores all recorded data as a CSV file.

---

## Fitts' Law

The experiment consists of a circular arrangement of targets.

- The currently active target is displayed in **red**.
- Participants click on the red target.
- After a successful click, the next target becomes active automatically.
- The target order alternates across the circle according to the standard Fitts' Law target sequence.

---

## Steering Law

The experiment displays a straight tunnel.

- Participants begin by crossing the **red** start line.
- They steer the cursor through the tunnel without leaving its boundaries.
- The trial ends successfully after crossing the **green** finish line.
- Leaving the tunnel results in a failed attempt, which is logged before the participant repeats the same parameter combination.