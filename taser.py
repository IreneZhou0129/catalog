# -*- coding: utf-8 -*-

'''Data preprocessing for inserting fixture into database '''

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import Category, Item, User


engine = create_engine('sqlite:///catalog.db')

DBSession = sessionmaker(bind=engine)

# clear the database before all of the insert
session = DBSession()
session.query(User).delete()
session.query(Item).delete()
session.query(Category).delete()

user1 = User(name="Tyler", email="tyler130@gmail.com")
session.add(user1)
session.commit()

user2 = User(name="Irene", email="Irene34@gmail.com")
session.add(user2)
session.commit()

user3 = User(name="Rock  Liang", email="locartrock@gmail.com")
session.add(user2)
session.commit()

category1 = Category(name="Dining Room", user_id=user1.id)
session.add(category1)
session.commit()

category2 = Category(name="Bath Room", user_id=user2.id)
session.add(category2)
session.commit()

# Inserting Item for category1
item1 = Item(user_id=user1.id, name="Dining tables",
             description="""Table with a top layer of solid wood,
                     good environment choice.""",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=user1.id, name="Dining chairs",
             description="""Solid pine is a natural material which ages
                        beautifully and gains its own unique character over time.""",
             category=category1)
session.add(item2)
session.commit()

item3 = Item(user_id=user2.id, name="Bar stoofs",
             description="Footrest for extra sitting comfort.",
             category=category1)

session.add(item3)
session.commit()

item4 = Item(user_id=user1.id, name="Dining Storage",
             description="""Adjustable shelves, so you can customize
                 your storage as needed. """,
             category=category1)
session.add(item4)
session.commit()

item5 = Item(user_id=user2.id, name="Junior Chair",
             description="""Gives the right seat height for the child
                    at the dining table. (For children 3 years or older)""",
             category=category1)
session.add(item5)
session.commit()

# Inserting Items for category2
item1 = Item(user_id=user1.id, name="Bathroom Mirror ",
             description="""The mirror comes with safety film on the back,
                    which reduces the risk of injury if the glass is broken""",
             category=category2)
session.add(item1)
session.commit()

item2 = Item(user_id=user2.id, name="Bathroom Lighting",
             description="""Gives a diffused light which is good for
                    spreading light into larger areas of a bathroom""",
             category=category2)
session.add(item2)
session.commit()

item3 = Item(
    user_id=user1.id,
    name="Sink Cabinets",
    description="""Laminate countertops are highly durable and easy to maintain.
                    A little care will keep them looking brand new for years""",
    category=category2)
session.add(item3)
session.commit()

print("Inserting fixtures into database")
