from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship

Base = declarative_base()


class Translator(Base):
    __tablename__ = "english_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    eng: Mapped[str] = mapped_column(String(100), unique=True, primary_key=False)
    rus: Mapped[str] = mapped_column(String(100), unique=True, primary_key=False)


class User(Base):
    __tablename__ = "user"

    id_user_telegram: Mapped[int] = mapped_column(unique=True, primary_key=True, autoincrement=False)


class UserWords(Base):
    __tablename__ = "user_words"

    id_user: Mapped[int] = mapped_column(ForeignKey("user.id_user_telegram"))
    id_word: Mapped[str] = mapped_column(ForeignKey("english_words.id"))

    user = relationship(User, backref="user_words")
    word = relationship(Translator, backref="user_words")

    id: Mapped[int] = mapped_column(primary_key=True)
