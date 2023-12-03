@REM @echo off

@REM if "%1"=="" (
@REM     echo Usage: %0 [update_label] [branch]
@REM     exit /b 1
@REM )

@REM git add .
@REM git commit -m "%1"

@REM if "%2"=="" (
@REM     git push origin main
@REM ) else (
@REM     git push origin "%2"
@REM )

@echo off

if "%~1"=="" (
    echo Usage: %0 "update_label" [branch]
    exit /b 1
)

git add .
git commit -m "%~1"

if "%2"=="" (
    git push origin main
) else (
    git push origin "%2"
)
