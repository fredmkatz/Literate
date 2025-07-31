# Simple GitHub update script for the Literate project

# Get the current branch
$BRANCH = git rev-parse --abbrev-ref HEAD

# Add all changes
Write-Host "Adding all changes..." -ForegroundColor Cyan
git add .

# Prompt for commit message
$COMMIT_MESSAGE = Read-Host -Prompt "Enter commit message"

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Cyan
git commit -m "$COMMIT_MESSAGE"

# Pull any changes from remote
Write-Host "Pulling latest changes from remote..." -ForegroundColor Cyan
git pull origin $BRANCH

# Push changes to remote
Write-Host "Pushing changes to remote..." -ForegroundColor Cyan
git push origin $BRANCH

Write-Host "Done! Repository updated successfully." -ForegroundColor Green
Read-Host -Prompt "Press Enter to exit"