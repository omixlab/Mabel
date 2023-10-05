# Para a aplicação em flask funcionar é necessário rodar 
# cada um desses comando em um terminal diferente

flask --app src run --debugger  

celery -A src.celery worker --loglevel=info

redis-server

# Create db
from src import app
from src import db 
app.app_context().push()
db.create_all()
