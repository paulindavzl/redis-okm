from __future__ import annotations

from .. import settings
from ..core.connection import RedisConnect
from ..exceptions import *



class RedisModel:
    """
    Base para todos os modelos em RedisOKM
    """
    __slots__ = ["__db__", "__instancied__", "__idname__", "__tablename__", "__autoid__", "__testing__", "__hashid__", "__settings__", "__expire__", "__fk__", "__fks__", "to_dict"]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__instancied__ = False
        cls.__slots__ = set(getattr(cls, "__slots__", []) + RedisModel.__slots__)

    def __init__(self, **attributes):
        """
        Cria uma instância de um modelo que usa **RedisModel**

        Params:

            **attributes - atributos/informações declaradas na estrutura do modelo.
        
        Examples:

            class UserModel(RedisModel):
                ...
                # attributes
                name: str
                age: int
            
            user = UserModel(name="example_user", age=18)

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """

        # obtém informações do modelo
        db = getattr(self, "__db__", None)
        idname = getattr(self, "__idname__", None)
        autoid = getattr(self, "__autoid__", True)
        hashid = getattr(self, "__hashid__", True)
        testing = getattr(self, "__testing__", False)
        tablename = getattr(self, "__tablename__", None)
        sett = getattr(self, "__settings__", settings)
        expire = getattr(self, "__expire__", None)
        fk = getattr(self, "__fk__", {})

        if db is None:
            raise RedisModelDBException("Specify the database using __db__ when structuring the model")
        elif isinstance(db, str):
            db = sett.get_db(db)
        if not idname:
            for attr in self.__annotations__:
                if not attr.startswith("__"):
                    idname = attr
                    break
        if not tablename:
            tablename = type(self).__name__.lower()
            
        # repassa a informações para o modelo (exceção de __db__ que é obrigatório)
        self.__db__ = db
        self.__settings__ = sett
        self.__tablename__ = tablename
        self.__testing__ = testing
        self.__autoid__ = autoid
        self.__hashid__ = hashid
        self.__idname__ = idname
        self.__expire__ = expire
        self.__fk__ = fk # salva as informações para chaves estrangeiras
        self.__fk_models__ = {} # salva o modelo e o ID
        self.__callable__ = []
        self.__fks__ = []

        # verifica se é para instanciar por completo a classe (usado por RedisConnect)
        if attributes.get("instance") != False:
            attrs = {} # atributos que serão passados ao modelo
            dirs = self.__dir__()
            ann = self.__annotations__

            for d in dirs:
                if not d.startswith("__") and not d in self.__slots__ and callable(getattr(self, d)):
                    self.__callable__.append(d)
                    ann[d] = getattr(self, d)

            set_id = attributes.pop("set_id") if attributes.get("set_id") else False
            # tipa todos os atributos passados ao modelo
            for attr, value in attributes.items():
                if attr in self.__slots__ and attr != "__fks__":
                    raise RedisModelAttributeException(f'"{attr}" is an internal attribute and cannot be set')
                elif attr not in ann and attr not in self.__callable__:
                    raise RedisModelAttributeException(f'{type(self).__name__} does not have "{attr}" attribute!')
                
                if attr in self.__callable__:
                    continue

                typ: type = ann[attr]
                if typ.__base__ == RedisModel:
                    _idname = typ(instance=False).__idname__
                    f = {_idname: value}

                    model = RedisConnect.get(typ).filter_by(**f)
                    if not model:
                        raise RedisModelForeignKeyException(f"The foreign key ({typ.__name__} {_idname}:{value}) has no record.")
                    def fk_return():
                        return model
                    
                    self.__fk_models__[attr] = {"model": typ, "id": value}
                    
                    setattr(self, attr, fk_return)
                else:
                    try:
                        count_db: None
                        attrs[attr] = typ(value)
                    except ValueError:
                        received = value if value else count_db
                        raise RedisModelTypeValueException(f"{attr} expected a possible {typ.__name__} value, but received a {type(received).__name__} ({received}) value!")

            if autoid and set_id != True:
                attrs[idname] = RedisConnect.get # ID será gerado somente na hora de adicionar no banco de dados
                self.__callable__.append(idname)
                
            for attr, value in attrs.items():
                setattr(self, attr, value)

            self.to_dict = attrs # define to_dict

            for attr in ann:
                if not str(attr).startswith("__") and attr not in attrs and attr not in self.__fk_models__:
                    name = type(self)
                    if not hasattr(name, attr):
                        raise RedisModelNoValueException(f"{attr} must receive a value!")
                    value = getattr(name, attr)
                    if callable(value):
                        value = value()
                    setattr(self, attr, value)
                    self.to_dict[attr] = value

            if self.__fk_models__ or self.__fk__:
                if not self.__fk__:
                    raise RedisModelForeignKeyException("Define an action for foreign keys (__fk__ = {fk_name: action})")
                elif not isinstance(self.__fk__, dict):
                    raise RedisModelForeignKeyException(f"Foreign key actions must be dict. action: {fk} ({type(fk).__name__})")
                for fk in self.__fk_models__.keys():
                    if not self.__fk__.get(fk):
                        raise RedisModelForeignKeyException(f'Define an action for the foreign key "{fk}"' + ' (__fk__ = {"user": action}).')
                for fk in self.__fk__.keys():
                    if not self.__fk_models__.get(fk):
                        raise RedisModelForeignKeyException(f'"{fk}" cannot have an action because its foreign key has not been defined!')
            
            self.__instancied__ = True
        else:
            identify = attributes.get("identify")
            if identify:
                setattr(self, idname, identify)


     



# created by:


# █▀█ ▄▀█ █░█ █░░ █ █▄░█ █▀▄ ▄▀█ █░█ ▀█ █░░
# █▀▀ █▀█ █▄█ █▄▄ █ █░▀█ █▄▀ █▀█ ▀▄▀ █▄ █▄▄

# https://github.com/paulindavzl
#