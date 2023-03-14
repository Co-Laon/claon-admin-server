from dataclasses import asdict

from dependency_injector import containers, providers

from claon_admin.config.config import conf
from claon_admin.schema.conn import Database

db = Database(db_url=asdict(conf())['DB_URL'])


class Container(containers.DeclarativeContainer):
    """ Repository """

    """ Service """
