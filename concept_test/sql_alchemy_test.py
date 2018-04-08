from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import code


engine = create_engine('sqlite:///:memory:', echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)


Base.metadata.create_all(engine)

ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
session.add(ed_user)
session.add_all([
    User(name='ed1', fullname='Ed Jones 1', password='edspassword'),
    User(name='ed2', fullname='Ed Jones 2', password='edspassword'),
    User(name='ed3', fullname='Ed Jones 3', password='edspassword'),
])

# our_user = session.query(User).filter_by(name='ed').first()

# print(repr(our_user))
code.interact(local=locals())
