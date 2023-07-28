# Para a aplicação em flask funcionar é necessário rodar 
# cada um desses comando em um terminal diferente

flask --app src run --debugger  

celery -A src.celery worker --loglevel=info

redis-server


