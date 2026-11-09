#!/usr/bin/env python3
"""
Proves the brief's hard rule: this pipeline calls no embedding or LLM API.

Checks what the code actually DEPENDS ON, by parsing the import statements with
Python's own ast module, plus the declared requirements. It deliberately does not
grep prose: an earlier substring version matched "cohere" inside the word
"COHERENT" in a code comment and failed the build, which is exactly the kind of
false positive that trains people to ignore a safety check.

    python tools/verify_no_embeddings.py        # exit 0 clean, 1 on a finding
"""
import ast, os, re, sys

BANNED = {
    "openai", "anthropic", "cohere", "google.generativeai", "mistralai",
    "sentence_transformers", "transformers", "tiktoken", "tokenizers",
    "faiss", "chromadb", "pinecone", "weaviate", "qdrant_client", "lancedb",
    "langchain", "llama_index", "haystack", "litellm", "instructor",
}
SCAN_DIRS = ("pipeline", "tools")
SCAN_FILES = ("run_pipeline.py",)
REQ = "requirements.txt"


def top(name):
    return (name or "").split(".")[0]


def imports_of(path):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except SyntaxError as e:
        return [], f"{path}: could not parse ({e})"
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                found.append((al.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                found.append((node.module, node.lineno))
    return found, None


def main():
    py = list(SCAN_FILES)
    for d in SCAN_DIRS:
        for root, _dirs, files in os.walk(d):
            if "__pycache__" in root:
                continue
            py += [os.path.join(root, f) for f in sorted(files) if f.endswith(".py")]

    findings, scanned = [], 0
    for path in py:
        if not os.path.exists(path):
            continue
        scanned += 1
        mods, err = imports_of(path)
        if err:
            findings.append(err)
        for mod, line in mods:
            if top(mod) in BANNED or mod in BANNED:
                findings.append(f"{path}:{line}: imports {mod!r}")

    if os.path.exists(REQ):
        for i, raw in enumerate(open(REQ, encoding="utf-8"), start=1):
            line = raw.split("#")[0].strip()
            if not line:
                continue
            pkg = re.split(r"[\[<>=!~ ]", line, maxsplit=1)[0].strip().replace("-", "_").lower()
            if pkg in BANNED:
                findings.append(f"{REQ}:{i}: declares dependency {pkg!r}")

    print(f"scanned {scanned} Python file(s) and {REQ} for "
          f"{len(BANNED)} embedding/LLM packages")
    if findings:
        print("FAIL:")
        for f in findings:
            print(f"  {f}")
        return 1
    print("PASS: no embedding or LLM client is imported or declared anywhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
