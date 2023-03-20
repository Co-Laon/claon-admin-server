import pytest

from claon_admin.schema.example import Example, ExampleRepository

example_repository = ExampleRepository()


@pytest.fixture
async def example_fixture(session):
    example = await example_repository.save(session, Example(name='example'))
    yield example


@pytest.mark.asyncio
async def test_find_by_id(session, example_fixture):
    # given
    example_id = example_fixture.id

    # when
    result = await example_repository.find_by_id(session, example_id)

    # then
    assert result.id == example_id
    assert result.name == example_fixture.name
