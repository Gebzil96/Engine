def test_registry_import_and_create_entity():
    # Минимальный тест: проверяем, что Registry импортируется и создаёт entity.
    # Это не трогает окно/рендер и работает быстро.
    from engine.ecs.registry import Registry

    reg = Registry()
    eid = reg.create_entity()
    assert isinstance(eid, int)
