import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from typing import Iterable
import argparse

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")


EXCLUDE_DIRS = {".git", "node_modules", ".venv", "dist", "build", "__pycache__", ".serverless"}
EXCLUDE_FILES = {".DS_Store", ".env"}

def list_files(root: Path):
    for p in root.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.is_file() and p.name not in EXCLUDE_FILES:
            yield p

def read_file(path: Path) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="ignore")
        if len(data) > 10000:
            return data[:10000] + "\n\n[TRUNCATED]\n"
        return data
    except Exception as e:
        return f"Could not read text for file {path}"


def build_context(root: Path) -> str:
    parts = [f"Project root: {root}\n", "File list:\n"]
    files = list(list_files(root))

    for file in files:
        rel_path = file.relative_to(root)
        parts.append(f"- {rel_path}\n")

    parts.append("\nFiles truncated\n")

    for file in files:
        rel_path = file.relative_to(root)
        parts.append(f"\n--- FILE: {rel_path} ---\n")
        parts.append(read_file(file))       

    return "".join(parts)

def ask_openai(question: str, context: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a skilled senior engineer. Answer concisely."
                    "If you are not sure about a question, say so. It is important to understand the question before answering."
                )
            },
            {
                "role": "user",
                "content": (
                    f"CONTEXT: \n {context} \n QUESTION: {question}"
                )
            }
        ]
    )

    return response.output_text
    
def main():
    parser = argparse.ArgumentParser(description="Repo Assistant")
    parser.add_argument("path", type=str, help="Path to the repository")
    parser.add_argument("--url", "-u", type=str, required=False, help="URL of the repository (optional)")
    parser.add_argument("--question", "-q", type=str, required=True, help="Question to ask about the repository")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    print("Scanning:", root)
    print("Exists:", root.exists())
    context = build_context(root)

    answer = ask_openai(args.question, context)
    print(answer)

if __name__ == "__main__":
    main()
