@echo off

if "%1"=="" (
    echo Usage: %0 [update_label] [branch]
    exit /b 1
)

git add .
git commit -m "%1"

if "%2"=="" (
    git push origin main
) else (
    git push origin "%2"
)
