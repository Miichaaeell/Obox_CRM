# Obox CRM

Aplicação web baseada em Django para gestão de processos de negócio (CRM), com tarefas assíncronas via Celery e integração com PostgreSQL/RabbitMQ.

## Stack principal
- Python 3.13 + Django 5.2
- PostgreSQL (persistência)
- Celery + RabbitMQ (tarefas assíncronas/beat)
- Docker/Docker Compose (ambiente completo)

## Estrutura do projeto
- `core/`: configurações do Django, URLs, templates e assets estáticos.
- `accounts/`, `enterprise/`, `sales/`, `students/`: apps de domínio.
- `services/`: serviços compartilhados.
- `fixtures/`: dados iniciais (`fixtures/initial_data.json`).
- `docker-compose.yml`: stack de desenvolvimento (web, postgres, rabbitmq, celery).

## Configuração de ambiente
1. Copie o arquivo de exemplo:
   - `cp .env.example .env`
2. Ajuste as variáveis conforme seu ambiente (banco, RabbitMQ e integrações).

## Como rodar localmente (sem Docker)
1. Crie e ative um virtualenv.
2. Instale dependências:
   - `pip install -r requirements.txt`
3. Execute migrações e seed:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py loaddata initial_data`
4. Suba o servidor:
   - `python manage.py runserver`

## Como rodar com Docker
Suba toda a stack (app + banco + RabbitMQ + Celery):
- `docker compose up --build`

Arquivos úteis:
- `docker-compose.yml` (desenvolvimento)
- `docker-compose-prod.yml` (produção/staging)

## Tarefas assíncronas (Celery)
Em ambiente local, use os serviços do Compose. Para rodar manualmente:
- Worker: `celery -A core worker -l info`
- Beat: `celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`

## Testes
Execute todos os testes:
- `python manage.py test`

Executar apenas um app:
- `python manage.py test accounts`

## Documentação detalhada
Consulte `docs/PROJETO.md` para visão de arquitetura, fluxo de dados e orientações de operação.
