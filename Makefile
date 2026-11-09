.PHONY: pipeline sample broken clean install report

install:
	pip install -r requirements.txt

pipeline:
	python run_pipeline.py

sample:
	python run_pipeline.py --sample 5

broken:
	-python run_pipeline.py --raw data/fixtures/broken --out data/fixtures/out

clean:
	rm -rf data/processed data/fixtures/out

verify-no-embeddings:
	@echo "Scanning pipeline code and requirements for embedding/LLM clients..."
	@if grep -rniE '(openai|cohere|sentence_transformers|tiktoken|faiss|chromadb|pinecone|weaviate|qdrant|embeddings\.create|langchain|llama_index)' \
		--include='*.py' --include='*.txt' pipeline tools run_pipeline.py requirements.txt ; then \
		echo "FAIL: an embedding or LLM client is referenced above."; exit 1; \
	else \
		echo "PASS: no embedding or LLM client appears in the pipeline code or requirements."; \
	fi
