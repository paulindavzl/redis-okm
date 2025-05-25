# Settings

Esta classe é responsável por armazenar as configurações de conexão com **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. Por padrão, todo modelo usa uma instância global de **Settings**, obtida com `redis_okm.tools import settings`:

```python
# redis_okm/tools.py

settings = Settings(path="redis_configure.json") # por padrão, Settings referencia o arquivo "redis_configure.json" (pode ser alterado ao instanciar a classe)
```

## Sumário

- **[Estrutura padrão](#estrutura-padrão)** - Veja como é a estrutura padrão de configuração.
- **[Como usar](#como-usar)** - Como usar a classe **Settings**.
  - **[Definir cofigurações](#definir-configurações)** - Aprenda a definir configurações com e sem `envfile`.
  - **[Nomear índices de bancos de dados](#nomear-bancos-de-dados)** - Veja como nomeia-se bancos de dados.
  - **[Obter índices nomeados](#obter-índices-dos-bancos-de-dados-pelo-nome)** - Veja como obter o valor dos índices nomeados.
- **[Docs](#docs "Outras documentações")** - Veja outras documentações com instruções para melhores usos da biblioteca.

## Estrutura padrão

A estrutura de um arquivo de configuração gerado por **Settings** é essa:

```json
{
    "envfile": null,
    "tests": {
        "use_tests": true,
        "db": "tests",
        "restart_db": true
    },
    "network": {
        "host": "localhost",
        "port": 6379,
        "password": null
    },
    "connection": {
        "decode_response": true,
        "timeout": 30,
        "retry_on_timeout": [
            true,
            3
        ]
    },
    "pools": {
        "max_connections": 10,
        "blocking_timeout": 3
    },
    "structure": {
        "separator": ":",
        "prefix": "cwd",
        "hash_algorithm": "md5"
    },
    "dbname": {
        "tests": 15
    }
}
```

## Como usar

Para definir uma instância de **Settings** em um modelo você deve usar `__settings__`:

```python
from redis_okm.tools import RedisModel, Settings # ou settings (instância já padrão de todo modelo)


# instância de Settings
settings = Settings(path="your_configuration_path.json") # path deve receber um arquivo JSON


class ExampleModel(RedisModel):
	__settings__ = settings
	...
```

### Definir configurações

Para definir configurações, usá-se o método `Settings.set_config(...)`:

```python
...

settings.set_config(
	envfile=".env", # define um arquivo com variáveis de ambiente
	host="env:HOST", # define o servidor do Redis ("env:" indica que é uma chave de variável de ambiente, "HOST" indica a chave da variável de ambiente)
	port="env:PORT", # define a porta do servidor Redis
	...
)

# para definir qualquer configuração, basta por o nome dela seguido do valor que ele deve receber
# para ver o nome das configurações, basta abrir o arquivo de configuração JSON
```

> ⚠️**Atenção:** Definir `envfile` não é obrigatório (mas é **RECOMENDADO**), por tanto, caso não haja `envfile` use os valores diretamente ao definir as configurações: `host="localhost"`.

### Nomear bancos de dados

Para nomear os índices dos bancos de dados é um pouco diferente, você usa o parâmetros `dbname`, que recebe o nome do índice seguido pelo valor (**dbname="name:index"**)

```python
...

settings.set_config(
	dbname="user:0" # para nomear somente um índice usa-se um str
	dbname=["user:0", "product:1"] # para nomear mais de um índice usa-se uma lista de str
	edit_dbname=True/False # permite editar bancos de dados já nomeados
)
```

> ⚠️**Atenção:** Cada índice só pode ter um nome e não pode haver mais de um nome no mesmo arquivo.

Caso você tente definir uma configuração que não existe, ela será criada e poderá ser acessada pelo nome:

```python
...

settings.set_config(example="value")

print(settings.example) # value
```

### Obter índices dos bancos de dados pelo nome

Esta é um método de uso interno do **RedisOKM**. Para obter os índices, usa-se o método `settings.get_db(...)`:

```python
...

index = settings.get_db("testes")
print(index) # 15
```

## Docs

Veja também outras documentações úteis para trabalhar com **RedisOKM:**

### Boas práticas

O **RedisOKM** possui uma seção que **boas práticas** para melhorar o uso da biblioteca. Veja mais em **[Boas Práticas](./good-practices.md "Veja mais sobre Boas Práticas.").**

### RedisConnect

**RedisConnect** é a classe que se conecta de fato com o servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. Veja mais sobre ela em **[RedisConnect](./redis-connect.md "Veja mais sobre RedisConnect")**.

### RedisModel

**RedisModel** é a classe que todo modelo de **RedisOKM** deve herdar. Veja mais sobre em **[RedisModel](./redis-model.md "Veja mais sobre RedisModel")**.

### Getter

**Getter** é a classe retornada ao fazer uma consulta com **[RedisConnect](#RedisConnect "Veja mais sobre RedisConnect")**. Ela agrupa o retorno de mais de um modelo e permite consultas personalizadas. Veja mais sobre ela em **[Getter](./getter.md "Veja mais sobre Getter")**.

### Exceptions

O **RedisOKM** possui exceções personalizadas. Veja mais informações em **[Exceptions](./exceptions.md "Veja mais sobre Exceptions")**.

### Licença

**RedisOKM** é distribuído sob a Licença MIT. Veja o arquivo **[LICENSE](./LICENSE "LICENÇA de uso")** para mais detalhes.
