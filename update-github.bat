@echo off
:: Simple GitHub update script for the Presentable project

:: Get the current branch
for /f "tokens=*" %%a in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%a

:: Add all changes
echo Adding all changes...
git add .

:: Prompt for commit message
set /p COMMIT_MESSAGE=Enter commit message: 

:: Commit changes
echo Committing changes...
git commit -m "%COMMIT_MESSAGE%"

:: Pull any changes from remote
echo Pulling latest changes from remote...
git pull origin %BRANCH%

:: Push changes to remote
echo Pushing changes to remote...
git push origin %BRANCH%

echo Done! Repository updated successfully.
pause