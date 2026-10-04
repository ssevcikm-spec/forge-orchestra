extends Node

# Gather resources from a node.
# Returns the number of items gathered.
func gather(node: Node) -> int:
    # Expected node properties:
    # - "resource_id": String identifier of the material (e.g., "iron_ore", "wood", "stone")
    # - "difficulty": int difficulty of the material
    # - "cell": the cell position (passed to world.gather)

    var resource_id: String = ""
    var difficulty: int = 0
    var cell = null

    if node.has_method("get_resource_id"):
        resource_id = node.get_resource_id()
    elif node.has("resource_id"):
        resource_id = node.resource_id
    else:
        push_error("Mining.gd: node missing 'resource_id'")
        return 0

    if node.has_method("get_difficulty"):
        difficulty = node.get_difficulty()
    elif node.has("difficulty"):
        difficulty = node.difficulty
    else:
        push_error("Mining.gd: node missing 'difficulty'")
        return 0

    if node.has_method("get_cell"):
        cell = node.get_cell()
    elif node.has("cell"):
        cell = node.cell

    # Determine which skill to use.
    var skill_name: String = ""
    match resource_id:
        "iron_ore", "stone":
            skill_name = "tezba"
        "wood":
            skill_name = "drevorubectvi"
        _:
            # Default to mining skill if unknown.
            skill_name = "tezba"

    # Access the global skills singleton (assumed to be autoloaded as "Skills").
    var skills_node = get_node_or_null("/root/Skills")
    if skills_node == null:
        push_error("Mining.gd: Skills singleton not found")
        return 0

    var skill_value: int = skills_node.hodnota(skill_name)

    # Calculate yield.
    var yield_amount: int = int(max(0, 1 + (skill_value - difficulty) / 10))

    # Increase the skill by 1.
    skills_node.add(skill_name, 1)

    # Notify the world that the cell has been gathered.
    var world_node = get_node_or_null("/root/World")
    if world_node != null:
        world_node.gather(cell)

    return yield_amount
