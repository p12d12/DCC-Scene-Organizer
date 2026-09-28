# DCC Scene Organizer

Blender上のオブジェクト命名規則のチェックと、Collection整理を自動化するPythonツールです。

3D制作時に発生する反復的なシーン整理作業を削減し、一定のNaming Conventionを維持することを目的として制作しました。

Technical Artistを志望する上で、単純なスクリプト作成だけではなく、実際にアーティストが使用することを想定した操作性・安全性・エラー処理まで含めて実装しています。

---

## Demo

![DCC Scene Organizer Demo](demo/dcc_scene_organizer.gif)

**Messy Scene → Fix All → Organized Scene**

`Fix All`を実行することで、命名規則の修正とCollection整理をまとめて行うことができます。

---

## 概要

3D制作では、作業が進むにつれて以下のような問題が発生することがあります。

- オブジェクト名のルールが統一されていない
- `Cube.001`などBlenderのデフォルト名が残っている
- Mesh / Camera / Lightが複数のCollectionに混在している
- シーン整理を手作業で繰り返す必要がある
- オブジェクト複製時に名前の重複管理が必要になる

DCC Scene Organizerでは、現在のSceneをScanし、命名規則に違反しているオブジェクトを検出・修正した上で、オブジェクトタイプごとにCollectionを整理します。

---

## Before / After

### Before

整理前のScene例です。

![Before](screenshots/before.png)

```text
Scene Collection
├── Cube
├── Cube.001
├── Mesh
├── Light
└── Camera
```

Naming Conventionに一致していないオブジェクトを自動的に検出し、UI上にNaming Issueとして表示します。

### After

`Fix All`実行後：

![After](screenshots/after.png)

```text
DCC_Organizer
├── Geometry
│   ├── GEO_Cube
│   ├── GEO_Cube_01
│   └── GEO_Mesh
├── Lights
│   └── LGT_Light
└── Cameras
    └── CAM_Camera
```

---

## 主な機能

### Scene Scan

現在のScene内から対応オブジェクトを取得します。

対応しているObject Type：

- Mesh
- Camera
- Light

---

### Naming Convention Validation

Object TypeごとにPrefixルールを設定しています。

| Object Type | Prefix |
| --- | --- |
| Mesh | `GEO_` |
| Camera | `CAM_` |
| Light | `LGT_` |

例：

```text
Cube   → GEO_Cube
Camera → CAM_Camera
Light  → LGT_Light
```

Naming Conventionに一致していないオブジェクトはProblem Objectとして検出されます。

---

### Blender Suffix Cleanup

Blenderでオブジェクトを複製した際に自動付与される`.001`形式のSuffixを検出し、独自の番号形式へ変換します。

```text
GEO_Cube.001
↓
GEO_Cube_01
```

---

### Name Collision Handling

リネームを行う前に、同じ名前がすでにScene内で使用されていないか確認します。

例えば以下の名前が存在している場合：

```text
GEO_Cube_01
GEO_Cube_02
GEO_Cube_03
```

新しく：

```text
Cube.001
```

を処理すると、使用可能な次の番号を検索し：

```text
Cube.001
↓
GEO_Cube_04
```

へ自動的に変更します。

これにより名前の重複を防止します。

---

## Collection Organization

Object Typeごとに、`DCC_Organizer`配下へ自動分類します。

```text
DCC_Organizer
├── Geometry
├── Cameras
└── Lights
```

### Add Link

既存Collectionとのリンクを保持したまま、`DCC_Organizer`側にもオブジェクトを追加します。

既存のアーティスト作業構造を変更しない、Non-Destructiveな整理方法です。

### Move

既存Collectionとのリンクを解除し、`DCC_Organizer`配下へオブジェクトを移動します。

既存Scene構造を変更する操作のため、実行前にConfirmation Dialogを表示するようにしています。

---

## Fix All

`Fix All`では、主要なScene Cleanup処理を一度に実行できます。

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

複数の整理作業を1つの操作で完了できるようにしました。

---

## User Interface

![DCC Scene Organizer UI](screenshots/ui.png)

BlenderのSidebarから各機能を操作できます。

UI上では以下の情報・機能を確認できます。

- Mesh / Camera / Light数
- Naming Issue数
- Problem Object一覧
- Scan Scene
- Fix Names
- Collection Mode選択
- Organize Collections
- Fix All
- Last Result

例：

