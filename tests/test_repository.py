from uuid import UUID
from app.repositories.base import BaseRepository


class TestEntity:
    pass


class TestRepository(BaseRepository[TestEntity]):
    def create(self, entity: TestEntity):
        return entity

    def find(self, _id: UUID):
        return TestEntity()

    def find_all(self):
        return [TestEntity()]

    def update(self, entity: TestEntity):
        return entity

    def delete(self, _id: UUID):
        return TestEntity()


class TestRepositories:
    def test_abstract_repository(self):
        test_entity = TestEntity()
        test_repository = TestRepository()
        assert test_repository.create(test_entity) == test_entity
