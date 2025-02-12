Bambu Systematic Review
==========================

### Clone repository 
`git clone git@github.com:omixlab/Mabel.git`

### Open folder 
`cd Mabel`

### Docker
`make build`
`make run`

```
CELERY_BROKER_URL=XXXXXXXXXXXXXXXXX
CELERY_RESULT_BACKEND=XXXXXXXXXXXXX
SQLALCHEMY_DATABASE_URI=XXXXXXXXXXX
FLASK_SECRET_KEY=XXXXXXXXXXXXXXXXXX
FLASHTEXT_MODELS='data/flashtext_models/default_models/'
FLASHTEXT_USER_MODELS='data/flashtext_models/users_models/'
UPLOAD_FILES='data/uploads/'
DUMPS_PATH='data/dumps'
```
