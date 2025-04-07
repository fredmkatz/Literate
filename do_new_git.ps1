git init
git remote add origin https://github.com/fredmkatz/Presentable.git
git add .
git commit -m "Initial commit"  
git push -u origin main

git pull origin main --allow-unrelated-histories

git add .
git commit -m "Merge remote changes with local project"
git push -u origin main
