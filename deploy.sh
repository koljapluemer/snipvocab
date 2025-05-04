#!/usr/bin/env bash
set -e

# Parse command line arguments
NO_FIXTURE=false
for arg in "$@"; do
    case $arg in
        --no-fixture)
            NO_FIXTURE=true
            shift
            ;;
    esac
done

# 0) activate virtual environment
source .venv/bin/activate

# 1) dump fixtures and make commit (only if --no-fixture is not provided)
if [ "$NO_FIXTURE" = false ]; then
    python manage.py dumpdata shared --indent 2 > fixture.json
    git add fixture.json
    git commit -m "deploy script: dump updated fixtures" --no-verify || true
fi

# 2) push to germanwithvideos
git push germanwithvideos HEAD:main
heroku run --app germanwithvideos python manage.py migrate
if [ "$NO_FIXTURE" = false ]; then
    heroku run python manage.py loaddata fixture.json --app germanwithvideos
fi

# 3) push to arabicwithvideos
# not necessary to migrate because db is shared with germanwithvideos
git push arabicwithvideos HEAD:main