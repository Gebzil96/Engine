from collections.abc import Callable


SceneBuilder = Callable[[], list[dict]]


def get_scene_builder(scene_id: str) -> SceneBuilder:
    """
    Минимальный loader: по строковому id возвращает функцию-сборщик сцены.
    Позже тут можно сделать автопоиск/пакеты/JSON, но сейчас — просто реестр.
    """
    if scene_id == "example_scene":
        from src.engine.scenes.example_scene import build_example_scene
        return build_example_scene

    raise ValueError(f"Unknown scene_id: {scene_id!r}")
