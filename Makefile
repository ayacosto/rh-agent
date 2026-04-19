.PHONY: start stop logs ingest test clean rebuild

start:
	docker compose up -d
	@echo "Application demarree sur http://localhost:3000"
	@echo "API disponible sur http://localhost:8000/docs"

stop:
	docker compose down
	@echo "Tous les services arretes"

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-rag:
	docker compose logs -f init-rag

ingest:
	docker compose restart init-rag
	@echo "Reindexation des documents lancee"

test:
	@echo "Execution des tests..."
	cd tests && python run_tests.py

clean:
	docker compose down -v --remove-orphans
	@echo "Conteneurs et volumes supprimes"

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "Rebuild complet termine"

status:
	docker compose ps

pull-model:
	@echo "Utilisation de Groq API - aucun modele a telecharger"