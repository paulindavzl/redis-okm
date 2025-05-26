# Exceptions

O **RedisOKM** possui várias exceções personalizadas para facilitar o **Debug** dos projetos. Cada `classe/módulo` possui suas próprias exceções, permitindo assim, localizar com precisão onde os erros ocorreram.

## RedisModel

Estas são as exceções levantadas por **[RedisModel](./redis-model.md)**:

### RedisModelAttributeException

Este erro pode acontecer de três formas:

- Quando o usuário não define um banco de dados ao estruturar um **[modelo](./redis-model.md#o-que-é-um-modelo)** (`__db__`):

    ```sh
    # exemplo de erro
    RedisModelAttributeException: 'Model: Specify the database using __db__ when structuring the model'
    ```

    Para evitá-la, adicione `__db__` na estrutura do **[modelo](./redis-model.md#o-que-é-um-modelo)**:

    ```python
    class Model(RedisModel):
        __db__ = "dbname" # ou índice (0, 1, ..., 15)
        ...
    ```

- Quando o usuário tenta acessar/definir um atributo que não existe no **[modelo](./redis-model.md#o-que-é-um-modelo)**:

    ```sh
    # exemplo de erro
    RedisModelAttributeException: 'Model does not have "invalid" attribute!'
    ```

    Basta garantir que o atributo exista antes de tentar manipulá-lo:

    ```python
    class Model(RedisModel):
        ...

        id: int
        name: str


    model = Model(
        name = "example",
        invalid="error" # gerará erro (invalid não é um atributo de Model)
    )
    ```

-  Quando o usuário tenta definir um **"atributo especial"** (iniciados com **dunder** - **__**). Isso ocorre para que não haja conflitos na atribuição de valores aos atributos:

    ```sh
    # exemplo de erro
    RedisModelAttributeException: 'Model: Cannot set attributes that start and end with "__" (__attribute__)!'
    ```

    Para que este erro não ocorra, não tente definir atributos nomeados com **dunder** (__):

    ```python
    class Model(RedisModel):
        ...

        id: int
        name: str


    model = Model(
        name = "example",
        __error__ = "error" # não pode iniciar-se com dunder
    )
    ```

    > ⚠️ **Atenção:** Este erro em específico (por este motivo) não costuma acontecer, já que antes geraria o erro: `RedisModelAttributeException: Model does not have "invalid" attribute!`

-  Quando o usuário define `__action__` com um valor que não é um dicionário (dict):

    ```sh
    # exemplo de erro
    RedisModelAttributeException: 'Model: __action__ must be dict. __action__: error (str)'
    ```

    Sempre que for definir `__action__`, use dicionário:

    ```python
    class Model(RedisModel):
        __action__ = {"fk": "cascade"}
        __action__ = "error" # gerará erro (qualquer tipo diferente de dict)
        ...
    ```

    > ⚠️ **Atenção**: `__action__` só deve ser definido em caso de uso de **[chaves estrangeiras](./redis-model.md#chave-estrangeira)**!

### RedisModelInvalidNomenclatureException

Este erro ocorre quando o usuário tenta definir um atributo iniciado e finalizado com **dunder** (__) na estrutura do **[modelo](./redis-model.md#o-que-é-um-modelo)** e que já não seja esperado:

```sh
# exemplo de erro
RedisModelInvalidNomenclatureException: 'Model: Cannot set attributes that start and end with "__" (__invalid__)!'
```

Este erro pode ser evitado com o usuário não tentando criar atributos para o **[modelo](./redis-model.md#o-que-é-um-modelo)** usando **dunder** (__):

```python
class Model(RedisModel):
    # atributos especiais permitidos
    __db__ = None 
	__idname__ = None 
	__autoid__ = True 
	__hashid__ = False 
	__settings__ = settings 
	__action__ = None
	__expire__ = None
	__tablename__ = None

    __invalid__ = "error" # gerará erro

    ...
```

> 🔔 **Note:** Neste caso, todos os atributos de **__db__** até **__tablename__** foram permitidos porque já fazem parte do modelo por padrão, já **__invalid__** seria um atributo novo, que poderia gerar conflitos! Veja mais sobre a **[estrutura padrão de um modelo](./redis-model.md#estrutura-básica-de-um-modelo)**.


### RedisModelForeignKeyException

Este erro está relacionado à qualquer problema relacionado à **[chaves estrangeiras](./redis-model.md#chave-estrangeira)** quando um **[modelo](./redis-model.md#o-que-é-um-modelo)** é instanciado. Ele pode ocorrer das seguintes formas:

-  Quando o usuário tenta definir uma chave estrangeira onde o modelo referencia a si mesmo:

    ```sh
    # exemplo de erro
    RedisModelForeignKeyException: 'Model: You cannot define a foreign key in a model of itself (fk2)!'
    ```

    Não tente referenciar uma **[chaves estrangeiras](./redis-model.md#chave-estrangeira)** no seu próprio **[modelo](./redis-model.md#o-que-é-um-modelo)** para que este erro não ocorra:

    ```python
    class OtherModel(RedisModel):
        ...


    class Model(RedisModel):
        ...

        id: int
        fk1: OtherModel
        fk2: Model # gerará um erro
    ```

-  Quando os **[modelos](./redis-model.md#o-que-é-um-modelo)** não possuem as mesma informações de conexão com o servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**:

    ```python
    from redis_okm.tools import Settings


    settings1 = Settings(path="settings1.json")
    settings1.set_config(host="...", port=..., password="...") # servidor, porta e senhas diferentes

    settings2 = Settings(path="settings2.json")
    settings2.set_config(host="...", port=..., password="...") # servidor, porta e senhas diferentes


    class OtherModel(RedisModel):
        __settings__ = settings1
        ...


    class Model(RedisModel):
        __settings__ = settings2
        ...

        fk: OtherModel
    ```

    ```sh
    # exemplo de erro
    RedisModelForeignKeyException: 'The connection information (HOST, PORT and PASSWORD) of the reference model (OtherModel) and the referenced model (Model) must be the same. Differences: HOST, PORT, PASSWORD'
    ```

    Certifique-se de os modelos referenciados e os que referenciam-os possuam as mesmas informações de conexão, de preferenciam, que usem a mesma instância em `__settings__`:

    ```python
    from redis_okm.tools import settings # o RedisOKM já possui uma instância global de Settings


    class OtherModel(RedisModel):
        __settings__ = settings
        ...


    class Model(RedisModel):
        __settings__ = settings
        ...

        fk: OtherModel
    ```

    > 💡 **Sugestão:** Sempre que possível, use a instância global de **[Settings](./settings.md)** e não defina-a na **[estrutura do modelo](./redis-model.md#estrutura-básica-de-um-modelo)**, **[RedisModel](./redis-model.md)** já lida com ela por padrão!

-  Quando o usuário tenta definir `__action__` sem definir uma **[chave estrangeira](./redis-model.md#chave-estrangeira)**:

    ```sh
    # exemplo de erro
    RedisModelForeignKeyException: 'Model: Define foreign key "fk" to define an action!'
    ```

    Sempre definir `__action__`, defina também a **[chave estrangeira](./redis-model.md#chave-estrangeira)**:

    ```python
    class OtherModel(RedisModel):
        ...


    class Model(RedisModel):
        ...
        __action__ = {"fk": "cascade"} # pode ser "restrict" no lugar de "cascade"

        id: int
        fk: OtherModel # se não definir a chave estrangeira, gera um erro
    ```

    >  ⚠️ **Atenção:** Para ser considerado **[chave estrangeira](./redis-model.md#chave-estrangeira)**, a chave referenciada deve ser um **[modelo](./redis-model.md#o-que-é-um-modelo)** com base em **[RedisModel](./redis-model.md)**!

-  Quando o usuário instancia um **[modelo](./redis-model.md#o-que-é-um-modelo) mas não atribui nenhum valor para a **[chave estrangeira](./redis-model.md#chave-estrangeira)**:

    ```sh
    # exemplo de erro
    RedisModelForeignKeyException: 'Model: Set a value for the foreign key "fk".'
    ```

    Sempre atribua valor para os atributos de um **[modelo](./redis-model.md#o-que-é-um-modelo)**, a menos que ele possua um valor padrão:

    ```python
    class OtherModel(RedisModel):
        ...


    class Model(RedisModel):
        ...
        __action__ = {"fk": "cascade"} # pode ser "restrict" no lugar de "cascade"

        id: int
        name: str
        fk: OtherModel

    model = Model(
        name="example",
        fk=0 # caso não atribua valor para a chave estrangeira, um erro será gerado
    )
    ```

-  Quando o usuário informa o ID de uma **[chave estrangeira](./redis-model.md#chave-estrangeira)** que não possui registro:

    ```sh
    # exemplo de erro
    RedisModelForeignKeyException: 'Model: There is no record for foreign key "fk" (OtherModel) with ID 0!'
    ```

    Garanta que a **[chave estrangeira](./redis-model.md#chave-estrangeira)** esteja **[registrada](./redis-connect.md#salvar-um-registro)** antes de atribuí-la a um **[modelo](./redis-model.md#o-que-é-um-modelo)**:

    ```python
    from redis_okm.tools import RedisModel, RedisConnect


    class OtherModel(RedisModel):
        ...


    class Model(RedisModel):
        ...
        __action__ = {"fk": "cascade"} # pode ser "restrict" no lugar de "cascade"

        id: int
        name: str
        fk: OtherModel


    other_model = OtherModel(...)
    RedisConnect.add(other_model) # adiciona o modelo referenciado (chave estrangeira) no banco de dados


    model = Model(
        name="example",
        fk=0 # garanta que ID esteja registrado para que não ocorra erro
    )
    ```

-  Quando o usuário define uma chave estrangeira mas não a adiciona em `__action__`:

    ```sh
    # exemplo de erro
    RedisModelForeignKeyException: 'Model: To define the foreign key "fk", add an action for it in __action__'
    ```

    Sempre que definir uma chave estrangeira, adicione-a em `__action__` também:

    ```python
    class OtherModel(RedisModel):
        ...


    class Model(RedisModel):
        ...
        __action__ = {"fk": "cascade"} # se não adiciona uma ação para a chave estrangeira, um erro ocorrerá

        id: int
        fk: OtherModel
    ```

    > 🔔 **Saiba:** As ações podem ser **"cascade"** ou **"restrict"**!

### RedisModelTypeValueException

Este erro ocorre quando um atributo recebe um valor com um tipo inesperado. Ele pode ocorrer nas seguintes situações:

-  Quando o usuário define o **ID** com um tipo que não seja `int` ou `str`:

    ```sh
    # exemplo de erro
    RedisModelTypeValueException: 'Model: The id must be of type int (integer) or str (string). id: list'
    ```

    O ID de um **[modelo](./redis-model.md#o-que-é-um-modelo)** sempre deve ser `int` ou `str`:

    ```python
    class Model(RedisModel):
        ...

        id: int|str
        id: list # gera erro
        ...
    ```

-  Quando o usuário define um tipo `list`, `dict` ou `tuple`, mas ao atribuir um valor, informa um tipo diferente:

    ```sh
    # exemplo de erro
    RedisModelTypeValueException: 'Model: Divergence in the type of the attribute "wishes". expected: "list" - received: "dict"'
    ```

    Sempre informe o valor com tipo definido na estrutura do **[modelo](./redis-model.md#o-que-é-um-modelo)**:

    ```python
    class Model(RedisModel):
        ...

        id: int
        wishes: list


    model = Model(
        wishes=[...],
        wishes={...} # gerará erro
    )
    ```

    > `int` e `str` não possuem tanta restrição, desde que possam ser convertidos para o tipo esperado. Porém, `dict`, `list` e `tuple` aceitam somente o tipo que lhes foi definido!

-  Quando um atributo espera um tipo e recebe um valor que não pode ser convertido (geralmente `float` e `int`):

    ```sh
    # exemplo de erro
    RedisModelTypeValueException: 'Model: price expected a possible float value, but received a str (inconvertible) value!'
    ```

    Em caso de atributos que esperam `int` ou `float`, garanta que o valor pode ser convertido:

    ```python
    class Model(RedisModel):
        ...

        id: int
        price: float


    model = Model(
        price = "2.5", # pode ser convertido
        price = "inconvertible" # gerará erro pois não pode ser convertido
    )
    ```
