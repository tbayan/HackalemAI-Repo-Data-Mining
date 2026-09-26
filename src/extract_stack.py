"""Phase M2a: Technology and hygiene features at each repo's final state -> data/stack.csv

Reads the default-branch HEAD of every mirror clone (the state the organisers
archived). Records file names, dependency names and yes/no flags only; file
contents are never stored. LLM SDK use is detected from manifests and from
`git grep` over source files, excluding vendored folders.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import PurePosixPath, Path

from tqdm import tqdm

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLONE_DIR = DATA_DIR / "clones"
TABLE = DATA_DIR / "repo_table.csv"
OUT_FILE = DATA_DIR / "stack.csv"

VENDORED = re.compile(r"(^|/)(node_modules|\.venv|venv|env|site-packages|__pycache__|dist|build|\.next|vendor)/")

LANGUAGES = {
    ".py": "Python", ".ipynb": "Jupyter", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".html": "HTML", ".css": "CSS",
    ".scss": "CSS", ".vue": "Vue", ".svelte": "Svelte", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
    ".swift": "Swift", ".rs": "Rust", ".cpp": "C++", ".cc": "C++", ".c": "C", ".cs": "C#", ".php": "PHP",
    ".rb": "Ruby", ".dart": "Dart", ".sql": "SQL", ".sh": "Shell",
}
MARKUP = {"HTML", "CSS", "Jupyter"}

# Dependency name -> label. Names are normalised to lower case with "_" -> "-".
FRAMEWORKS = {
    "react": "React", "next": "Next.js", "vue": "Vue", "svelte": "Svelte", "@sveltejs/kit": "Svelte",
    "@angular/core": "Angular", "vite": "Vite", "tailwindcss": "Tailwind", "express": "Express",
    "@nestjs/core": "NestJS", "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "streamlit": "Streamlit", "gradio": "Gradio", "typescript": "TypeScript (dep)", "prisma": "Prisma",
    "@prisma/client": "Prisma", "sqlalchemy": "SQLAlchemy", "pandas": "pandas", "numpy": "NumPy",
    "scikit-learn": "scikit-learn", "torch": "PyTorch", "lightgbm": "LightGBM", "xgboost": "XGBoost",
    "catboost": "CatBoost", "networkx": "NetworkX", "transformers": "Transformers",
    "sentence-transformers": "sentence-transformers", "openai-whisper": "Whisper",
    "faster-whisper": "Whisper", "chromadb": "Chroma", "faiss-cpu": "FAISS", "supabase": "Supabase",
    "@supabase/supabase-js": "Supabase", "firebase": "Firebase", "pydantic": "Pydantic",
    "uvicorn": "Uvicorn", "pytest": "pytest", "jest": "Jest", "vitest": "Vitest",
    "@playwright/test": "Playwright", "playwright": "Playwright", "aiogram": "aiogram",
    "python-telegram-bot": "python-telegram-bot", "telegraf": "Telegraf",
}
LLM_PACKAGES = {
    "openai": "OpenAI", "@openai/agents": "OpenAI", "openai-agents": "OpenAI",
    "anthropic": "Anthropic", "@anthropic-ai/sdk": "Anthropic",
    "google-generativeai": "Google", "google-genai": "Google", "@google/generative-ai": "Google",
    "@google/genai": "Google", "langchain": "LangChain", "langchain-openai": "LangChain",
    "langchain-core": "LangChain", "@langchain/openai": "LangChain", "langgraph": "LangChain",
    "llama-index": "LlamaIndex", "ai": "Vercel AI SDK", "@ai-sdk/openai": "Vercel AI SDK",
    "groq": "Groq", "mistralai": "Mistral", "ollama": "Ollama", "litellm": "LiteLLM",
}
# Import patterns for source files (git grep -E), per provider.
LLM_IMPORTS = {
    "OpenAI": r"from openai|import openai|require\(['\"]openai['\"]\)|from ['\"]openai['\"]|api\.openai\.com",
    "Anthropic": r"from anthropic|import anthropic|@anthropic-ai/sdk|api\.anthropic\.com",
    "Google": r"google\.generativeai|google\.genai|@google/generative-ai|@google/genai|generativelanguage\.googleapis",
    "LangChain": r"from langchain|import langchain|@langchain/",
    "Ollama": r"import ollama|from ollama|localhost:11434",
}
SOURCE_PATHSPEC = ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.mjs", "*.cjs", "*.go", "*.java", "*.kt",
                   "*.php", "*.rb", "*.cs", ":!:**/node_modules/**", ":!:**/.venv/**", ":!:**/venv/**",
                   ":!:**/dist/**", ":!:**/build/**", ":!:**/.next/**"]

AGENT_FILES = {
    "agents_md": re.compile(r"(^|/)agents\.md$", re.I),  # the AGENTS.md convention; "agent.md" is ambiguous
    "claude_md": re.compile(r"(^|/)claude\.md$|(^|/)\.claude/", re.I),
    "gemini_md": re.compile(r"(^|/)gemini\.md$", re.I),
    "cursor_rules": re.compile(r"(^|/)\.cursorrules$|(^|/)\.cursor/", re.I),
    "copilot_instructions": re.compile(r"(^|/)\.github/(copilot-instructions\.md|instructions/|prompts/)", re.I),
    "other_agent_rules": re.compile(r"(^|/)(\.windsurfrules|\.clinerules|\.aider[^/]*|\.codex/)", re.I),
}
ENV_FILE = re.compile(r"(^|/)\.env(\.[^/]*)?$")
ENV_TEMPLATE = re.compile(r"\.(example|sample|template|dist|defaults?|tpl)$", re.I)
TEST_FILE = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]+\.py$|_test\.(py|go)$|\.(test|spec)\.[jt]sx?$")
DEPLOY = re.compile(r"(^|/)(vercel\.json|netlify\.toml|render\.yaml|fly\.toml|Procfile|railway\.(json|toml)|app\.yaml)$")


def git(git_dir: Path, *args: str) -> str:
    return subprocess.run(["git", f"--git-dir={git_dir}", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def norm(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def deps_from(git_dir: Path, path: str) -> set[str]:
    text = git(git_dir, "show", f"HEAD:{path}")
    name = PurePosixPath(path).name.lower()
    found: set[str] = set()
    if name == "package.json":
        try:
            data = json.loads(text)
            for key in ("dependencies", "devDependencies"):
                found |= {norm(k) for k in (data.get(key) or {})}
        except (json.JSONDecodeError, AttributeError):
            pass
    elif name.startswith("requirements") and name.endswith(".txt"):
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("-"):
                found.add(norm(re.split(r"[=<>~!\[; @]", line, 1)[0]))
    elif name in ("pyproject.toml", "pipfile"):
        found |= {norm(m) for m in re.findall(r'["\']([A-Za-z0-9_.\-]+)\s*(?:[=<>~!\[;]|["\'])', text)}
        found |= {norm(m) for m in re.findall(r"^([A-Za-z0-9_.\-]+)\s*=", text, re.M)}
    elif name == "go.mod":
        found |= {norm(m) for m in re.findall(r"^\s*([\w./\-]+)\s+v\d", text, re.M)}
    return found


def process(name: str) -> dict:
    git_dir = CLONE_DIR / f"{name}.git"
    tree = git(git_dir, "ls-tree", "-r", "-l", "HEAD").splitlines()
    files = []
    for line in tree:
        meta, path = line.split("\t", 1)
        parts = meta.split()
        size = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
        files.append((path, size))
    paths = [p for p, _ in files]
    own = [(p, s) for p, s in files if not VENDORED.search(p)]

    lang_bytes: Counter = Counter()
    for path, size in own:
        lang = LANGUAGES.get(PurePosixPath(path).suffix.lower())
        if lang:
            lang_bytes[lang] += size
    code_langs = {k: v for k, v in lang_bytes.items() if k not in MARKUP}
    primary = max(code_langs, key=code_langs.get) if code_langs else (max(lang_bytes, key=lang_bytes.get) if lang_bytes else "")

    manifests = [p for p, _ in own if PurePosixPath(p).name.lower() in
                 ("package.json", "pyproject.toml", "pipfile", "go.mod")
                 or re.match(r"requirements[^/]*\.txt$", PurePosixPath(p).name.lower())]
    deps: set[str] = set()
    for path in manifests[:30]:
        deps |= deps_from(git_dir, path)
    frameworks = sorted({FRAMEWORKS[d] for d in deps if d in FRAMEWORKS})
    llm = {LLM_PACKAGES[d] for d in deps if d in LLM_PACKAGES}
    for provider, pattern in LLM_IMPORTS.items():
        if provider not in llm and git(git_dir, "grep", "-I", "-l", "-E", pattern, "HEAD", "--", *SOURCE_PATHSPEC).strip():
            llm.add(provider)

    env_files = [p for p in paths if ENV_FILE.search(p) and not ENV_TEMPLATE.search(p)]
    gitignore = git(git_dir, "show", "HEAD:.gitignore") if ".gitignore" in paths else ""
    ignores_env = bool(re.search(r"^\s*/?(\*\*/)?\.env(\*|\.\*|\b)", gitignore, re.M) or "*.env" in gitignore)

    row = {
        "repo": name,
        "files": len(paths),
        "own_files": len(own),
        "primary_language": primary,
        "languages": ";".join(k for k, _ in lang_bytes.most_common()),
        "frameworks": ";".join(frameworks),
        "llm_sdks": ";".join(sorted(llm)),
        "manifests": len(manifests),
        "dockerfile": int(any(re.search(r"(^|/)Dockerfile[^/]*$", p) for p in paths)),
        "compose": int(any(re.search(r"(^|/)(docker-)?compose[^/]*\.ya?ml$", p) for p in paths)),
        "tests": int(any(TEST_FILE.search(p) for p, _ in own)),
        "ci": int(any(re.search(r"^\.github/workflows/[^/]+\.ya?ml$", p) for p in paths)),
        "deploy_config": int(any(DEPLOY.search(p) for p in paths)),
        "notebooks": sum(p.endswith(".ipynb") for p, _ in own),
        "env_file_committed": int(bool(env_files)),
        "env_example": int(any(ENV_FILE.search(p) and ENV_TEMPLATE.search(p) for p in paths)),
        "gitignore": int(".gitignore" in paths),
        "gitignore_covers_env": int(ignores_env),
        "node_modules_committed": int(any("node_modules/" in p for p in paths)),
        "virtualenv_committed": int(any(re.search(r"(^|/)(\.venv|venv)/|site-packages/", p) for p in paths)),
        "pycache_committed": int(any("__pycache__/" in p for p in paths)),
        "readme": int(any(re.fullmatch(r"readme(\.[a-z]+)?", p, re.I) for p in paths)),
    }
    for key, pattern in AGENT_FILES.items():
        row[key] = int(any(pattern.search(p) for p in paths))
    return row


def main() -> None:
    with TABLE.open(encoding="utf-8") as f:
        names = [r["repo"] for r in csv.DictReader(f) if int(r["team_commits"]) > 0]
    with ProcessPoolExecutor() as pool:
        rows = list(tqdm(pool.map(process, names, chunksize=8), total=len(names), desc="Stack", unit="repo"))
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} repos -> {OUT_FILE}")


if __name__ == "__main__":
    main()
