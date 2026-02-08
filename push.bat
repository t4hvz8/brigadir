#!/bin/bash
# save as create_repo.sh
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/t4hvz8/brigadir.git
git push -u origin main