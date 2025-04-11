# SnipVocab

*my latest, nth attempt to build vvv, this time django+vue*.

## User Stories

|   | Nr | User Story                                                                        |
|---|----|-----------------------------------------------------------------------------------|
| ![User Story 1 illustration](doc/img/us1.png)   | 1  | As a learner, I want to watch and understand interesting Arabic videos from day 1 |
|  ![User Story 2 illustration](doc/img/us2.png)   | 2  | As a learner, I want to learn to communicate in Arabic                            |
| ![User Story 3 illustration](doc/img/us3.png)  | 3  | As a learner, I want to integrate the app into my long-term Arabic study routine  |

## The Project

### Vue Frontend

![screenshot frontend](/doc/img/frontend.png)

- Learner facing web-app, see [documentation](/frontend/README.md)

### CMS

![screenshots cms](/doc/img/cms.png)

- Admin-only (maybe later for translators) "CMS" to decide which videos to translate when and how

### Django REST backend

*...to be documented*

## Running it

### Backend

1. go to `backend/` and activate venv with `source .venv/bin/activate`
2. go to `backend/backend/` and run `python manage.py runserver`

### Frontend

1. go to `frontend/`
2. run `npm run dev`


## Common Things You May Want To Do

### Adding Content

- `http://127.0.0.1:8000/cms/` has everything you want

### Checking Something Regarding Types

- check `frontend/src/shared/types/domainTypes.ts` for frontend stuff
  - although some stuff may have its own internal types, especially `frontend/src/modules/backend-communication/api.ts`
- backend is all about `backend/backend/shared/models.py`
  - however, learning-specific stuff (not yet used) is defined in `backend/backend/learnapi/models.py`



### Deployment

#### Backend


##### Create Fixture

*because you can't call the youtube api from Heroku, thanks Google*

```
python manage.py dumpdata shared --indent 2 > fixture.json
```

...and on heroku

```
heroku run python manage.py loaddata fixture.json
```

##### Rest of Deploy

```
git push heroku main
heroku run python manage.py migrate
```

...and log:


```
heroku logs --tail --app snipvocab-backend
```