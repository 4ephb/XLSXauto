from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship  # , Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, func, event
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

engine = create_engine('sqlite:///' + os.path.join(basedir, 'db/main.db'))

class Certificates(Base):
    """
    PARENT
    CHILD_1: Designations2
        Одна запись в Certificates может иметь несколько записей в Designations2.
        Связана с моделью Certificates через внешний ключ cert_id.

    CHILD_2: TradeMarks
        Oдна запись в Certificates может иметь несколько записей в TradeMarks.
        Связана с моделью Certificates через внешний ключ cert_id.
    """
    __tablename__ = 'certificates'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # code: Mapped[str] = mapped_column(String, nullable=False)
    # cert_name: Mapped[str] = mapped_column(String, nullable=False)
    # start_date: Mapped[str] = mapped_column(String, nullable=False)
    # exp_date: Mapped[str] = mapped_column(String, nullable=False)
    # children_1: Mapped[List["TradeMarks"]] = relationship("TradeMarks", back_populates="parent")
    # children_2: Mapped[List["Designations2"]] = relationship("Designations2", back_populates="parent")

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    cert_name = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    exp_date = Column(String, nullable=False)
    designations = relationship("Designations2", back_populates="certificate")
    trademarks = relationship("TradeMarks", back_populates="certificate")


class Designations2(Base):
    """
    CHILD_1
    PARENT: Certificates
    Связана с моделью Certificates через внешний ключ cert_id.
    Одна запись в Designations2 может быть связана с одной записью в Certificates.
    Однонаправленная связь - можно получить объект Certificates из объекта Designations2 (не наоборот).
    Связь определена с помощью атрибута certificate, который указывает на объект Certificates, связанный с данной записью Designations2.
    """
    __tablename__ = 'designations_2'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # cert_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'), nullable=False)
    # designation: Mapped[str] = mapped_column(String, nullable=False)
    # hscode: Mapped[str] = mapped_column(String, nullable=False)
    # s_low: Mapped[float] = mapped_column(Float, nullable=False)
    # s_high: Mapped[float] = mapped_column(Float)
    # parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'))
    # parent: Mapped["Certificates"] = relationship(back_populates="designations")

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    cert_id = Column(Integer, ForeignKey('certificates.id'), nullable=False)
    designation = Column(String, nullable=False)
    hscode = Column(String, nullable=False)
    s_low = Column(Float, nullable=False)
    s_high = Column(Float, nullable=False)
    certificate = relationship("Certificates", back_populates="designations")


class TradeMarks(Base):
    """
    CHILD_2
    PARENT: Certificates
    Связана с моделью Certificates через внешний ключ cert_id.
    Одна запись в TradeMarks может быть связана с одной записью в Certificates.
    Однонаправленная связь - можно получить объект Certificates из объекта TradeMarks (не наоборот).
    Связь определена с помощью атрибута certificate, который указывает на объект Certificates, связанный с данной записью TradeMarks.
    """
    __tablename__ = 'trade_marks'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # cert_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'), nullable=False)
    # trade_mark: Mapped[str] = mapped_column(String, nullable=False)
    # manufacturer: Mapped[str] = mapped_column(String)
    # category: Mapped[int] = mapped_column(Integer)
    # parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'))
    # parent: Mapped["Certificates"] = relationship(back_populates="trademarks")

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    cert_id = Column(Integer, ForeignKey('certificates.id'), nullable=False)
    trade_mark = Column(String, nullable=False)
    manufacturer = Column(String)
    category = Column(Integer)
    certificate = relationship("Certificates", back_populates="trademarks")


class Designations1(Base):
    """
    Модель Designations1 не имеет связей с другими моделями.
    """
    __tablename__ = 'designations_1'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # hscode: Mapped[str] = mapped_column(String, nullable=False)
    # designation: Mapped[str] = mapped_column(String, nullable=False)

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    hscode = Column(String, nullable=False)
    designation = Column(String, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # name: Mapped[str] = mapped_column(String, index=True, unique=True)
    # password_hash: Mapped[str] = mapped_column(String(255))

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(name, password):
        user = User(name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # return user

    def __repr__(self):
        return '<User {0}>'.format(self.name)

@event.listens_for(engine, "connect")
def sqlite_connect(dbapi_conn, conn_record):
    dbapi_conn.create_function("stem_porter", 1, stem_porter)
