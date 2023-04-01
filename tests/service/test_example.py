import uuid

from unittest.mock import AsyncMock

import pytest

from claon_admin.schema.example import Example, ExampleRepository, ExampleProperty
from claon_admin.service.example import ExampleService


@pytest.fixture
def example_fixture():
    example = Example(id=str(uuid.uuid4()), name='example', prop=ExampleProperty(name='prop', description='desc'))
    return example


async def test_example_find_by_id(session, example_fixture):
    # given
    mock_example_repo = AsyncMock(spec=ExampleRepository)
    mock_example_repo.find_by_id.side_effect = [example_fixture]

    # when
    example_service = ExampleService(mock_example_repo)
    result = await example_service.find_by_id(session, example_fixture.id)

    # then
    assert result.id == example_fixture.id
    assert result.name == example_fixture.name


async def test_example_save(session, example_fixture):
    # given
    mock_example_repo = AsyncMock(spec=ExampleRepository)
    mock_example_repo.save.side_effect = [example_fixture]

    # when
    example_service = ExampleService(mock_example_repo)
    result = await example_service.save(session, example_fixture)

    # then
    assert result.id == example_fixture.id
    assert result.name == example_fixture.name
