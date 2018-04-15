from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

import code

engine = create_engine('sqlite:///:memory:', echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


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


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address


User.addresses = relationship(
    "Address", order_by=Address.id, back_populates="user")

# session.commit()
# print(repr(our_user))
Base.metadata.create_all(engine)
code.interact(local=locals())
