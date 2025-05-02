import time
import redis
import hashlib
import fakeredis
from typing import Any

import redis.exceptions

from ..core import _model
from .configure import Settings
from ..models.getter_model import Getter
from ..exceptions.connection_exceptions import *


class RedisConnect:
    """
    Conecta e manipula operações com Redis
    """
    @staticmethod
    def _connect(model: _model=None, use_model: bool=True, **kwargs) -> redis.Redis:
        db: int|str
        settings: Settings
        is_testing: bool
        if use_model:
            db = model.__db__
            settings = model.__settings__

            if not isinstance(settings, Settings):
                raise RedisConnectionSettingsInstanceException(f"settings must be an instance of Settings! senttings_handler: {type(settings).__name__}")
            
            is_testing = getattr(model, "__testing__", False)
        else:
            db = kwargs.get("db")
            settings = kwargs.get("settings")

            if not isinstance(settings, Settings):
                raise RedisConnectionSettingsInstanceException(f"settings must be an instance of Settings! senttings_handler: {type(settings).__name__}")
            
            is_testing = getattr(settings, "testing", False)

            if isinstance(db, str):
                db = settings.get_db(db)
        
        retry = settings.retry_on_timeout
        tries = int(retry[1]) if isinstance(retry, list) else 1
        for attempts in range(tries):
            try:
                _redis = fakeredis.FakeRedis(db=db, **settings.redis_info) if is_testing else redis.Redis(db=db, **settings.redis_info)
                _redis.ping()
                return _redis
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                if attempts < tries - 1:
                    time.sleep(.5)
                    continue
                raise RedisConnectConnectionFailedException(f"Unable to connect to Redis database: {e.__str__()}")


    

    @staticmethod
    def _get_name(model: _model, pattern: bool=False) -> str:
        settings = model.__settings__
        name = (
            str(settings.prefix) 
            +str(settings.separator) 
            +str(model.__tablename__) 
            +str(settings.separator) 
            +str("*" if pattern else getattr(model, model.__idname__))
        )
        return name


    @staticmethod
    def add(model: _model, exists_ok: bool=False):
        """
        Adiciona um novo registro no banco de dados.

        Params:

            model - modelo que usa RedisModel (instanciado)

            exists_ok (bool) - quando True, atualiza o valor do registro, caso exista. Se False, gera um erro (ValueError) caso já exista um registro com aquele ID (padrão False)

        Examples:

            class UserModel(RedisModel):
            
                __idname__ = "id"
                ...

                
            user = UserModel(...)
            
            RedisConnect.add(model=user) # registra um modelo

            RedisConnect.add(model=user, exists_ok=True) # atualiza um registro

            RedisConnect.add(model=user) # gera um erro - "This id (0) already exists in the database!"

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-orm "GitHub RedisORM")

        """
        if not model.__instancied__:
            raise RedisConnectionModelInstanceException("The model must be instantiated to be added to the database!")

        idname = model.__idname__
        identify = getattr(model, idname)
        if callable(identify):
            identify = hashlib.md5(str(identify(model.__class__)).encode("utf-8")).hexdigest() if model.__hashid__ else identify(model.__class__)
            setattr(model, idname, identify)
            model.to_dict[idname] = identify
        name = RedisConnect._get_name(model)
 
        redis_handler = RedisConnect._connect(model)
        if RedisConnect.exists(model) and not exists_ok:
            raise RedisConnectionAlreadyRegisteredException(f"This {idname} ({identify}) already exists in the database!")
        redis_handler.hset(name, mapping=model.to_dict)


    @staticmethod
    def exists(model: _model, identify: Any=None) -> bool:
        """
        Verifica se um modelo já existe no banco de dados

        Params:

            model - modelo que usa RedisModel

            identify (Any) - identificador do registro que será verificado. Caso o modelo esteja instanciado, não é obrigatório (padrão None)

        Examples:

            class UserModel(RedisModel):
                ...

            user = UserModel(...)

            exists = RedisConnect.exists(model=user) # retorna True ou False

            exists = RedisConnect.exists(model=UserModel, identify=0) # retorna True ou False
        
        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-orm "GitHub RedisORM")
        """
        if not model.__instancied__ and identify is None:
            raise RedisConnectNoIdentifierException(f"Use an instance of the model ({model.__name__}) or provide an identifier.")

        if model.__instancied__ and identify is None:
            identify = getattr(model, model.__idname__)

        if callable(model):
            model = model(instance=False, identify=identify)

        redis_handler = RedisConnect._connect(model)
        name = RedisConnect._get_name(model)
        return redis_handler.exists(name) == 1
    

    @staticmethod
    def get(model: _model) -> None|_model|Getter:
        """
        Obtém dados do banco de dados baseado em modelos

        Params:

            model - modelo que usa RedisModel

        Examples:

            class UserModel(RedisModel):
                ...

            
            models = RedisConnect.get(UserModel) # o retorno pode ser None, uma instância do modelo ou Getter (grupo de modelos)

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-orm "GitHub RedisORM")
        """

        if callable(model):
            model = RedisConnect._get_instance(model)
        
        pattern = RedisConnect._get_name(model, True)

        redis_handler = RedisConnect._connect(model)
        getters = []
        for name in redis_handler.scan_iter(pattern):
            resp = redis_handler.hgetall(name)
            new_model = model.__class__(**resp)
            getters.append(new_model)

        if len(getters) == 1:
            return getters[0]
        elif len(getters) > 1:
            return Getter(getters)
        return None
    

    @staticmethod
    def delete(model: _model, identify: Any|list=None, non_existent_ok: bool=False):
        """
        Apaga um ou mais registro do banco de dados

        Params:

            model - modelo que usa RedisModel

            identify (Any|list) - identificador (es) do registro que será apagado. Caso o modelo esteja instanciado, não é obrigatório (padrão None)

            non_existent_ok (bool) - caso False, se identify não estiver relacionado a nenhum registro um erro é levantado (ValueError). Quando True, nada acontece se identify não existir (padrão False)

        Examples:

            class UserModel(RedisModel):
                ...

            
            user = UserModel(...)

            RedisConnect.delete(model=user) # apaga o registro do modelo (user - UserModel), levantando erro se não existir

            RedisConnect.delete(model=UserModel, identify=0) # apaga o registro do modelo com ID 0, se não existir levanta um ValueError - "This ID (0) does not exist in the database!"

            RedisConnect.delete(model=UserModel, identify=[0, 1, 2]) # apaga vários registros do modelo, levantando ValueError se não existir

            # note que o erro não seria levantado se o parâmetro non_existent_ok fosse True

            RedisConnect.delete(..., non_existent_ok=True)
        
        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-orm "GitHub RedisORM")
        """
        if not model.__instancied__ and identify is None:
            raise RedisConnectNoIdentifierException(f"Use an instance of the model ({model.__name__}) or provide an identifier.")

        if model.__instancied__ and identify is None:
            identify = getattr(model, model.__idname__)
            model = model.__class__
        
        def _delete(delete_model: _model):
            if not non_existent_ok and not RedisConnect.exists(delete_model):
                idname = delete_model.__idname__
                raise RedisConnectNoRecordsException(f"This {idname} ({getattr(delete_model, idname)}) does not exist in the database!")
            
            name = RedisConnect._get_name(delete_model)
            redis_handler = RedisConnect._connect(delete_model)
            redis_handler.delete(name)
        
        if isinstance(identify, list):
            for _id in identify:
                del_model = RedisConnect._get_instance(model if callable(model) else model.__class__)
                setattr(del_model, del_model.__idname__, _id)
                del_model.__instancied__ = True
                _delete(del_model)
        else:
            del_model = RedisConnect._get_instance(model if callable(model) else model.__class__)
            setattr(del_model, del_model.__idname__, identify)
            del_model.__instancied__ = True
            _delete(del_model)


    @staticmethod
    def count(model: _model) -> int:
        """
        Retorna a quantidade de registros de um banco de dados

        Params:

            model - modelo que usa RedisModel

        Examples:

            class UserModel(RedisModel):
                ...

            
            count = RedisConnect.count(UserModel)

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-orm "GitHub RedisORM")
        """
        if callable(model):
            model = RedisConnect._get_instance(model)
        redis_handler = RedisConnect._connect(model)
        count = redis_handler.dbsize()
        return count
    

    @staticmethod
    def _get_instance(model: _model) -> _model:
        if callable(model):
            return model(instance=False)
        return model
    

    @staticmethod
    def restart_full_db(db: Any|list, settings: Settings):
        """
        Apaga por completo todos os registros do banco de dados

        Params:

            db (any|list) - índice ou lista de índices dos bancos de dados que terão dados apagados. Pode ser índices nomeados

            settings (Settings) - instância de Settings

        Examples:

            settings = Settings()
            settings.set_config(dbname="example:10") # nomeia um banco de dados

            RedisConnect.restart_full_db(db="example", settings=settings) # apaga os dados do banco nomeado "example" (10)

            RedisConnect.restart_full_db(db=0, ...) # apaga os dados do banco 0

            RedisConnect.restart_full_db(db=[0, 1], ...) # apaga os dados dos bancos 0 e 1

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-orm "GitHub RedisORM")
        """
        
        if db == "__all__":
            for i in range(16):
                redis_handler = RedisConnect._connect(use_model=False, db=i, settings=settings)
                redis_handler.flushall()
        else:
            redis_handler = RedisConnect._connect(use_model=False, db=db, settings=settings)
            redis_handler.flushall()



"""
created by:


▄▀█ █▀ ▀█▀ █░█ ▀█▀ █▀█
█▀█ ▄█ ░█░ █▄█ ░█░ █▄█

https://github.com/paulindavzl/redis-orm
"""