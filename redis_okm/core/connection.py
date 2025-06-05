import time
import json
import redis
import hashlib
import fakeredis
from typing import Any

from ..core import _model
from .configure import Settings
from .getter import Getter
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
                raise RedisConnectionSettingsInstanceException(f"{model.__name__}: settings must be an instance of Settings! senttings_handler: {type(settings).__name__}")
            
            is_testing = getattr(model, "__testing__", False)
        else:
            db = kwargs.get("db")
            settings = kwargs.get("settings")

            if not isinstance(settings, Settings):
                raise RedisConnectionSettingsInstanceException(f"{f"{model.__name__}: " if use_model else ""}settings must be an instance of Settings! senttings_handler: {type(settings).__name__}")
            
            is_testing = getattr(settings, "testing", False)

            if isinstance(db, str):
                db = settings.get_db(db)
        
        retry = settings.retry_on_timeout
        tries = int(retry[1]) if isinstance(retry, list) else 1
        for attempts in range(tries):
            try:
                connection = settings.redis_info
                connection.update({"db": db})
                _redis = fakeredis.FakeRedis(**connection) if is_testing else redis.Redis(**connection)
                _redis.ping()
                return _redis
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                if attempts < tries - 1:
                    time.sleep(.5)
                    continue
                raise RedisConnectConnectionFailedException(f"{f"{model.__name__}: " if use_model else ""}Unable to connect to Redis database: {e.__str__()}")


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

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")

        """
        def _set_identify(algorithm):
            pos = RedisConnect.get(model, _set_fk=False).length
            identify = algorithm(str(pos).encode("utf-8")).hexdigest() if model.__hashid__ else pos

            setattr(model, idname, identify)
            model.to_dict[idname] = identify

        def _add(handler: redis.Redis, _settings: Settings, algorithm, set_id: bool=False):
            if RedisConnect.exists(model) and not exists_ok:
                if not set_id:
                    raise RedisConnectionAlreadyRegisteredException(f"{type(model).__name__}: This {idname} ({getattr(model, idname)}) already exists in the database!")
                else:
                    _set_identify(algorithm)

            name = RedisConnect._get_name(model)
            content: dict = model.to_dict
            fks: dict = model.__foreign_keys__
            if fks:
                model_name = type(model).__name__
                for key, value in fks.items():
                    id = value["id"]
                    fk_model = value["model"](instance=False, identify=id)
                    fk_settings: Settings = fk_model.__settings__

                    differences = [
                        "HOST" if fk_settings.host != _settings.host else "", 
                        "PORT" if fk_settings.port != _settings.port else "",
                        "PASSWORD" if fk_settings.password != _settings.password else ""
                    ] 
                    differences = [d for d in differences if d]
                    if differences:
                        raise RedisConnectForeignKeyException(f"{model_name}: The connection information (HOST, PORT and PASSWORD) of the reference model ({type(fk_model).__name__}) and the referenced model ({model_name}) must be the same. Differences: {", ".join(differences)}")
                    
                    fk_name = RedisConnect._get_name(fk_model)
                    fk_handler = RedisConnect._connect(fk_model)
                    fk_db = fk_model.__db__
                    fk_testing = fk_model.__testing__
                    fk_tablename__ = fk_model.__tablename__


                    fk_data = fk_handler.hgetall(fk_name)
                    eid = id if isinstance(id, int) else f'"{id}"'
                    if not fk_data:
                        raise RedisConnectForeignKeyException(f'{type(model).__name__}: Foreign key "{key}" ({value["model"].__name__}) with ID {eid} has no record!')

                    referenced = fk_data.get("__referenced__")
                    referenced = json.loads(referenced) if referenced else {}
                    
                    referenced[fk_tablename__] = {"key": key, "name": name, "action": model.__action__[key], "db": fk_db, "testing": fk_testing, "model": model_name, "idname": model.__idname__, "id": getattr(model, model.__idname__)}

                    referenced = json.dumps(referenced)
                    fk_data["__referenced__"] = referenced
                    
                    fk_handler.hset(fk_name, mapping=fk_data)

                    content[key] = id

            for key, value in content.items():
                if isinstance(value, (dict, list, tuple)):
                    typ: type = model.__annotations__[key]
                    if typ != type(value):
                        raise RedisConnectTypeValueException(f'{type(model).__name__}: Divergence in the type of the attribute "{key}". expected: "{typ.__name__}" - received: "{type(value).__name__}"')
                    
                    content[key] = json.dumps(value)

            content = {k: str(v) for k, v in content.items()}
            setattr(model, "__key__", hashlib.sha256(
                str(model.__idname__).encode("utf-8")
                +str(model.__tablename__).encode("utf-8")
                +str(model.__db__).encode("utf-8")
                +str(getattr(model, model.__idname__)).encode("utf-8")
            ).hexdigest())
            data = str(model.__key__).encode("utf-8") + str(json.dumps(content)).encode("utf-8")
            hs = hashlib.sha256(data).hexdigest()
            content["__hash__"] = hs

            for attr, value in content.items():
                if callable(value):
                    callable_value = value()
                    setattr(model, attr, callable_value)
                    content[attr] = callable_value
                                            
            handler.hset(name, mapping=content)

        if not model.__instancied__:
            raise RedisConnectionModelInstanceException(f"{model.__name__}: The model must be instantiated to be added to the database!")

        idname = model.__idname__
        set_id = model.__autoid__ is True and getattr(model, idname) == "__await_autoid__"
        settings: Settings = model.__settings__
        algorithm = getattr(hashlib, settings.hash_algorithm)

        if set_id:
            _set_identify(algorithm)

        redis_handler = RedisConnect._connect(model)
        _add(redis_handler, settings, algorithm, set_id)

        # verifica se tem expiração
        expire = getattr(model, "__expire__")
        if expire:
            try:
                name = RedisConnect._get_name(model)
                expire = float(expire)
                redis_handler.expire(name, expire)
            except ValueError:
                raise RedisConnectInvalidExpireException(f'{type(model).__name__}: expire must be convertible to float! expire: "{expire}"')


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
        
        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """
        if not model.__instancied__ and identify is None:
            raise RedisConnectNoIdentifierException(f"{model.__name__}: Use an instance of the model or provide an identifier.")

        if model.__instancied__ and identify is None:
            identify = getattr(model, model.__idname__)

        if callable(model):
            model = model(instance=False, identify=identify)

        redis_handler = RedisConnect._connect(model)
        name = RedisConnect._get_name(model)
        return redis_handler.exists(name) == 1
    

    @staticmethod
    def get(model: _model, on_corrupt="flag", _set_fk: bool=True) -> Getter:
        """
        Obtém dados do banco de dados baseado em modelos

        Params:

            model - modelo que usa RedisModel
            _set_fk (bool) - indica se é necessário definir chave estrangeira (uso interno)

        Examples:

            class UserModel(RedisModel):
                ...

            
            models = RedisConnect.get(UserModel) # o retorno pode ser None, uma instância do modelo ou Getter (grupo de modelos)

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """

        if callable(model):
            model = RedisConnect._get_instance(model)

        if on_corrupt not in ["skip", "flag", "ignore"]:
            raise RedisConnectGetOnCorruptException(f'on_corrupt must be "flag", "skip" or "ignore"! on_corrupt: "{on_corrupt}"')
        
        pattern = RedisConnect._get_name(model, True)

        redis_handler = RedisConnect._connect(model)
        getters = []
        for name in redis_handler.scan_iter(pattern):
            resp = redis_handler.hgetall(name)
            
            __hash__ = resp.pop("__hash__", "error")
            content = resp
            resp.pop("__referenced__", None)

            for key, value in resp.items():
                typ: type = model.__annotations__[key]
                if typ in [list, dict, tuple]:
                    try:
                        value = value.decode("utf-8") if isinstance(value, bytes) else value
                        resp[key] = json.loads(value)
                    except json.JSONDecodeError:
                        resp[key] = "corrupted"

            new_model = model.__class__(set_fk=_set_fk, **resp)
            
            setattr(new_model, "__key__", hashlib.sha256(
                str(new_model.__idname__).encode("utf-8")
                +str(new_model.__tablename__).encode("utf-8")
                +str(new_model.__db__).encode("utf-8")
                +str(getattr(new_model, new_model.__idname__)).encode("utf-8")
            ).hexdigest())

            data = str(new_model.__key__).encode("utf-8")+str(json.dumps(content)).encode("utf-8")
            hs = hashlib.sha256(
                data
            ).hexdigest()

            if hs != __hash__:
                if on_corrupt == "flag":
                    new_model.__status__ = False
                    for attr in new_model.__annotations__:
                        if attr not in [new_model.__idname__, "__idname__"]:
                            setattr(new_model, attr, "corrupted")
                elif on_corrupt == "skip":
                    continue
            getters.append(new_model)

        return Getter(getters)
    

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
        
        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """
        if not model.__instancied__ and identify is None:
            raise RedisConnectNoIdentifierException(f"{model.__name__}: Use an instance of the model or provide an identifier.")

        if model.__instancied__ and identify is None:
            identify = getattr(model, model.__idname__)
            model = model.__class__
        
        def _delete(delete_model: _model):
            if not non_existent_ok and not RedisConnect.exists(delete_model):
                idname = delete_model.__idname__
                raise RedisConnectNoRecordsException(f"{type(model).__name__}: This {idname} ({getattr(delete_model, idname)}) does not exist in the database!")

            name = RedisConnect._get_name(delete_model)
            redis_handler = RedisConnect._connect(delete_model)

            referenced = redis_handler.hget(name, "__referenced__")
            if referenced:
                fk_connection = delete_model.__settings__.redis_info
                try:
                    referenced: dict = json.loads(referenced)

                    for value in referenced.values():
                        fk_key = value["key"]
                        fk_name = value["name"]
                        fk_action = value["action"]
                        fk_testing = value["testing"]
                        fk_model = value["model"]
                        fk_idname = value["idname"]
                        fk_id = value["id"]

                        fk_connection.update({"db": value["db"]})
                        fk_handler = fakeredis.FakeRedis(**fk_connection) if fk_testing else redis.Redis(**fk_connection)

                        if fk_handler.exists(fk_name) == 1:
                            if fk_action == "restrict":
                                raise RedisConnectForeignKeyException(f"{type(delete_model).__name__}: It was not possible to delete the model because it is a reference to another record ({fk_model} - {fk_idname}: {fk_id} - {fk_key})!")
                            elif fk_action == "cascade":
                                fk_handler.delete(fk_name)
                            else:
                                raise RedisConnectForeignKeyException(f"{fk_model}: Foreign key action is invalid ({fk_key}: {fk_action} - {fk_idname}: {fk_id})!")
                except json.JSONDecodeError:
                    raise RedisConnectForeignKeyException(f"{fk_model}: Failed to decode __referenced__ field. Data might be corrupted.")
                
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
    def count(db: int|str, settings: Settings, testing: bool=False) -> int:
        """
        Retorna a quantidade de registros de um banco de dados completo, sejam eles do mesmo modelo ou não

        Params:

            db (int|str) - índice do banco de dados
            settings (Settings) - configurações para a conexão
            testing (bool) - informa se é um teste

        Examples:
            
            count = RedisConnect.count(db="tests", settings=settings)

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """
        if isinstance(db, str):
            if not isinstance(settings, Settings):
                raise RedisConnectionSettingsInstanceException("For a named db enter an instance of Settings!")
            db = settings.get_db(db)
        
        redis_handler = RedisConnect._connect(use_model=False, settings=settings, db=db, testing=testing)
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

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """

        def restart(index):
            redis_handler = RedisConnect._connect(use_model=False, db=index, settings=settings)
            redis_handler.flushall()
        
        if db == "__all__":
            for i in range(16):
                try:
                    restart(i)
                except:
                    pass
        else:
            if isinstance(db, list):
                for i in db:
                    restart(i)
            else:
                restart(db)



"""
created by:


▄▀█ █▀ ▀█▀ █░█ ▀█▀ █▀█
█▀█ ▄█ ░█░ █▄█ ░█░ █▄█

https://github.com/paulindavzl/redis-okm
"""