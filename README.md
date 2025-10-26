# Mercurius

Biblioteca leve para gerar endpoints CRUD (FastAPI) a partir de modelos SQLAlchemy.

![CI](https://github.com/Kalimbinha/Mercurius/actions/workflows/ci.yml/badge.svg)

## O que é

`Mercurius` gera endpoints CRUD automaticamente a partir de um modelo SQLAlchemy e schemas Pydantic.

Principais features:
- Geração automática de rotas: list, get, create, update, delete
- Suporte a schemas separados (read/create/update)
- Paginação (skip/limit), filtragem simples (`filters` como `field:value`) e ordenação (sort_by, sort_dir)
- Injeção de dependências por operação (ex.: autenticação por rota)

## Exemplo mínimo

```python
from fastapi import FastAPI
from mercurius import Mercurius

app = FastAPI()

# supondo: Model (SQLAlchemy), ItemRead (Pydantic), get_db dependency
Mercurius(app, Model, ItemRead, get_db, create_schema=ItemCreate, update_schema=ItemUpdate)
```

Protegendo apenas a criação com uma dependência de autenticação:

```python
def require_auth(user=Depends(get_current_user)):
	return user

Mercurius(
	app,
	Model,
	ItemRead,
	get_db,
	create_schema=ItemCreate,
	operation_dependencies={"create": [require_auth]}
)
```

## Query params suportados na listagem

- skip: int (offset)
- limit: int
- sort_by: nome do campo
- sort_dir: `asc` ou `desc`
- filters: múltiplos parâmetros `filters=field:value` (por exemplo `?filters=name:john&filters=age:30`)

## Testes locais

Rode os testes com:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest httpx
pytest -q
```

## CI/CD (GitHub Actions)

Adicionei dois workflows em `.github/workflows/`:

- `ci.yml` — roda testes em push/PR (Python 3.10/3.11/3.12)
- `publish.yml` — constrói e publica no PyPI quando você pushar uma tag `vX.Y.Z`

### Notas sobre segurança de filtros

O `Mercurius` agora suporta whitelists para campos utilizados em filtros e ordenação, evitando exposição acidental de atributos do modelo. Para ativar, passe `filter_fields` e/ou `sort_fields` ao registrar:

```python
Mercurius(
	app,
	Model,
	ItemRead,
	get_db,
	create_schema=ItemCreate,
	filter_fields=["name", "value"],
	sort_fields=["value"],
)
```

Para publicar automaticamente no PyPI, crie um token de API no PyPI e adicione-o nos _Secrets_ do repositório GitHub:

1. No PyPI: https://pypi.org/manage/account/token/ — crie um token com o escopo desejado.
2. No GitHub: Settings -> Secrets -> Actions -> New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: o token do PyPI

Quando quiser publicar, crie uma tag semântica e faça push:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

O workflow `publish.yml` será acionado e fará upload dos artefatos para o PyPI usando o token.

## Observações e boas práticas

- Recomendo configurar um `LICENSE` (por exemplo MIT) antes de publicar.
- Considere habilitar branch protection na `main` e exigir CI verde antes do merge.
- Para segurança, nunca coloque tokens no código — use os _Secrets_ do GitHub.

## Estado atual

- O pacote já foi estruturado no layout `src/mercurius` e pode ser instalado localmente via `pip install -e .`.
- Há um exemplo em `examples/main.py` e testes em `tests/test_crud.py`.

---

Se quiser eu configuro também o `LICENSE` (MIT) e um workflow de CI que rode lint/mypy/coverage. Diga quais extras prefere.