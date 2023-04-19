from dataclasses import asdict

from dependency_injector import containers, providers

from claon_admin.config.config import conf
from claon_admin.config.redis import Redis
from claon_admin.schema.conn import Database
from claon_admin.schema.user import UserRepository
from claon_admin.service.user import UserService

db = Database(db_url=asdict(conf())['DB_URL'])
redis = Redis(host=asdict(conf())['REDIS_HOST'], port=asdict(conf())['REDIS_PORT'])


class Container(containers.DeclarativeContainer):
    """ Repository """
    user_repository = providers.Factory(UserRepository)

    """ Service """
    user_service = providers.Factory(UserService, user_repository=user_repository)