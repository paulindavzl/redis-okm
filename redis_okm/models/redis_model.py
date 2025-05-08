from .. import settings
from ..core.connection import RedisConnect
from ..exceptions import *



class RedisModel:
    """
    Base para todos os modelos em RedisOKM
    """
    __slots__ = ["__db__", "__instancied__", "__idname__", "__tablename__", "__autoid__", "__testing__", "__hashid__", "__settings__", "__expire__", "to_dict"]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__instancied__ = False
        cls.__slots__ = getattr(cls, "__slots__", []) + RedisModel.__slots__

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

        if not attributes.get("instance") is False:
            attrs = {}
            ann = self.__annotations__

            # passa as informações para o modelo caso ele aceite-as
            for attr, value in attributes.items():
                if attr not in ann:
                    raise RedisModelAttributeException(f'{type(self).__name__} does not have "{attr}" attribute!')          
                      
                typ: type = ann[attr]
                try:
                    count_db: None
                    attrs[attr] = typ(value)
                except ValueError:
                    received = value if value else count_db
                    raise RedisModelTypeValueException(f"{attr} expected a possible {typ.__name__} value, but received a {type(received).__name__} ({received}) value!")

            if autoid:
                attrs[idname] = RedisConnect.get # ID será gerado somente na hora de adicionar no banco de dados
            for attr, value in attrs.items():
                setattr(self, attr, value)

            self.to_dict = attrs # define to_dict

            for attr in ann:
                if not str(attr).startswith("__") and attr not in attrs:
                    name = type(self)
                    if not hasattr(name, attr):
                        raise RedisModelNoValueException(f"{attr} must receive a value!")
                    value = getattr(name, attr)
                    if callable(value):
                        value = value()
                    setattr(self, attr, value)
                    self.to_dict[attr] = value
            
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