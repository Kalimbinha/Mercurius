# Mercurius 🟤

Biblioteca leve para gerar **endpoints CRUD** automáticos para **FastAPI** a partir de modelos **SQLAlchemy**.

![CI](https://github.com/Kalimbinha/Mercurius/actions/workflows/ci.yml/badge.svg)  

---

## 🔹 O que é

`Mercurius` cria rotas REST automaticamente (`list`, `get`, `create`, `update`, `delete`) a partir de:

- Modelos **SQLAlchemy**
- Schemas **Pydantic**

Ele é ideal para:
- Prototipagem rápida de recursos CRUD  
- Aplicações internas e dashboards  
- Padrão consistente de endpoints em projetos FastAPI + SQLAlchemy  

---

## ✨ Principais features

- Geração automática de rotas CRUD  
- Suporte a **schemas separados**: read / create / update  
- Paginação (`skip`/`limit`), filtros (`filters=field:value`) e ordenação (`sort_by`/`sort_dir`)  
- Injeção de dependências por operação (ex.: autenticação apenas em `create`)  
- Whitelist de campos para filtros e ordenação  
- Compatível com **Pydantic v1 e v2**

---

## ⚙️ Registro principal

```python
from mercurius import Mercurius

Mercurius(app, model, read_schema, db_session_dep, *,
           create_schema=None, update_schema=None,
           prefix=None, pk_name='id',
```
Biblioteca leve para gerar endpoints CRUD automáticos para FastAPI a partir de modelos SQLAlchemy.

---

## 🔹 O que é

`Mercurius` cria rotas REST automaticamente: `list`, `get`, `create`, `update` e `delete`, a partir de:

- Modelos SQLAlchemy (ORM mapped)
- Schemas Pydantic (compatível v1 e v2)

Indicado para prototipagem rápida, aplicações internas, dashboards e para padronizar endpoints em projetos FastAPI + SQLAlchemy.

---

## ✨ Principais features

- Geração automática de rotas CRUD
- Suporte a schemas separados: read / create / update
- Paginação (`skip` / `limit`), filtros (`filters=field:value`) e ordenação (`sort_by` / `sort_dir`)
- Injeção de dependências por operação (ex.: autenticação apenas em `create`)
- Whitelist de campos permitidos para filtros e ordenação
- Compatível com Pydantic v1 e v2

---

## ⚙️ Uso básico

Importante: o construtor principal é:

```py
from mercurius import Mercurius

Mercurius(app, model, read_schema, db_session_dep,
           create_schema=None, update_schema=None,
         prefix=None, pk_name='id',
           operations=('list','get','create','update','delete'),
           tags=None, operation_dependencies=None,
           filter_fields=None, sort_fields=None)
```

Parâmetros comuns

| Parâmetro | Descrição |
|---|---|
| app | Instância de FastAPI ou APIRouter |
| model | Classe SQLAlchemy mapeada |
| read_schema | Pydantic schema usado para leitura/serialização |
| db_session_dep | Dependência FastAPI que retorna uma sessão SQLAlchemy |
| create_schema / update_schema | Schemas opcionais para validação de payloads |
| operation_dependencies | Dict com dependências por operação (list,get,create,update,delete) |
| filter_fields / sort_fields | Listas com campos permitidos para filtros/ordenação |

Query params suportados (rota `list`)

- `skip` — int (offset)
- `limit` — int (tamanho da página)
- `sort_by` — nome do campo
- `sort_dir` — `asc` ou `desc`
- `filters` — múltiplos parâmetros no formato `filters=field:value` (ex.: `?filters=name:john&filters=age:30`)

---

## 📝 Exemplo mínimo

```py
from fastapi import FastAPI
from mercurius import Mercurius
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Integer, default=0)

class ItemRead(BaseModel):
    id: int
    name: str
    value: int

class ItemCreate(BaseModel):
    name: str
    value: int = 0

def get_db():
    ...

app = FastAPI()

Mercurius(
    app,
    Item,
    ItemRead,
    get_db,
    create_schema=ItemCreate,
    filter_fields=['name', 'value'],
    sort_fields=['value'],
)
```

Rotas criadas automaticamente

| Método | Endpoint | Operação |
|---:|:---|:---|
| GET | /items | list |
| GET | /items/{id} | get |
| POST | /items | create |
| PUT | /items/{id} | update |
| DELETE | /items/{id} | delete |

---

## 🔒 Protegendo rotas por operação

Você pode passar dependências por operação:

```py
from fastapi import Depends

def require_auth(...):
    ...

Mercurius(
    app,
    Item,
    ItemRead,
    get_db,
    create_schema=ItemCreate,
    operation_dependencies={'create': [Depends(require_auth)]}
)
```

---

## 🚀 Instalação (desenvolvimento)

No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## 🎯 Executando o exemplo

No PowerShell:

```powershell
uvicorn examples.main:app --reload
```

## ✅ Testes

Instale as dependências para teste e execute:

```powershell
python -m pip install pytest httpx
pytest -q
```

## 📂 Estrutura do repositório

```
mercurius/
├─ mercurius/         # pacote principal
├─ examples/main.py    # exemplo de uso
├─ tests/test_crud.py  # testes unitários
├─ pyproject.toml / setup.py
└─ README.md
```


## 🌟 Recursos avançados

- Whitelist de campos para filtros e ordenação
- Paginação automática
- Dependências por operação (autenticação, roles, etc.)
- Compatível com Pydantic v1 / v2

---

