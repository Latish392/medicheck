@echo off
title MediCheck — Deploy to GitHub
color 0A

echo.
echo ================================================
echo   MediCheck — GitHub Deployment Setup
echo ================================================
echo.

REM ── Step 1: Check Git ──────────────────────────
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed.
    echo.
    echo Please download and install Git from:
    echo   https://git-scm.com/download/win
    echo.
    echo After installing, re-run this script.
    pause
    exit /b 1
)
echo [OK] Git found.

REM ── Step 2: Ask for GitHub details ─────────────
echo.
set /p GITHUB_USERNAME=Enter your GitHub username: 
set /p REPO_NAME=Enter your new GitHub repo name (e.g. medicheck): 
set /p GIT_EMAIL=Enter your GitHub email: 
set /p GIT_NAME=Enter your name (for commits): 

REM ── Step 3: Configure git ──────────────────────
git config --global user.email "%GIT_EMAIL%"
git config --global user.name "%GIT_NAME%"
echo [OK] Git configured.

REM ── Step 4: Init repo ──────────────────────────
if exist ".git" (
    echo [INFO] Git repo already initialized.
) else (
    git init
    echo [OK] Git repo initialized.
)

REM ── Step 5: Create .gitignore if missing ───────
if not exist ".gitignore" (
    (
        echo __pycache__/
        echo *.pyc
        echo .env
        echo .streamlit/secrets.toml
        echo venv/
        echo .venv/
    ) > .gitignore
    echo [OK] .gitignore created.
)

REM ── Step 6: Stage files ────────────────────────
git add app.py symptom_analyzer.py utils.py requirements.txt README.md .streamlit/config.toml .gitignore
echo [OK] Files staged.

REM ── Step 7: Commit ─────────────────────────────
git commit -m "Initial MediCheck deployment"
echo [OK] Committed.

REM ── Step 8: Set branch to main ─────────────────
git branch -M main

REM ── Step 9: Add remote ─────────────────────────
git remote remove origin >nul 2>&1
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo [OK] Remote set to: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

REM ── Step 10: Push ──────────────────────────────
echo.
echo ================================================
echo  IMPORTANT: GitHub now requires a Personal
echo  Access Token (PAT) instead of a password.
echo.
echo  Get your PAT here:
echo  https://github.com/settings/tokens/new
echo  - Expiration: 90 days
echo  - Scope: check "repo"
echo  Then COPY the token and PASTE it below
echo  when prompted for a password.
echo ================================================
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo  SUCCESS! Your code is on GitHub at:
    echo  https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
    echo  Next: Deploy on Streamlit Cloud
    echo  1. Go to https://share.streamlit.io
    echo  2. Click "New app"
    echo  3. Select repo: %GITHUB_USERNAME%/%REPO_NAME%
    echo  4. Main file: app.py
    echo  5. Click Deploy
    echo  6. Add secret: GEMINI_API_KEY = "your_key"
    echo ================================================
) else (
    echo.
    echo [ERROR] Push failed. Check your PAT and that
    echo the repo exists on GitHub:
    echo https://github.com/new
)

echo.
pause
