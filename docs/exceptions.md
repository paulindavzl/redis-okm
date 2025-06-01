# Exceptions

O **RedisOKM** define diversas exceções personalizadas para facilitar o rastreamento e a depuração de erros durante o desenvolvimento. Cada módulo principal — como `RedisModel`, `RedisConnect`, `Settings` e `Getter` — possui suas próprias exceções específicas, permitindo identificar precisamente a origem de falhas.

---

## Índice

- [Exceções de RedisModel](#exceções-de-redismodel)
- [Exceções de Settings](#exceções-de-settings)
- [Exceções de RedisConnect](#exceções-de-redisconnect)
- [Exceções de Getter](#exceções-de-getter)

---

## Exceções de RedisModel

A classe **[RedisModel](./redis-model.md)** lança exceções personalizadas para facilitar o rastreamento de erros de configuração e uso. Todas estão localizadas em:

```python
from redis_okm.exceptions import ...
````

---

### `RedisModelAttributeException`

**Descrição:**
Lançada quando um atributo fornecido é inválido, não existe no modelo, ou tem nomenclatura proibida (`__duplo__`).

**Exemplo:**

```python
class User(RedisModel):
    __db__ = "default"
    name: str

user = User(username="not_declared")  # Erro: "username" não está definido
```

---

### `RedisModelInvalidNomenclatureException`

**Descrição:**
Lançada quando o modelo declara um atributo com nomes reservados (que começam e terminam com `__`).

**Exemplo:**

```python
class Invalid(RedisModel):
    __db__ = "default"
    __custom__: str  # Proibido
```

---

### `RedisModelForeignKeyException`

**Descrição:**
Relacionada a erros no uso de chaves estrangeiras, incluindo:

* Definição de modelo como chave para si mesmo;
* Falta de valor para uma foreign key obrigatória;
* Uso de `__action__` sem chave estrangeira correspondente;
* Incompatibilidade de conexão entre modelos;
* Referência a registros inexistentes.

**Exemplo:**

```python
class Country(RedisModel):
    __db__ = "default"
    code: str

class City(RedisModel):
    __db__ = "default"
    name: str
    country: Country
    __action__ = {
        "country": "RESTRICT"
    }

city = City(name="Lisbon", country="XX")  # "XX" não existe
```

---

### `RedisModelTypeValueException`

**Descrição:**
Lançada quando o valor de um atributo não corresponde ao tipo declarado.

**Exemplo:**

```python
class Product(RedisModel):
    __db__ = "default"
    price: float

product = Product(price="cheap")  # str em vez de float
```

---

## Exceções de Settings

Exceções levantadas pela classe **[Settings](./settings.md)**, relacionadas a configurações de ambiente, arquivos `.env`, e definição de bancos nomeados.

---

### `SettingsEnvfileNotFoundException`

**Descrição:**
Arquivo `.env` especificado não foi encontrado.

```text
The .env file for environment variables was not found!
```

---

### `SettingsEnvkeyException`

**Descrição:**
Uma chave do tipo `env:VAR_NAME` não está presente no arquivo `.env`.

```text
"env:REDIS_URL" key does not exist in environment variables (.env)!
```

---

### `SettingsUnknownDBException`

**Descrição:**
Nome de banco solicitado não foi previamente registrado via `settings.set_config()`.

```text
There is no database named: mydb!
```

---

### `SettingsInvalidDBNameException`

**Descrição:**
Definição inválida de nome de banco — não segue o padrão `"nome:index"`.

```text
Database index definition must be in two parts, separated by ":"! Invalid definition: "wrongindex"
```

---

### `SettingsExistingDBException`

**Descrição:**
Conflito de nomes ou índices entre bancos nomeados.

```text
Could not set database "prod:1" because it already belongs to a named database (dev)!
```

---

## Exceções de RedisConnect

Exceções levantadas pela classe **[RedisConnect](./redis-connect.md)**, associadas a operações de conexão, inserção, obtenção, exclusão e consistência de dados.

---

### `RedisConnectionSettingsInstanceException`

**Descrição:**
O argumento `settings` não é uma instância da classe `Settings`.

```text
UserModel: settings must be an instance of Settings! settings_handler: dict
```

---

### `RedisConnectConnectionFailedException`

**Descrição:**
Falha ao conectar ao Redis após múltiplas tentativas.

```text
UserModel: Unable to connect to Redis database: ConnectionError(...)
```

---

### `RedisConnectionAlreadyRegisteredException`

**Descrição:**
Tentativa de adicionar um registro com ID já existente e `exists_ok=False`.

```text
UserModel: This id (0) already exists in the database!
```

---

### `RedisConnectForeignKeyException`

**Descrição:**
Erros com chaves estrangeiras, incluindo:

* Diferença na configuração de conexão entre modelos;
* Registro referenciado não existe;
* Restrição de remoção por `__action__`.

```text
UserModel: Foreign key "category_id" (CategoryModel) with ID 2 has no record!
```

🔗 Veja também: [`RedisModelForeignKeyException`](#redismodelforeignkeyexception)

---

### `RedisConnectTypeValueException`

**Descrição:**
Valor com tipo divergente do esperado ao adicionar dados.

```text
UserModel: Divergence in the type of the attribute "metadata". expected: "dict" - received: "list"
```

---

### `RedisConnectInvalidExpireException`

**Descrição:**
Valor de `__expire__` não pode ser convertido para `float`.

```text
UserModel: expire must be convertible to float! expire: "ten"
```

---

### `RedisConnectNoIdentifierException`

**Descrição:**
Nenhum identificador fornecido para `exists` ou `delete`.

```text
UserModel: Use an instance of the model or provide an identifier.
```

---

### `RedisConnectGetOnCorruptException`

**Descrição:**
Valor inválido passado para o parâmetro `on_corrupt` em `get`.

```text
on_corrupt must be "flag", "skip" or "ignore"! on_corrupt: "break"
```

---

### `RedisConnectNoRecordsException`

**Descrição:**
Tentativa de deletar um registro inexistente com `non_existent_ok=False`.

```text
UserModel: This id (5) does not exist in the database!
```

---

## Exceções de Getter

Exceções da classe **[Getter](./getter.md)**, utilizadas em `get()` e suas extensões de filtragem, ordenação e inspeção.

---

### `GetterNotListModelsException`

**Descrição:**
O valor inicial passado ao `Getter` não é uma lista.

```text
get_returns must be a list! get_returns: 42 (int)
```

---

### `GetterNotRedisModelException`

**Descrição:**
Algum elemento da lista passada não é instância de `RedisModel`.

```text
All models passed to Getter must be a class that inherits from RedisModel. FooClass does not inherit RedisModel!
```

---

### `GetterDifferentModelsException`

**Descrição:**
A lista passada contém modelos de tipos diferentes.

```text
All models passed to Getter must be of the same type/class (UserModel). ProductModel != UserModel
```

---

### `GetterAttributeException`

**Descrição:**
Tentativa de filtrar ou ordenar por um atributo que não existe no modelo.

```text
UserModel does not have "email" attribute!
```

---

### `GetterConditionTypeException`

**Descrição:**
O tipo do valor usado em `filter_by()` é incompatível com o atributo.

```text
The "age" condition must be a possible int. age: "abc" (str)
```

---

### `GetterCorruptionException`

**Descrição:**
O registro encontrado está marcado como corrompido (`__status__ = False`).

```text
UserModel: The information in this record (id: 7) is corrupt!
```

---

### `GetterReferenceTypeException`

**Descrição:**
O argumento `reference` em `first()` ou `last()` não é do tipo `str`.

```text
reference must be a str (string)! reference: 123 (int)
```
