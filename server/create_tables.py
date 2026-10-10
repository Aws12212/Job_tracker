from database import Base, engine
import models  # registers the models with Base

Base.metadata.create_all(engine)
print("Tables created")