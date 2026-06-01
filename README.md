# Bolao Bonassi

Aplicacao Flask separada em backend de API e frontend estatico.

## Estrutura

- `backend/app`: API Flask organizada por dominio.
- `backend/app/<dominio>/models.py`: entidades e mapeamento SQLAlchemy.
- `backend/app/<dominio>/schemas.py`: validacao e serializacao de entrada/saida.
- `backend/app/<dominio>/service.py`: regras de negocio e orquestracao.
- `backend/app/<dominio>/routes.py`: camada HTTP, sem regra de negocio.
- `frontend`: telas HTML, CSS e JavaScript estaticos.

## Rodando localmente

```bash


