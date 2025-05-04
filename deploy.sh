#!/usr/bin/env bash
set -e
# 0) activate virtual environment
source .venv/bin/activate

# 1) dump fixtures and make commit
python manage.py dumpdata shared --indent 2 > fixture.json
git add fixture.json
git commit -m "deploy script: dump updated fixtures" --no-verify || true

# 2) push to germanwithvideos
git push germanwithvideos HEAD:main
heroku run --app germanwithvideos python manage.py migrate
heroku run python manage.py loaddata fixture.json --app germanwithvideos

# 3) push to arabicwithvideos
# not necessary to migrate because db is shared with germanwithvideos
git push arabicwithvideos HEAD:main