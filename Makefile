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

# Proves the brief's hard rule: the pipeline calls no embedding or LLM API.
# Checks IMPORTS and DEPENDENCIES, not prose -- an earlier substring version
# matched "cohere" inside the word "COHERENT" in a comment and failed the build.
verify-no-embeddings:
	@python3 tools/verify_no_embeddings.py
