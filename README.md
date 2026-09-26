# DCC Scene Organizer

A Blender Python tool for validating object naming conventions and organizing scene collections.

DCC Scene Organizer was created to reduce repetitive scene-cleanup work and help maintain consistent naming and collection structures during 3D production.

> **Status:** MVP / Portfolio Project

---

## Overview

In 3D production, scenes can quickly become difficult to manage due to:

- Inconsistent object naming
- Blender default names such as `Cube.001`
- Mixed object types in collections
- Repetitive manual cleanup
- Naming conflicts when duplicated objects are created

DCC Scene Organizer scans the current Blender scene, detects naming issues, automatically fixes supported problems, and organizes objects into predefined collections.

---

## Demo

> Add `demo/dcc_scene_organizer.gif` here after recording the demo.

Recommended demo flow:

**Messy Scene → Fix All → Organized Scene**

---

## Features

### Scene Scan

Scans supported objects in the current scene.

Supported object types:

- Mesh
- Camera
- Light

The tool also displays a Scene Status summary directly in the UI.

---

### Naming Convention Validation

Objects are checked against predefined naming rules.

| Object Type | Prefix |
|---|---|
| Mesh | `GEO_` |
| Camera | `CAM_` |
| Light | `LGT_` |

Example:

```text
Cube      → GEO_Cube
Camera    → CAM_Camera
Light     → LGT_Light
```

---

### Blender Suffix Cleanup

Blender-generated suffixes such as:

```text
GEO_Cube.001
```

are detected and converted to a cleaner numbering format.

```text
GEO_Cube.001
↓
GEO_Cube_01
```

---

### Name Collision Handling

Before assigning a numbered name, the tool checks whether that name is already being used.

Example:

```text
GEO_Cube_01
GEO_Cube_02
GEO_Cube_03
```

If a new `Cube.001` is processed, the tool automatically searches for the next available number.

```text
Cube.001
↓
GEO_Cube_04
```

This prevents duplicate naming conflicts.

---

## Collection Organization

Objects are automatically organized under a dedicated root collection.

```text
DCC_Organizer
├── Geometry
│   ├── GEO_Cube
│   └── GEO_Character
├── Cameras
│   └── CAM_Main
└── Lights
    └── LGT_Key
```

### Add Link Mode

Keeps the object's existing collection links and also links the object to the appropriate `DCC_Organizer` collection.

This provides a non-destructive organization option.

### Move Mode

Removes previous collection links and moves the object into the appropriate `DCC_Organizer` collection.

Because this operation changes the existing scene structure, a confirmation dialog is displayed before execution.

---

## Fix All

`Fix All` combines the main cleanup operations into a single action.

```text
Scene Scan
    ↓
Naming Validation
    ↓
Auto Rename
    ↓
Name Collision Check
    ↓
Collection Organization
```

This allows common scene-cleanup tasks to be performed with one button.

---

## Scene Status UI

The Blender sidebar displays the current scene status.

Example:

```text
Scene Status

Meshes: 7
Cameras: 1
Lights: 1
Naming Issues: 2
```

Naming problems are also shown directly inside the panel.

```text
Problem Objects

Cube             Missing Prefix
GEO_Cube.001     Blender Suffix
```

When no naming problems are detected:

```text
No naming issues found
```

is displayed.

---

## User Feedback

The tool provides execution feedback directly in the UI.

Example:

```text
Last Result

Fixed 2 naming issue(s)
```

or:

```text
Fixed 2 naming issue(s) and organized 9 object(s)
```

Warnings and errors are also reported when an operation cannot be completed.

---

## Safety Features

The tool includes several safeguards for scene editing.

- Undo support
- Confirmation dialog for Move operations
- Non-destructive Add Link mode
- Empty-scene handling
- Name collision prevention
- Duplicate collection prevention
- Repeated execution stability
- Runtime error handling

---

## Testing

The tool was tested using several scene conditions.

### Test 01 — Clean Scene

A scene that already follows the expected naming and collection rules.

Results:

- No naming changes
- No duplicate collections
- No duplicate links
- No errors during repeated execution

### Test 02 — Messy Naming

Example input:

```text
Cube
Cube.001
Mesh
Light
Camera
```

Expected result:

```text
GEO_Cube
GEO_Cube_01
GEO_Mesh
LGT_Light
CAM_Camera
```

Result: Passed.

### Test 03 — Number Collision

Existing objects:

```text
GEO_Cube_01
GEO_Cube_02
GEO_Cube_03
```

New object:

```text
Cube.001
```

Result:

```text
GEO_Cube_04
```

Result: Passed.

### Test 04 — Complex Collections

Tested with existing custom collections such as:

```text
Character
Props
TestCollection
```

Verified:

- Add Link preserves existing collection links
- Move removes previous links
- Undo restores the previous scene state

Result: Passed.

### Test 05 — Empty Scene

When no supported objects are found, the tool safely cancels the operation and displays:

```text
No supported objects found
```

Result: Passed.

### Test 06 — Repeated Execution

`Fix All` was executed repeatedly on an already-organized scene.

Verified:

- No duplicate names
- No duplicate collections
- No duplicate links
- No execution errors
- Scene structure remains stable

Result: Passed.

---

## Project Structure

```text
DCC-Scene-Organizer/
│
├── README.md
├── scene_organizer.py
│
├── screenshots/
│   ├── before.png
│   ├── after.png
│   └── ui.png
│
└── demo/
    └── dcc_scene_organizer.gif
```

---

## Usage

1. Open Blender.
2. Open the **Scripting** workspace.
3. Load `scene_organizer.py`.
4. Run the script.
5. Open the 3D Viewport sidebar with `N`.
6. Select the **DCC Organizer** tab.
7. Use:
   - `Scan Scene`
   - `Fix Names`
   - `Organize Collections`
   - `Fix All`

---

## Technical Structure

The tool is separated into several functional areas.

```text
Scene Scan
↓
Naming Validation
↓
Rename Logic
↓
Collection Organization
↓
Scene Status
↓
Blender Operators
↓
UI Panel
```

### Technologies

- Python
- Blender Python API (`bpy`)
- Regular Expressions (`re`)

---

## Development Goals

This project was created not only to automate scene cleanup, but also to explore Technical Artist tool-development concepts such as:

- Artist workflow automation
- Naming convention management
- Non-destructive workflows
- Scene validation
- Error handling
- User feedback
- Undo support
- Tool usability
- Repeated-operation safety

---

## Future Improvements

Possible future improvements include:

- Custom naming presets
- User-defined prefix rules
- Additional Blender object types
- Batch validation
- Validation report export
- Add-on packaging
- 3ds Max version
