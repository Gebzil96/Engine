from src.engine.ecs.components.transform import Transform
from src.engine.ecs.components.renderable import Renderable


class Scene:
    def __init__(self, registry):
        self.registry = registry
        self.entities: list[int] = []

    def spawn_example(self):
        # Player
        player = self.registry.create_entity()
        self.entities.append(player)

        self.registry.add(
            player,
            Transform(
                pos_x=0.0,
                pos_y=0.0,
                rot=0.0,
                scale_x=1.0,
                scale_y=1.0,
            ),
        )
        self.registry.add(player, Renderable(z_index=0))

        # Static quad
        e2 = self.registry.create_entity()
        self.entities.append(e2)

        self.registry.add(
            e2,
            Transform(
                pos_x=300.0,
                pos_y=0.0,
                rot=0.0,
                scale_x=1.0,
                scale_y=1.0,
            ),
        )
        self.registry.add(e2, Renderable(z_index=1))

        return player, e2
