# Imports
import bpy
import re


# Naming / Collection Rules
PREFIX_RULES = {
    "MESH": "GEO_",
    "CAMERA": "CAM_",
    "LIGHT": "LGT_"
}

COLLECTION_RULES = {
    "MESH": "Geometry",
    "CAMERA": "Cameras",
    "LIGHT": "Lights"
}

# Scene Scan
def scan_scene():
    objects = []

    for obj in bpy.context.scene.objects:
        if obj.type in PREFIX_RULES:
            objects.append(obj)

    return objects


# Naming Validation
def has_blender_number_suffix(name):
    pattern = r"\.\d{3}$"

    return re.search(pattern, name) is not None


def validate_names(objects):
    problem_objects = []

    for obj in objects:
        prefix = PREFIX_RULES[obj.type]

        if not obj.name.startswith(prefix):
            problem_objects.append(obj)

        elif has_blender_number_suffix(obj.name):
            problem_objects.append(obj)

    return problem_objects


def get_naming_issues(objects):
    issues = []

    for obj in objects:
        prefix = PREFIX_RULES[obj.type]

        if not obj.name.startswith(prefix):
            issues.append((obj, "Missing Prefix"))

        elif has_blender_number_suffix(obj.name):
            issues.append((obj, "Blender Suffix"))

    return issues


# Rename
# 他のシーンも含めて名前の重複を避ける。
def get_next_numbered_name(base_name):
    index = 1

    while True:
        new_name = f"{base_name}_{index:02d}"

        if new_name not in bpy.data.objects:
            return new_name

        index += 1


def fix_names(problem_objects):
    for obj in problem_objects:
        old_name = obj.name
        prefix = PREFIX_RULES[obj.type]

        new_name = old_name

        if not new_name.startswith(prefix):
            new_name = prefix + new_name

        match = re.search(r"\.\d{3}$", new_name)

        if match:
            base_name = re.sub(r"\.\d{3}$", "", new_name)

            # 元の連番は引き継がず、空いている番号を使う。
            new_name = get_next_numbered_name(base_name)

        obj.name = new_name
        print(old_name, "->", new_name)


# Collection Organization
def organize_collections(objects, mode="LINK"):
    root_name = "DCC_Organizer"

    if root_name not in bpy.data.collections:
        root_collection = bpy.data.collections.new(root_name)
        bpy.context.scene.collection.children.link(root_collection)
    else:
        root_collection = bpy.data.collections[root_name]

    for obj in objects:
        collection_name = COLLECTION_RULES[obj.type]

        if collection_name not in bpy.data.collections:
            target_collection = bpy.data.collections.new(collection_name)
            root_collection.children.link(target_collection)

        else:
            target_collection = bpy.data.collections[collection_name]

            if target_collection.name not in root_collection.children:
                root_collection.children.link(target_collection)

        if mode == "MOVE":
            # リンク解除で一覧が変わるため、コピーを走査する。
            for collection in list(obj.users_collection):

                if collection != target_collection:
                    collection.objects.unlink(obj)

        if obj.name not in target_collection.objects:
            target_collection.objects.link(obj)

            print(obj.name, "->", root_name + "/" + collection_name)

        else:
            print(obj.name, "already in", root_name + "/" + collection_name)

    # 両モードでシーン直下の重複リンクを外し、階層をまとめる。
    for collection_name in COLLECTION_RULES.values():
        target_collection = bpy.data.collections.get(collection_name)

        if target_collection is None:
            continue

        if target_collection.name in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.unlink(target_collection)


# Scene Properties
def register_properties():
    bpy.types.Scene.dcc_collection_mode = bpy.props.EnumProperty(
        name="Collection Mode",
        description="Choose how objects are organized into collections",
        items=[
            (
                "LINK",
                "Add Link",
                "Keep existing collections and add another link"
            ),
            (
                "MOVE",
                "Move",
                "Remove existing collection links and move to DCC Organizer"
            ),
        ],
        default="LINK"
    )

    bpy.types.Scene.dcc_last_result = bpy.props.StringProperty(
        name="Last Result",
        default="No operation yet"
    )


def unregister_properties():
    del bpy.types.Scene.dcc_collection_mode


# Operators
class DCC_OT_ScanScene(bpy.types.Operator):
    bl_idname = "dcc.scan_scene"
    bl_label = "Scan Scene"
    bl_description = "Scan objects in the current scene"

    def execute(self, context):
        objects = scan_scene()

        print("=== Scene Scan ===")

        for obj in objects:
            print(obj.name, obj.type)

        return{'FINISHED'}


class DCC_OT_FixNames(bpy.types.Operator):
    bl_idname = "dcc.fix_names"
    bl_label = "Fix Names"
    bl_description = "Fix naming issues in the current scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = scan_scene()
        problem_objects = validate_names(objects)

        issue_count = len(problem_objects)

        print("=== Naming Issue ===")

        for obj in problem_objects:
            print(obj.name, obj.type)

        print("=== Fix Names ===")

        fix_names(problem_objects)

        if issue_count == 0:
            context.scene.dcc_last_result = "No naming issues found"

            self.report(
                {'INFO'},
                "No naming issues found"
            )

        else:
            context.scene.dcc_last_result = (
                f"Fixed {issue_count} naming issue(s)"
            )

            self.report(
                {'INFO'},
                f"Fixed {issue_count} naming issue(s)"
            )


        return {'FINISHED'}


