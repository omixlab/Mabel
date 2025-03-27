from src import app, db
from src.models import FlashtextModels
import datetime

with app.app_context():

    flastext_model = FlashtextModels()
    flastext_model.user_id = 1
    flastext_modelcreated_date = datetime.datetime.utcnow()
    flastext_model.name = 'Human genes'
    flastext_model.type = 'GENE_OR_GENE_PRODUCT'
    flastext_model.path = 'data/flashtext_models/default_models/genes_human.pickle'

    db.session.add(flastext_model)
    db.session.commit()