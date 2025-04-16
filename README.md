# SnipVocab


*my latest, nth attempt to build vvv, this time django+vue*.

- [SnipVocab](#snipvocab)
  - [User Stories](#user-stories)
  - [Architecture](#architecture)
    - [Vue Frontend](#vue-frontend)
    - [CMS](#cms)
    - [Django REST backend](#django-rest-backend)
  - [Running it](#running-it)
    - [Backend](#backend)
    - [Frontend](#frontend)
  - [Common Things You May Want To Do](#common-things-you-may-want-to-do)
    - [Adding Content](#adding-content)
    - [Checking Something Regarding Types](#checking-something-regarding-types)
    - [Deployment](#deployment)
      - [Backend](#backend-1)
        - [Create Fixture](#create-fixture)
        - [Rest of Deploy](#rest-of-deploy)
        - [Notes for Deployment](#notes-for-deployment)
  - [Testing](#testing)
    - [Backend](#backend-2)
    - [Frontend](#frontend-1)


## User Stories

|   | Nr | User Story                                                                        |
|---|----|-----------------------------------------------------------------------------------|
| ![User Story 1 illustration](doc/img/us1.png)   | 1  | As a learner, I want to watch and understand interesting Arabic videos from day 1 |
|  ![User Story 2 illustration](doc/img/us2.png)   | 2  | As a learner, I want to learn to communicate in Arabic                            |
| ![User Story 3 illustration](doc/img/us3.png)  | 3  | As a learner, I want to integrate the app into my long-term Arabic study routine  |

## Architecture

```
./
├── backend                                         # This is the actual Django backend, mostly utilizing the Django REST framework.
│   ├── authapi                                     # A Django REST API responsible for basic auth functionality: login, logout, register.
│   │   ├── migrations
│   ├── backend                                     # The automatic sub-app Django always creates.
│   ├── cms                                         # Content management system for me, the admin, to add and maintain youtube videos, words, meanings etc.
│   │   ├── migrations
│   │   ├── templates
│   │   │   ├── includes
│   ├── learnapi                                    # Handles everything to do with learning, videos, snippets, words — on the backend.
│   │   ├── migrations
│   │   ├── views
│   │   │   ├── learning_events
│   │   │   ├── snippet_interaction                 # Everything needed to interact with a singular snippet.
│   │   │   ├── tags
│   │   │   ├── utils
│   │   │   ├── video_list
│   │   │   ├── video_view                          # Everything regarding displaying one or more videos.
│   ├── payment
│   │   ├── migrations
│   ├── shared                                      # holds the models such as `Video` and `Snippet`, which are needed when learners use the app (`learnapi`) but ofc also when adding/maintaining content from an admin perspective (`cms`).
│   │   ├── migrations
│   ├── static
│   ├── staticfiles
├── doc
│   ├── img
│   └── readmes
├── frontend                                        # The learner-facing website, implemented in Vue3/ts/vite/tailwind/daisy.
│   ├── public
│   ├── src
│   │   ├── composables
│   │   ├── directives
│   │   ├── modules
│   │   │   ├── auth
│   │   │   │   ├── login
│   │   │   │   ├── logout
│   │   │   │   ├── register
│   │   │   │   └── show-user
│   │   │   ├── backend-communication
│   │   │   ├── learning-and-spaced-repetition
│   │   │   ├── pages
│   │   │   │   ├── dashboard
│   │   │   │   └── profile
│   │   │   ├── payment
│   │   │   └── videos
│   │   │       ├── video-list
│   │   │       └── view-video
│   │   │           ├── components
│   │   │           │   ├── __tests__
│   │   │           │   │   └── VideoCard.test.ts   # per module test example
│   │   │           └── view-snippet
│   │   │               ├── modes
│   │   ├── shared
│   │   │   ├── elements
│   │   │   │   └── toast
│   │   │   ├── types
│   │   │   └── utils
```

### Vue Frontend

![screenshot frontend](/doc/img/frontend.png)

- Learner facing web-app, see [documentation](/frontend/README.md)

### CMS

![screenshots cms](/doc/img/cms.png)

- Admin-only (maybe later for translators) "CMS" to decide which videos to translate when and how
- requires a `superuser` to exist, and needs auth as such

### Django REST backend

*...to be documented*

## Running it

### Backend

1. go to `backend/` and activate venv with `source .venv/bin/activate`
2. go to `backend/backend/` and run `python manage.py runserver`

- if you want to do Stripe things, run `stripe listen --forward-to http://localhost:8000/api/payment/webhook/` and make sure the secret is correctly reflected in the local `backend/.env`s

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

##### Notes for Deployment

1. first, add all .env vars from both frontend and backend
2. kind of need domain first
3. ...because we need to create a webhook in stripe where hardcode the domain 

## Testing

### Backend

Running tests:
```
python manage.py test
```
To see how to add tests, check `backend/learnapi/views/learning_events/tests.py` as an example. Note the required `__init__.py` file in the folder.

### Frontend

```
npm test
```

To see an example: `frontend/src/modules/videos/view-video/components/__tests__/VideoCard.test.ts`