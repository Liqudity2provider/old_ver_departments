import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app import app, Base
from app import Departments, Employees


class TestCase(unittest.TestCase):
    app.config['TESTING'] = True
    app.config['CSRF_ENABLED'] = False

    def test_func(self):
        department = Departments(department_name='department_name')
        session.add(department)
        session.commit()
        departments = session.query(Departments)

        assert departments[0] == department

    def test_deleting(self):
        departments = session.query(Departments)

        for i in departments:
            if i.department_name == 'department_name':
                session.delete(i)
                session.commit()
                assert 1 == 1


if __name__ == '__main__':
    engine = create_engine('sqlite:///test.db', echo=False)
    # Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    unittest.main()
    Base.metadata.drop_all(engine)
