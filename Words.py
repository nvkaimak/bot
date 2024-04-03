import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conn import *
from model import *


class Words():
    def __init__(self, id_user):
        self.DSN = f'postgresql://{USER}:{PASSWORD}@localhost:5432/{DATABASE}'
        self.id_user = id_user

    def session(self):
        engine = create_engine(self.DSN)
        Session = sessionmaker(bind=engine)
        return Session()

    def create_start_links(self):
        session = self.session()
        with session:
            existing_user = session.query(User.id_user_telegram).where(User.id_user_telegram == self.id_user).first()
            if existing_user is None:
                new_user = User(id_user_telegram=self.id_user)
                session.add(new_user)
                session.commit()

                for word in range(1, 11):
                    obj = UserWords(id_user=self.id_user, id_word=word)
                    session.add(obj)
                    session.commit()

    def get_words(self):
        session = self.session()
        with session:
            words = session.query(Translator.eng, Translator.rus) \
                .select_from(UserWords) \
                .join(Translator, UserWords.id_word == Translator.id) \
                .filter(UserWords.id_user == self.id_user).all()
            target = random.choice(words)
            words_copy = words[:]
            words_copy.remove(target)
            random.shuffle(words_copy)

            return target.rus, target.eng, [eng.eng for eng in words_copy[:3]]

    def add_word(self, eng, rus):
        session = self.session()
        with session:
            existing_words = session.query(Translator.id).where(Translator.eng == eng).first()
            if existing_words is None:
                words = Translator(eng=eng, rus=rus)
                session.add(words)
                session.commit()

            user_words = UserWords(id_user=self.id_user, id_word=words.id)
            session.add(user_words)
            session.commit()


    #
    def delete_word(self, eng):
        session = self.session()
        existing_words = session.query(Translator.id)\
            .where(Translator.eng == eng)\
            .first()
        flag = 1
        with session:
            if existing_words:
                words = session.query(UserWords) \
                    .select_from(UserWords) \
                    .join(Translator) \
                    .filter(UserWords.id_user == self.id_user) \
                    .filter(Translator.eng == eng) \
                    .first()
                session.delete(words)
                session.commit()

            else:
                flag = 0

        return flag
