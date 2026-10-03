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
# Next.js writes agent context files itself: create-next-app always, and `next dev` (16.3 and later) when it
# detects a coding agent. Its AGENTS.md holds only this managed block, and its CLAUDE.md only "@AGENTS.md"
# (https://nextjs.org/docs/app/guides/ai-agents). Such files are not counted as traces of any agent.
NEXTJS_BLOCK = re.compile(r"<!-- BEGIN:nextjs-agent-rules -->.*?<!-- END:nextjs-agent-rules -->", re.S)
CLAUDE_FILE = re.compile(r"(^|/)claude\.md$", re.I)
ENV_FILE = re.compile(r"(^|/)\.env(\.[^/]*)?$")
ENV_TEMPLATE = re.compile(r"\.(example|sample|template|dist|defaults?|tpl)$", re.I)
TEST_FILE = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]+\.py$|_test\.(py|go)$|\.(test|spec)\.[jt]sx?$")
# A test definition inside a test file: pytest/unittest, Jest/Vitest/Mocha, Go.
TEST_DEF = r"^\s*(async\s+)?def\s+test_|^\s*class\s+Test|\b(it|test|describe)\s*\(\s*['\"`]|^func\s+Test[A-Z_]"
TEST_SOURCE = re.compile(r"\.(py|go|[jt]sx?|mjs|cjs)$")
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


def context_files(git_dir: Path, own_paths: list[str]) -> dict:
    """AGENTS.md and CLAUDE.md files that a person or an agent wrote, outside vendored folders.

    An AGENTS.md that holds only the Next.js block, and a CLAUDE.md that holds only "@AGENTS.md" next to an
    AGENTS.md with that block, are left out. The *_any_path flags keep the earlier definition (any file of that
    name, vendored folders included) so that the number of excluded files can be reported.
    """
    nextjs_dirs, agents_own, nextjs = set(), False, False
    for p in own_paths:
        if AGENT_FILES["agents_md"].search(p):
            text = git(git_dir, "show", f"HEAD:{p}")
            if NEXTJS_BLOCK.search(text):
                nextjs = True
                nextjs_dirs.add(str(PurePosixPath(p).parent))
                if not NEXTJS_BLOCK.sub("", text).strip():
                    continue
            agents_own = True
    claude_own = False
    for p in own_paths:
        if AGENT_FILES["claude_md"].search(p):
            if (CLAUDE_FILE.search(p) and "/.claude/" not in f"/{p}" and str(PurePosixPath(p).parent) in nextjs_dirs
                    and git(git_dir, "show", f"HEAD:{p}").strip() == "@AGENTS.md"):
                continue
            claude_own = True
    return {"agents_md": int(agents_own), "claude_md": int(claude_own), "nextjs_agent_files": int(nextjs)}


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

    test_paths = [p for p, _ in own if TEST_FILE.search(p)]
    test_code = [p for p in test_paths if TEST_SOURCE.search(p)]
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
        "tests": int(bool(test_paths)),
        "test_functions": int(bool(test_code) and bool(
            git(git_dir, "grep", "-I", "-l", "-E", TEST_DEF, "HEAD", "--", *test_code[:300]).strip())),
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
    own_paths = [p for p, _ in own]
    for key, pattern in AGENT_FILES.items():
        row[key] = int(any(pattern.search(p) for p in own_paths))
    row["agents_md_any_path"] = int(any(AGENT_FILES["agents_md"].search(p) for p in paths))
    row["claude_md_any_path"] = int(any(AGENT_FILES["claude_md"].search(p) for p in paths))
    row.update(context_files(git_dir, own_paths))
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
