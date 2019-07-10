from sqlalchemy import types
from .scalar_coercible import ScalarCoercible

pendulum = None
try:
    import pendulum
except ImportError:
    pass


class PendulumType(types.TypeDecorator, ScalarCoercible):
    """
    Pendulum support.

    Example::


        from sqlalchemy_utils import PendulumType
        import pendulum


        class User(Base):
            __tablename__ = 'user'
            id = sa.Column(sa.Integer, primary_key=True)
            birthday = sa.Column(PendulumType)


        user = User()
        user.birthday = pendulum.datetime(year=1995, month=7, day=11)
        session.add(user)
        session.commit()
    """
    impl = types.DateTime

    def __init__(self, *args, **kwargs):
        if not pendulum:
            raise ImproperlyConfigured(
                "'pendulum' package is required to use 'PendulumType'"
            )

        super(PendulumType, self).__init__(*args, **kwargs)

    @staticmethod
    def _coerce(value):
        if value and not isinstance(value, pendulum.datetime.DateTime):
            value = pendulum.parse(value)
        return value

    def process_bind_param(self, value, dialect):
        if value:
            return self._coerce(value)
        return value

    def process_result_value(self, value, dialect):
        if value:
            return pendulum.parse(value)
        return value

    def process_literal_param(self, value, dialect):
        return str(value)

    @property
    def python_type(self):
        return self.impl.type.python_type