class DCC_OT_OrganizeCollections(bpy.types.Operator):
    bl_idname = "dcc.organize_collections"
    bl_label = "Organize Collections"
    bl_description = "Organize objects into management collections"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        mode = context.scene.dcc_collection_mode

        if mode == "MOVE":
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)

    def execute(self, context):
        try:
            objects = scan_scene()

            if not objects:
                context.scene.dcc_last_result = "No supported objects found"
                self.report({'WARNING'}, "No supported objects found")
                return {'CANCELLED'}

            mode = context.scene.dcc_collection_mode

            print("=== Organize Collections ===")
            print("Mode:", mode)

            organize_collections(objects, mode)

            message = f"Organized {len(objects)} object(s)"

            context.scene.dcc_last_result = message

            self.report(
                {'INFO'},
                message
            )

            return {'FINISHED'}

        except Exception as error:
            message = f"Error: {error}"

            context.scene.dcc_last_result = message
            self.report({'ERROR'}, message)

            print("=== DCC Organizer Error ===")
            print(error)

            return {'CANCELLED'}


class DCC_OT_FixAll(bpy.types.Operator):
    bl_idname = "dcc.fix_all"
    bl_label = "Fix All"
    bl_description = "Fix naming issues and organize collections"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        mode = context.scene.dcc_collection_mode

        if mode == "MOVE":
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)

    def execute(self, context):
        try:
            objects = scan_scene()

            if not objects:
                context.scene.dcc_last_result = "No supported objects found"
                self.report({'WARNING'}, "No supported objects found")
                return {'CANCELLED'}

            problem_objects = validate_names(objects)

            issue_count = len(problem_objects)
            mode = context.scene.dcc_collection_mode

            print("=== Fix All Start")

            print("=== Fix Names ===")
            fix_names(problem_objects)

            print("=== Organize Collections ===")

            organize_collections(objects, mode)

            print("=== Fix All Complete ===")

            message = (
                f"Fixed {issue_count} naming issue(s)"
                f" and organized {len(objects)} object(s)"
            )

            context.scene.dcc_last_result = message
            self.report(
                {'INFO'},
                message
            )

            return {'FINISHED'}

        except Exception as error:
            message = f"Error: {error}"

            context.scene.dcc_last_result = message
            self.report({'ERROR'}, message)

            print("=== DCC Organizer Error ===")
            print(error)

            return {'CANCELLED'}


# UI
class DCC_PT_SceneOrganizer(bpy.types.Panel):
    bl_label = "DCC Scene Organizer"
    bl_idname = "DCC_PT_scene_organizer"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DCC Organizer"

    def draw(self, context):
        layout = self.layout

        stats = get_scene_stats()

        layout.label(
            text="Scene Status"
            )

        layout.label(
            text=f"Meshes: {stats['mesh']}"
        )

        layout.label(
            text=f"Cameras: {stats['camera']}"
        )

        layout.label(
            text=f"Lights: {stats['light']}"
        )

        layout.label(
            text=f"Naming Issues: {stats['issues']}"
        )

        if stats["issues"] > 0:
            box = layout.box()
            box.label(text="Problem Objects")

            for obj, reason in stats["naming_issues"]:
                row = box.row()

                row.label(text=obj.name, icon="ERROR")
                row.label(text=reason)

        else:
            box = layout.box()
            box.label(text="No naming issues found", icon="CHECKMARK")

        layout.separator()

        layout.operator("dcc.scan_scene")
        layout.operator("dcc.fix_names")

        layout.separator()

        layout.label(text="Collection Mode")

        layout.prop(
            context.scene,
            "dcc_collection_mode",
            expand=True
        )

        layout.operator("dcc.organize_collections")

        layout.separator()

        layout.operator("dcc.fix_all")

        layout.separator()

        box = layout.box()
        box.label(text="Last Result")

        box.label(
            text=context.scene.dcc_last_result,
            icon="CHECKMARK"
        )

# Scene Statistics
def get_scene_stats():
    objects = scan_scene()

    mesh_count = 0
    camera_count = 0
    light_count = 0

    for obj in objects:
        if obj.type == "MESH":
            mesh_count += 1

        elif obj.type == "CAMERA":
            camera_count += 1

        elif obj.type == "LIGHT":
            light_count += 1

    naming_issues = get_naming_issues(objects)

    return {
        "mesh": mesh_count,
        "camera": camera_count,
        "light": light_count,
        "issues": len(naming_issues),
        "naming_issues": naming_issues
    }


# Register / Unregister
classes = (
    DCC_OT_ScanScene,
    DCC_OT_FixNames,
    DCC_OT_OrganizeCollections,
    DCC_OT_FixAll,
    DCC_PT_SceneOrganizer,
)


# テキストエディターからの再実行に備えて登録を解除する。
def register():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    if hasattr(bpy.types.Scene, "dcc_collection_mode"):
        del bpy.types.Scene.dcc_collection_mode

    register_properties()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    if hasattr(bpy.types.Scene, "dcc_collection_mode"):
        del bpy.types.Scene.dcc_collection_mode

    if hasattr(bpy.types.Scene, "dcc_last_result"):
        del bpy.types.Scene.dcc_last_result

if __name__ == "__main__":
    register()
