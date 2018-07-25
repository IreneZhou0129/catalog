# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()
engine = create_engine('sqlite:///catalog.db')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    items = relationship("Item", cascade="all, delete-orphan")

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }


class Item(Base):
    __tablename__ = 'item'

    # properties
    item_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))

    # categroical relationship
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    # related user who created the item
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        }


Base.metadata.create_all(engine)
print("Creating all of the table")
