from datetime import datetime

import pytest
import sqlalchemy as sa

from sqlalchemy_utils.types import pendulum


@pytest.fixture
def User(Base):
    class User(Base):
        __tablename__ = 'users'
        id = sa.Column(sa.Integer, primary_key=True)
        birthday = sa.Column(pendulum.PendulumType)
    return User


@pytest.fixture
def init_models(User):
    pass


@pytest.mark.skipif('pendulum.pendulum is None')
class TestPendulumDateTimeType(object):

    def test_parameter_processing(self, session, User):
        user = User(
            birthday=pendulum.pendulum.datetime(2000, 11, 1)
        )

        session.add(user)
        session.commit()

        user = session.query(User).first()
        assert user.birthday.datetime

    def test_int_coercion(self, User):
        user = User(
            birthday=1367900664
        )
        assert user.birthday.year == 2013

    def test_string_coercion(self, User):
        user = User(
            birthday='1367900664'
        )
        assert user.birthday.year == 2013

    def test_utc(self, session, User):
        time = pendulum.pendulum.now("UTC")
        user = User(birthday=time)
        session.add(user)
        assert user.birthday == time
        session.commit()
        assert user.birthday == time

    def test_other_tz(self, session, User):
        time = pendulum.pendulum.now("UTC")
        local = time.in_tz('US/Pacific')
        user = User(birthday=local)
        session.add(user)
        assert user.birthday == time == local
        session.commit()
        assert user.birthday == time

    def test_literal_param(self, session, User):
        clause = user.birthday > '2015-01-01'
        compiled = str(clause.compile(compile_kwargs={"literal_binds": True}))
        assert compiled == 'user.birthday > 2015-01-01'
