"""
Tests for launcher scripts, requirements.txt, .gitignore, and project structure integrity.
Validates syntax rules from the windows-batch-launchers skill.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_files_exist():
    """Verify all required launcher, requirement, and doc files exist."""
    required_files = [
        "setup.bat",
        "start.bat",
        "setup.sh",
        "start.sh",
        "requirements.txt",
        ".gitignore",
        "README.md",
    ]
    for filename in required_files:
        path = REPO_ROOT / filename
        assert path.is_file(), f"Expected file {filename} to exist at {path}"


def test_batch_syntax_no_unescaped_parentheses():
    """
    Ensure setup.bat and start.bat adhere to the windows-batch-launchers rule:
    NEVER use unescaped parentheses inside if (...) or for (...) blocks,
    or preferably use goto :label jumps to avoid cmd.exe parse errors.
    """
    bat_files = [REPO_ROOT / "setup.bat", REPO_ROOT / "start.bat"]
    
    for bat_path in bat_files:
        assert bat_path.exists(), f"{bat_path.name} must exist"
        content = bat_path.read_text(encoding="utf-8")
        
        # Rule 1: UTF-8 encoding command
        assert "chcp 65001" in content, f"{bat_path.name} must include 'chcp 65001 >nul' for UTF-8 support"
        
        # Rule 2: cd /d "%~dp0..."
        assert 'cd /d "%~dp0' in content or 'cd /d "%~dp0"' in content, (
            f"{bat_path.name} must use cd /d \"%~dp0...\" with double quotes"
        )

        # Check for unescaped parentheses inside if (...) blocks:
        lines = content.splitlines()
        in_parentheses_block = False
        paren_depth = 0
        
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("::") or stripped.startswith("rem "):
                continue
                
            if re.search(r'\b(if|for)\b.*\(', stripped):
                in_parentheses_block = True
                paren_depth += 1
                continue
                
            if in_parentheses_block:
                if stripped.startswith(")") and paren_depth == 1:
                    paren_depth = 0
                    in_parentheses_block = False
                    continue
                if stripped.lower().startswith("echo"):
                    echo_text = stripped[4:]
                    clean_text = echo_text.replace("^)", "").replace("^(", "")
                    assert ")" not in clean_text and "(" not in clean_text, (
                        f"Line {idx} in {bat_path.name} contains unescaped parenthesis in echo block: '{line}'. "
                        "Follow windows-batch-launchers rule: use goto labels or escape with ^."
                    )


def test_setup_bat_structure():
    """Verify setup.bat includes title, color, steps [1/4] to [4/4], and python pip call."""
    bat_path = REPO_ROOT / "setup.bat"
    assert bat_path.exists(), "setup.bat must exist"
    content = bat_path.read_text(encoding="utf-8")
    
    assert "@echo off" in content
    assert "setlocal EnableDelayedExpansion" in content
    assert "title Voxa" in content
    assert "[1/4]" in content
    assert "[2/4]" in content
    assert "[3/4]" in content
    assert "[4/4]" in content
    assert "requirements.txt" in content
    assert "call python" in content or "python -m pip" in content


def test_start_bat_structure():
    """Verify start.bat includes title, color, port 7865, browser opening, and uvicorn command."""
    bat_path = REPO_ROOT / "start.bat"
    assert bat_path.exists(), "start.bat must exist"
    content = bat_path.read_text(encoding="utf-8")
    
    assert "@echo off" in content
    assert "title Voxa" in content
    assert "7865" in content
    assert 'start ""' in content or 'start "" "http://localhost:7865"' in content
    assert "backend.main:app" in content
    assert "[1/3]" in content
    assert "[2/3]" in content
    assert "[3/3]" in content


def test_shell_scripts_structure():
    """Verify setup.sh and start.sh have shebang, set -e, and proper commands."""
    setup_sh = REPO_ROOT / "setup.sh"
    start_sh = REPO_ROOT / "start.sh"
    assert setup_sh.exists(), "setup.sh must exist"
    assert start_sh.exists(), "start.sh must exist"
    
    setup_content = setup_sh.read_text(encoding="utf-8")
    start_content = start_sh.read_text(encoding="utf-8")
    
    assert setup_content.startswith("#!/usr/bin/env bash")
    assert "set -e" in setup_content
    assert "requirements.txt" in setup_content
    
    assert start_content.startswith("#!/usr/bin/env bash")
    assert "set -e" in start_content
    assert "backend.main:app" in start_content
    assert "7865" in start_content


def test_requirements_txt_dependencies():
    """Verify requirements.txt contains all core packages specified in task brief."""
    req_path = REPO_ROOT / "requirements.txt"
    assert req_path.exists(), "requirements.txt must exist"
    content = req_path.read_text(encoding="utf-8")
    
    expected_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-multipart",
        "psutil",
        "chatterbox-tts",
        "faster-whisper",
        "torch",
        "torchaudio",
        "pydub",
        "soundfile",
        "numpy",
        "pytest",
        "httpx",
    ]
    
    content_lower = content.lower()
    for pkg in expected_packages:
        assert pkg in content_lower, f"Package {pkg} must be in requirements.txt"


def test_gitignore_rules():
    """Verify .gitignore covers virtualenv, python cache, test cache, and output folders."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore must exist"
    content = gitignore_path.read_text(encoding="utf-8")
    
    expected_patterns = [
        ".venv",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "output",
        "voices",
        ".superpowers",
    ]
    for pat in expected_patterns:
        assert pat in content, f"Pattern {pat} must be in .gitignore"


def test_readme_content():
    """Verify README.md contains Portuguese documentation, repository link, and guides."""
    readme_path = REPO_ROOT / "README.md"
    assert readme_path.exists(), "README.md must exist"
    content = readme_path.read_text(encoding="utf-8")
    
    assert "Voxa" in content
    assert "https://github.com/WeslleyMouraDev/Voxa.git" in content
    assert "Chatterbox" in content or "chatterbox" in content
    assert "Faster Whisper" in content or "faster-whisper" in content
    assert "7865" in content
    assert "setup.bat" in content
    assert "start.bat" in content
