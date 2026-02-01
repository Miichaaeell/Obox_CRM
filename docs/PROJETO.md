# Documentação do Projeto Obox CRM

## Visão geral
O Obox CRM é uma aplicação Django voltada à gestão de processos de negócio. A base é composta por apps de domínio (contas, empresas, vendas e estudantes), com tarefas assíncronas executadas via Celery e dados persistidos em PostgreSQL. Para desenvolvimento local, o stack pode ser executado por Docker Compose.

## Arquitetura e módulos
- **Django core** (`core/`): configurações (`settings.py`), URLs, templates e arquivos estáticos.
- **Apps de domínio**: `accounts/`, `enterprise/`, `sales/`, `students/` — cada app concentra seus modelos, views, urls e testes.
- **Serviços compartilhados** (`services/`): utilitários e integrações reutilizáveis.
- **Integrações**:
  - **Django REST Framework** para APIs.
  - **Celery + django-celery-beat/results** para tarefas e agendamentos.
  - **Webmania** (variáveis em `.env`) para integrações externas.

## Dados e configuração
- As variáveis de ambiente são lidas via `python-decouple`.
- Conexão de banco é configurada por `DATABASE_URL` usando `dj_database_url`.
- O projeto possui seed de dados em `fixtures/initial_data.json` (carregado com `loaddata`).

## Ambiente de desenvolvimento
Requisitos recomendados:
- Python 3.13
- PostgreSQL e RabbitMQ (ou Docker Compose)

Comandos úteis (local):
```
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data
python manage.py runserver
```

Stack completa com Docker:
```
docker compose up --build
```

## Tarefas assíncronas
O processamento assíncrono roda em dois processos principais:
- Worker: `celery -A core worker -l info`
- Beat: `celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`

## Testes e qualidade
- Testes ficam em `*/tests.py`.
- Execução: `python manage.py test` ou `python manage.py test <app>`.
- O CI utiliza checks de lint/format via pre-commit (ruff e black).

## Organização de entregas
Para mudanças que afetam:
- **Banco**: inclua migrations e descreva o impacto nos PRs.
- **Dados iniciais**: atualize `fixtures/initial_data.json` e documente no PR.
- **Integrações**: documente variáveis novas no `.env.example`.
