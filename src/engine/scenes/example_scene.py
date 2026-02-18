def build_example_scene(player_texture, e2_texture) -> list[dict]:
    """
    Минимальный scene config: чистые данные (prefab-словарики),
    которые Scene потом превратит в ECS-сущности.
    """
    return [
        {
            "transform": {
                "pos_x": 0.0,
                "pos_y": 0.0,
                "rot": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0,
            },
            "renderable": {"z_index": 0},
            "sprite": {"texture_path": player_texture},
        },
        {
            "transform": {
                "pos_x": 300.0,
                "pos_y": 0.0,
                "rot": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0,
            },
            "renderable": {"z_index": 1},
            "sprite": {"texture_path": e2_texture},
        },
    ]
