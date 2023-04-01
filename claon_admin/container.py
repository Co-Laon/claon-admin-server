from dataclasses import asdict

from dependency_injector import containers, providers

from claon_admin.config.config import conf
from claon_admin.schema.conn import Database
from claon_admin.schema.example import ExampleRepository
from claon_admin.service.example import ExampleService

db = Database(db_url=asdict(conf())['DB_URL'])


class Container(containers.DeclarativeContainer):
    """ Repository """
    example_repository = providers.Factory(ExampleRepository)

    """ Service """
    example_service = providers.Factory(ExampleService,
                                        example_repository=example_repository)
    