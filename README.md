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