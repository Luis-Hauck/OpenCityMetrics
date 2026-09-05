import pytest
from repositories.in_memory_repository import InMemoryRepository
from repositories.base_repository import ItemNotFoundError

@pytest.fixture
def repository():
    return InMemoryRepository()

def test_create_item(repository):
    item_data = {"name": "Test Item", "value": 10}
    created_item = repository.create(item_data)

    assert "id" in created_item
    assert created_item["name"] == "Test Item"
    assert created_item["value"] == 10
    assert created_item["id"] == 1

def test_get_item(repository):
    item_data = {"name": "Test Item"}
    created_item = repository.create(item_data)

    item = repository.get(created_item["id"])
    assert item["name"] == "Test Item"

def test_get_nonexistent_item(repository):
    with pytest.raises(ItemNotFoundError):
        repository.get(999)

def test_get_all_items(repository):
    repository.create({"name": "Item 1"})
    repository.create({"name": "Item 2"})

    items = repository.get_all()
    assert len(items) == 2
    assert items[0]["name"] == "Item 1"
    assert items[1]["name"] == "Item 2"

def test_update_item(repository):
    item_data = {"name": "Test Item", "value": 10}
    created_item = repository.create(item_data)

    item_id = created_item["id"]
    updated_data = {"name": "Updated Item"}
    updated_item = repository.update(item_id, updated_data)

    assert updated_item["id"] == item_id
    assert updated_item["name"] == "Updated Item"
    assert updated_item["value"] == 10

def test_update_nonexistent_item(repository):
    with pytest.raises(ItemNotFoundError):
        repository.update(999, {"name": "Does not exist"})

def test_delete_item(repository):
    item_data = {"name": "Test Item"}
    created_item = repository.create(item_data)
    item_id = created_item["id"]

    result = repository.delete(item_id)
    assert result is True

    with pytest.raises(ItemNotFoundError):
        repository.get(item_id)

def test_delete_nonexistent_item(repository):
    with pytest.raises(ItemNotFoundError):
        repository.delete(999)
