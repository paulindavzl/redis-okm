# RedisModel

Esta é a classe base de todo  **modelo RedisOKM** , responsável por estruturar seus atributos e definir seu comportamento.

---

## Sumário

- **[O que é um modelo](#o-que-é-um-modelo "Veja o que define um modelo")** - Veja o que é um **modelo** no **RedisOKM**.
- **[Estrutura básica de um modelo](#estrutura-básica-de-um-modelo)** - Veja como é a estrutura básica de um **modelo**.
- **[Chave Estrangeira](#chave-estrangeira)** - Veja o que são chaves estrangeiras no **RedisOKM**.
  - **[Como usar na prática](#como-usar-na-prática)** - Aprenda a usar **chave estrangeira** no **RedisOKM**.
  - **[Ações](#ações)** - Veja como definir ações para as **chaves estrangeiras**.
  - **[Regras](#regras)** - Saiba quais são as regras de uso das **chaves estrangeiras** no **RedisOKM**.
- **[Docs](#docs "Outras documentações")** - Veja outras documentações com instruções para melhores usos da biblioteca

## O que é um modelo

Um **modelo** no **RedisOKM** representa uma tabela, com cada instância representando um possível registro.

> ⚠️ **Observação:** O **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")** não armazena valores no formato **coluna/tabela**, mas o **RedisOKM** se organiza com base neste formato!

---

## Estrutura básica de um modelo

Por padrão, um **modelo** já vem com alguns atributos e definições. Isso ajuda a simplificar a estruturação e poupar tempo, alterando-os somente quando necessário:

```python
from redis_okm.tools import RedisModel


class ExampleModel(RedisModel):
	__db__ = None # índice do banco de dados que modelo será registrado (obrigatório declará-lo)
	__idname__ = None # nome do atributo que representa o ID do modelo (caso não declarado será o primeiro atributo do modelo)
	__autoid__ = True # informa se o ID do modelo será atribuido de forma automática, com base na quantidade de registros do modelo
	__hashid__ = False # informa se ID será uma HASH (por padrão MD5 - pode ser alterada com Settings)
	__settings__ = settings # informa a instância de Settings que o modelo usará (por padrão a instância base)
	__action__ = None # informa as ações que serão tomadas com base nas chaves estrangeiras (obrigatório caso use chaves estrangeiras – cada chave deve estar mapeada para "restrict" ou "cascade")
	__expire__ = None # informa o tempo de expiração do registro (o registro não expira se não for definido)
	__tablename__ = None # informa o nome do modelo para registro (caso não informado será o nome da classe em minúsculo - examplemodel)
```

> ⚠️ **Atenção:** O **ID** do modelo deve ser `int` ou `str`, caso contrário ocorrerá um **[erro](./Exceptions "redis-modelypeValueException").**
>
> Caso o **ID** seja informado por `__idname__`, não é necessário atribuí-lo na estrutura do modelo:

```python
class ExampleModel(RedisModel):
	...
	__idname__ = "id"

	id: int # pode ser  dispensado
```

---

## Chave Estrangeira

O **RedisOKM** possui um sistema bem simples de chaves estrangeiras:

```python
from redis_okm.tools import RedisModel, RedisConnect


class UserModel(RedisModel):
	__db__ = "users"
	...

	uid: int
	name: str
	email: str
	password: str


class OrderModel(RedisModel):
	__db__ = "orders"
	...
	__action__ = {"user": "cascade"} # ação que será tomada caso a referência seja excluída (cascade/restrict)

	order_id: int
	user: UserModel # chave estrangeira
	elements: dict
```

Neste exemplo, temos um modelo que representa um usuário e outro que representa um pedido. **Pedido** possui uma chave `user` que referencia o **usuário** que realizou o pedido. Você define a chave estrangeira indica o **modelo** de referência.

> ⚠️ **Nota:** O **modelo** referenciado deve herdar **RedisModel**!

### Como usar na prática

Para instanciar um modelo que usar chave estrangeira, você precisa indicar o **ID** do modelo de referência e este precisa estar registrado:

```python
new_order = OrderModel(user=0, elements={...}) # o pedido será registrado referenciando o registro do usuário com ID 0
RedisConnect.add(new_order)

# caso não possua registro com este ID, um erro será levantado!
```

No momento em que um modelo com chave estrangeira é instanciado, o atributo que representa a chave estrangeira **pode ser acessado como um método**, retornando o modelo de referência atualizado.

```python
order = RedisConnect.get(OrderModel).filter_by(order_id=0)
user = order.user()  # user() retorna o modelo referenciado com base no ID salvo
```

Isso é possível porque o RedisOKM sobrescreve o método especial `__getattr__`, responsável por interceptar o acesso a atributos dinâmicos. Quando esse atributo for identificado como uma chave estrangeira, o RedisOKM retorna automaticamente uma função que consulta e retorna o modelo relacionado com base no ID informado.

> ⚠️ Sempre que `user()` (ou qualquer atributo que referencie outro modelo) for chamado, ele realizará uma nova consulta no Redis para garantir que os dados estejam atualizados.

#### Explicação simples

- Você define `user: UserModel` → isso é só uma anotação.
- Ao instanciar com `user=0`, o valor salvo no Redis é um ID (int ou str).
- Quando você chama `order.user()`, o `__getattr__` detecta que `user` é uma FK e retorna dinamicamente uma função.
- Essa função faz: `RedisConnect.get(UserModel).get_by_id(0)`

### Ações

As **ações**, definidas por `__action__`, indicam o comportamento que ocorrerá quando o modelo de referência tentar ser excluído. **RedisOKM** só possui suporte para as ações:

- **restrict** - impede que a referência seja excluída caso exista um registro referenciando-o
- **cascade** - exclui o registro referenciado caso a referência seja excluída

```python
class OrderModel(RedisModel):
	...
	__action__ = {"user": "cascade", "product": "restrict"}

	...


# cascade: quando o registro referenciado (user) for apagado, os registros que o referenciam (OrderModel) também serão apagados
# restrict: impede que o registro de product seja apagado enquanto existir um registro de OrderModel
```

Você também pode usar uma instância da chave estrangeira ao instanciar um modelo que o a referencia:

```python
...

user = UserModel(name="paulindavzl", ...)
new_order = OrderModel(user=user, elements={...}) 

# para indicar a chave estrangeira, foi usada uma instância do modelo referenciado (user - UserModel)
```

### Regras

O **RedisOKM** impõem algumas regras bem claras sobre as **Chaves Estrangeiras**:

- Os modelos relacionados com chaves estrangeiras podem estar em bancos de dados diferentes, mas devem estar no mesmo servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")!**
  - De preferência, use o mesmo `__settings__` nos modelos relacionados.
- Modelos que usam chave estrangeira não podem conter `__expire__` ou tempo de expiração!
- Atributos que referenciam outros modelos não podem conter valores padrão!

> ⚠️ **Atenção:** O **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")** não oferece nenhum suporte a chaves estrangeiras ou praticamente qualquer outra funcionalidade disponibilizadas pelo **RedisOKM**, por tanto, todas as alterações nos registros devem ser feitas usando a biblioteca! Alterações externas pode ocasionar em erros de corrompimento dos dados, o que impedirá a leitura dos mesmos.

---

## Docs

Veja também outras documentações úteis para trabalhar com **RedisOKM:**

### Boas práticas

O **RedisOKM** possui uma seção que **boas práticas** para melhorar o uso da biblioteca. Veja mais em **[Boas Práticas](./good-practices.md "Veja mais sobre Boas Práticas.").**

### RedisConnect

**RedisConnect** é a classe que se conecta de fato com o servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. Veja mais sobre ela em **[RedisConnect](./redis-connect.md "Veja mais sobre RedisConnect")**.

### Settings

**Settings** é a classe usada para configurar e obter configurações gerais sobre conexões e outras. Veja mais sobre ela em **[Settings](./settings.md "Veja mais sobre Settings")**.

### Getter

**Getter** é a classe retornada ao fazer uma consulta com **[RedisConnect](#RedisConnect "Veja mais sobre RedisConnect")**. Ela agrupa o retorno de mais de um modelo e permite consultas personalizadas. Veja mais sobre ela em **[Getter](./getter.md "Veja mais sobre Getter")**.

### Exceptions

O **RedisOKM** possui exceções personalizadas. Veja mais informações em **[Exceptions](./exceptions.md "Veja mais sobre Exceptions")**.

### Licença

**RedisOKM** é distribuído sob a Licença MIT. Veja o arquivo **[LICENSE](./LICENSE "LICENÇA de uso")** para mais detalhes.
