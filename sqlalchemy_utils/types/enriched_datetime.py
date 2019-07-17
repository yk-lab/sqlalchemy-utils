from __future__ import absolute_import

import six
from sqlalchemy import types

from ..exceptions import ImproperlyConfigured
from .scalar_coercible import ScalarCoercible

arrow = None
try:
    import arrow
except ImportError:
    pass

pendulum = None
try:
    import pendulum
except ImportError:
    pass


class EnrichedDateTimeType(types.TypeDecorator, ScalarCoercible):
    """
    Pendulum and arrow support.

    Example::


        from sqlalchemy_utils import EnrichedDateType
        import pendulum


        class User(Base):
            __tablename__ = 'user'
            id = sa.Column(sa.Integer, primary_key=True)
            created_at = sa.Column(EnrichedDateTimeType(type="pendulum"))
            # created_at = sa.Column(EnrichedDateTimeType(type="arrow"))


        user = User()
        user.created_at = pendulum.now()
        session.add(user)
        session.commit()
    """
    impl = types.DateTime

    def __init__(self, type="pendulum", *args, **kwargs):
        self.type = type
        if type == "pendulum":
            if not pendulum:
                raise ImproperlyConfigured(
                    "'pendulum' package is required to use 'EnrichedDateTimeType'"
                )
        elif type == "arrow":
            if not arrow:
                raise ImproperlyConfigured(
                    "'arrow' package is required to use 'EnrichedDateTimeType'"
                )

        super(EnrichedDateType, self).__init__(*args, **kwargs)

    @staticmethod
    def _coerce(value):
        if value is not None and self.type == "pendulum":
            if isinstance(value, pendulum.DateTime):
                pass
            elif isinstance(value, int):
                value = pendulum.from_timestamp(value)
            elif isinstance(value, six.string_types) and value.isdigit():
                value = pendulum.from_timestamp(int(value))
            else:
                value = pendulum.parse(value)
        elif value is not None and self.type == "arrow":
            if isinstance(value, six.string_types):
                value = arrow.get(value)
            elif isinstance(value, Iterable):
                value = arrow.get(*value)
            elif isinstance(value, datetime):
                value = arrow.get(value)
        return value

    def process_bind_param(self, value, dialect):
        if value:
            if self.type == "pendulum":
                return self._coerce(value).in_tz("UTC")
            elif self.type == "arrow":
                utc_val = self._coerce(value).to('UTC')
                return utc_val.datetime if self.impl.timezone else utc_val.naive
        return value

    def process_result_value(self, value, dialect):
        if value:
            if self.type == "pendulum":
                return pendulum.parse(value.isoformat())
            elif self.type == "arrow":
                return arrow.get(value)
        return value

    def process_literal_param(self, value, dialect):
        return str(value)

    @property
    def python_type(self):
        return self.impl.type.python_type


class EnrichedDateType(EnrichedDateTimeType):
    """
    Pendulum support only.

    Example::


        from sqlalchemy_utils import EnrichedDateType
        import pendulum


        class User(Base):
            __tablename__ = 'user'
            id = sa.Column(sa.Integer, primary_key=True)
            birthday = sa.Column(EnrichedDateType(type="pendulum"))  # not supported arrow


        user = User()
        user.birthday = pendulum.datetime(year=1995, month=7, day=11)
        session.add(user)
        session.commit()
    """
    impl = types.Date

    def __init__(self, type="pendulum", *args, **kwargs):
        self.type = type
        super(PendulumDateType, self).__init__(*args, **kwargs)

    @staticmethod
    def _coerce(value):
        value = PendulumDateType._coerce(value)
        if value:
            if self.type == "pendulum":
                if isinstance(value, pendulum.DateTime):
                    value = value.date()
        return value

    def process_result_value(self, value, dialect):
        if value:
            if self.type == "pendulum":
                return pendulum.parse(value.isoformat()).date()
        return value
