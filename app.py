from datetime import time, datetime
'''
https://aws.amazon.com/ru/getting-started/hands-on/serve-a-flask-app/?nc1=h_ls
https://www.youtube.com/watch?v=u0oDDZrDz9U
https://flask-service.hj02h9m0bpdcc.eu-west-1.cs.amazonlightsail.com/
'''
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import Session
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, BooleanField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired

app = Flask(__name__)

engine = create_engine('sqlite:///new_db.db', echo=False)
Base = declarative_base()


class Departments(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    department_name = Column(String, nullable=False)
    employees = relationship("Employees", backref="departments")

    def __repr__(self):
        return str(self.department_name)


class Employees(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    salary = Column(Integer, nullable=False, index=True)
    date_of_birth = Column(String, nullable=False, index=True)
    departments_id = Column(Integer, ForeignKey('departments.id'))

    def __repr__(self):
        return str(self.name)


Base.metadata.create_all(engine)


@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        Session = sessionmaker(bind=engine)
        session = Session()
        department_name = request.form['department_name']
        department = Departments(department_name=department_name)
        try:
            session.add(department)
            session.commit()
            flash('New department was added', 'add')
            return redirect('/departments')
        except Exception:
            return 'оишбка'
    else:
        return render_template('add_department.html')


import os

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


def choise_list():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(Departments)


class ChoiceForm(FlaskForm):
    opts = QuerySelectField(query_factory=choise_list, allow_blank=True, get_label='department_name')


@app.route("/", methods=['GET', 'POST'])
def test():
    return departments()


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    form = ChoiceForm()
    if request.method == 'POST':
        Session = sessionmaker(bind=engine)
        session = Session()
        employee_name = request.form['employee_name']
        employee_salary = request.form['employee_salary']
        employee_date_birth = request.form['employee_date_birth']
        employee_department_id = int(str(form.opts.data.id))

        employee = Employees(name=employee_name, salary=employee_salary, date_of_birth=employee_date_birth,
                             departments_id=employee_department_id)
        print(employee)
        try:
            session.add(employee)
            session.commit()
            flash('New employee was added', 'add')
            print('успшно добавили работника')
            return redirect('/employees')
        except Exception:
            return 'ошибка при добавлении работника'
    else:
        return render_template('add_employee.html', form=form)


@app.route('/departments')
def departments():
    Session = sessionmaker(bind=engine)
    session = Session()
    departments = session.query(Departments)

    dict_sum = {}

    for department in departments:
        temp_sum = 0
        if len(department.employees):
            for emp in department.employees:
                temp_sum += emp.salary
            dict_sum.update({department.id: temp_sum / len(department.employees)})
        else:
            dict_sum.update({department.id: 0})
    return render_template('departments.html', departments=departments, dict_sum=dict_sum)


@app.route('/employees')
def employees():
    Session = sessionmaker(bind=engine)
    session = Session()
    employees = session.query(Employees)
    departments = session.query(Departments)
    l_dep = {}
    for department in departments:
        l_dep.update({department.id: department.department_name})
    print(l_dep)
    return render_template('employees.html', employees=employees, departments=l_dep)


@app.route('/employee/<int:id>')
def employee_detail(id):
    Session = sessionmaker(bind=engine)
    session = Session()
    employee = session.query(Employees).get(id)
    dep_id = employee.departments_id
    print(dep_id)
    department = session.query(Departments).get(employee.departments_id)
    return render_template('employee_detail.html', employee=employee, department=department)


@app.route('/department/<int:id>')
def department_detail(id):
    Session = sessionmaker(bind=engine)
    session = Session()
    department = session.query(Departments).get(id)
    average_salary = 0
    total_department_salary = 0
    employees_quantity = 0
    if len(department.employees):
        for emp in department.employees:
            total_department_salary += emp.salary
        average_salary = total_department_salary / len(department.employees)
        employees_quantity = len(department.employees)
    return render_template('department_detail.html', department=department, average_salary=average_salary,
                           employees_quantity=employees_quantity, total_department_salary=total_department_salary)


@app.route('/department/<int:id>/delete')
def department_delete(id):
    Session = sessionmaker(bind=engine)
    session = Session()
    depatment = session.query(Departments).get(id)
    try:
        session.delete(depatment)
        session.commit()
        flash('Department removed', 'delete')
        return redirect('/departments')
    except:
        return 'ошибка при удалении статьи'


@app.route('/department/<int:id>/update', methods=['GET', 'POST'])
def department_update(id):
    Session = sessionmaker(bind=engine)
    session = Session()
    depatment = session.query(Departments).get(id)
    department_name = depatment.department_name
    if request.method == 'POST':
        depatment.department_name = request.form['department_name']
        try:
            session.commit()
            flash('Department updated', 'add')

            return redirect('/departments')
        except Exception:
            return 'оишбка'
    else:
        return render_template('add_department.html', department_name=department_name)


@app.route('/employee/<int:id>/delete')
def employee_delete(id):
    form = ChoiceForm()

    Session = sessionmaker(bind=engine)
    session = Session()
    employee = session.query(Employees).get(id)
    try:
        session.delete(employee)
        session.commit()
        flash('Employee removed', 'delete')
        return redirect('/employees')
    except:
        return 'ошибка при удалении статьи'


@app.route('/employee/<int:id>/update', methods=['GET', 'POST'])
def employee_update(id):
    form = ChoiceForm()

    Session = sessionmaker(bind=engine)
    session = Session()
    employee = session.query(Employees).get(id)
    value_name = employee.name
    value_salary = employee.salary
    value_date_birth = employee.date_of_birth
    if request.method == 'POST':
        employee.name = request.form['employee_name']
        employee.salary = request.form['employee_salary']
        employee.date_of_birth = request.form['employee_date_birth']
        employee.departments_id = int(str(form.opts.data.id))

        try:
            session.commit()
            flash('Employee updated', 'add')
            return redirect('/employees')
        except Exception:
            return 'оишбка'
    else:
        return render_template('add_employee.html', form=form, value_name=value_name, value_salary=value_salary,
                               value_date_birth=value_date_birth)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
