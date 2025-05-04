#!/usr/bin/env bash
set -e
# 0) activate virtual environment
source .venv/bin/activate

# 1) dump fixtures and make commit
python manage.py dumpdata shared --indent 2 > fixture.json
git add fixture.json
git commit -m "deploy script: dump updated fixtures" --no-verify

# 2) push to germanwithvideos
git push germanwithvideos HEAD:main
heroku run --app germanwithvideos python manage.py migrate
heroku run --app germanwithvideos python manage.py loaddata fixture.json

# 3) push to arabicwithvideos
# git push arabicwithvideos HEAD:main
# heroku run --app arabicwithvideos python manage.py migrate
# heroku run --app arabicwithvideos python manage.py loaddata fixture.json