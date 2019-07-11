from datetime import datetime

import pytest
import sqlalchemy as sa

from sqlalchemy_utils.types import pendulum


@pytest.fixture
def User(Base):
    class User(Base):
        __tablename__ = 'users'
        id = sa.Column(sa.Integer, primary_key=True)
        birthday = sa.Column(pendulum.PendulumDateType)
        created_at = sa.Column(pendulum.PendulumDateTimeType)
    return User


@pytest.fixture
def init_models(User):
    pass


    @pytest.mark.skipif('pendulum.pendulum is None')
    class TestPendulumDateType(object):

        def test_parameter_processing(self, session, User):
            user = User(
                birthday=pendulum.pendulum.date(1995, 7, 11)
            )

            session.add(user)
            session.commit()

            user = session.query(User).first()
            assert user.birthday.date

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
            local = time.in_tz('Asia/Tokyo')
            user = User(birthday=local)
            session.add(user)
            assert user.birthday == time == local
            session.commit()
            assert user.birthday == time

        def test_literal_param(self, session, User):
            clause = User.birthday > '2015-01-01'
            compiled = str(clause.compile(compile_kwargs={"literal_binds": True}))
            assert compiled == 'user.birthday > 2015-01-01'

@pytest.mark.skipif('pendulum.pendulum is None')
class TestPendulumDateTimeType(object):

    def test_parameter_processing(self, session, User):
        user = User(
            created_at=pendulum.pendulum.datetime(1995, 7, 11)
        )

        session.add(user)
        session.commit()

        user = session.query(User).first()
        assert user.created_at.datetime

    def test_int_coercion(self, User):
        user = User(
            created_at=1367900664
        )
        assert user.created_at.year == 2013

    def test_string_coercion(self, User):
        user = User(
            created_at='1367900664'
        )
        assert user.created_at.year == 2013

    def test_utc(self, session, User):
        time = pendulum.pendulum.now("UTC")
        user = User(created_at=time)
        session.add(user)
        assert user.created_at == time
        session.commit()
        assert user.created_at == time

    def test_other_tz(self, session, User):
        time = pendulum.pendulum.now("UTC")
        local = time.in_tz('Asia/Tokyo')
        user = User(created_at=local)
        session.add(user)
        assert user.created_at == time == local
        session.commit()
        assert user.created_at == time

    def test_literal_param(self, session, User):
        clause = User.created_at > '2015-01-01'
        compiled = str(clause.compile(compile_kwargs={"literal_binds": True}))
        assert compiled == 'user.created_at > 2015-01-01'