```text
Scene Status

Meshes: 3
Cameras: 1
Lights: 1
Naming Issues: 0

No naming issues found
```

---

## Problem Detection

命名規則に問題がある場合、対象オブジェクトと原因をUI上に表示します。

例：

```text
Problem Objects

Cube             Missing Prefix
GEO_Cube.001     Blender Suffix
```

System Consoleを開かなくても、問題のあるオブジェクトを確認できるようにしています。

---

## User Feedback

各処理を実行した後、最後の実行結果をUI上に保持します。

例：

```text
Last Result

Fixed 2 naming issue(s)
```

または：

```text
Fixed 2 naming issue(s) and organized 5 object(s)
```

対応オブジェクトが存在しない場合や処理に失敗した場合も、Warning / Errorを表示します。

---

## Safety Features

実際の制作Sceneで使用することを想定し、以下の安全対策を実装しました。

- Undo対応
- Move実行前のConfirmation Dialog
- Non-DestructiveなAdd Link Mode
- Empty Sceneへの対応
- Name Collision Prevention
- Collectionの重複生成防止
- 繰り返し実行時の安定性
- Runtime Error Handling

---

## Testing

複数のScene状態を想定して動作検証を行いました。

### Test 01 — Clean Scene

すでにNaming / Collectionルールに従って整理されているSceneでテストしました。

確認項目：

- 不要なリネームが発生しない
- Collectionが重複生成されない
- オブジェクトが重複リンクされない
- Fix Allを繰り返し実行してもエラーが発生しない

**Result: Passed**

---

### Test 02 — Messy Naming

入力：

```text
Cube
Cube.001
Mesh
Light
Camera
```

期待される結果：

```text
GEO_Cube
GEO_Cube_01
GEO_Mesh
LGT_Light
CAM_Camera
```

**Result: Passed**

---

### Test 03 — Number Collision

既存オブジェクト：

```text
GEO_Cube_01
GEO_Cube_02
GEO_Cube_03
```

追加オブジェクト：

```text
Cube.001
```

結果：

```text
GEO_Cube_04
```

**Result: Passed**

---

### Test 04 — Complex Collections

以下のような既存Collectionを用意してテストしました。

```text
Character
Props
TestCollection
```

確認項目：

- Add Linkで既存Collectionリンクを維持
- Moveで既存Collectionリンクを解除
- Undoで処理前の状態へ復元

**Result: Passed**

---

### Test 05 — Empty Scene

対応するオブジェクトが存在しない場合：

```text
No supported objects found
```

を表示し、安全に処理をキャンセルします。

**Result: Passed**

---

### Test 06 — Repeated Execution

整理済みSceneに対して`Fix All`を複数回実行しました。

確認項目：

- 名前が重複しない
- Collectionが重複生成されない
- オブジェクトが重複リンクされない
- エラーが発生しない
- Scene構造が維持される
- Last Resultが正常に更新される

**Result: Passed**

---

## 使用方法

1. Blenderを起動します。
2. `Scripting` Workspaceを開きます。
3. `scene_organizer.py`を読み込みます。
4. `Run Script`を実行します。
5. 3D Viewportに戻ります。
6. `N`キーでSidebarを開きます。
7. `DCC Organizer`タブを選択します。
8. 必要な機能を実行します。

主な操作：

- `Scan Scene`
- `Fix Names`
- `Organize Collections`
- `Fix All`

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

## Technical Structure

スクリプト内部では、役割ごとに処理を分けています。

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

### 使用技術

- Python
- Blender Python API (`bpy`)
- Regular Expression (`re`)

---

## 制作を通して意識したこと

このプロジェクトでは単にScene Cleanupを自動化するだけではなく、Technical ArtistとしてのTool Developmentを意識し、以下の点を考慮しました。

- Artist Workflowの自動化
- Naming Conventionの管理
- Scene Validation
- Non-Destructive Workflow
- Destructive Operationの安全対策
- Undo対応
- Error Handling
- User Feedback
- 繰り返し実行時の安定性
- UI / Usability

一度だけ動作するスクリプトではなく、実際にアーティストが繰り返し使用することを想定したツール設計を目標としました。

---

## Future Improvements

今後の拡張候補：

- Custom Naming Preset
- ユーザー定義Prefix
- 対応Object Typeの追加
- Batch Validation
- Validation Reportの出力
- Blender Add-on化
- 3ds Max版の制作
