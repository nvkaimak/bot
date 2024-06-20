import random

from decorators import session_decorator
from model import *


class Words:
        def __init__(self, id_user):
            self.id_user = id_user

        @session_decorator
        def create_start_links(self, session):
            existing_user = session.query(User.id_user_telegram).where(User.id_user_telegram == self.id_user).first()
            if existing_user is None:
                new_user = User(id_user_telegram=self.id_user)
                session.add(new_user)
                session.commit()

                for word in range(1, 11):
                    obj = UserWords(id_user=self.id_user, id_word=word)
                    session.add(obj)
                    session.commit()

        @session_decorator
        def get_words(self, session):
            words = session.query(Translator.eng, Translator.rus) \
                .select_from(UserWords) \
                .join(Translator, UserWords.id_word == Translator.id) \
                .filter(UserWords.id_user == self.id_user).all()
            target = random.choice(words)
            words_copy = words[:]
            words_copy.remove(target)
            random.shuffle(words_copy)
            return target.rus, target.eng, [eng.eng for eng in words_copy[:3]]

        @session_decorator
        def add_word(self, session, eng, rus):
            existing_words = session.query(Translator.id).where(Translator.eng == eng).first()
            if existing_words is None:
                words = Translator(eng=eng, rus=rus)
                session.add(words)
                session.commit()
            else:
                words = existing_words

            user_words = UserWords(id_user=self.id_user, id_word=words.id)
            session.add(user_words)
            session.commit()

        @session_decorator
        def delete_word(self, session, eng):
            word = session.query(Translator).filter_by(eng=eng).first()
            if word:
                user_word = session.query(UserWords) \
                    .filter(UserWords.id_user == self.id_user, UserWords.id_word == word.id) \
                    .first()
                if user_word:
                    session.delete(user_word)
                    session.commit()
                    return f"Слово '{eng}' успешно удалено."
                else:
                    return f"Слово '{eng}' не найдено у вас в карточках."
            else:
                return f"Слово '{eng}' не найдено в базе данных."


class AddWords():
    def __init__(self):
        self.common_words_data = [
            {'eng': 'red', 'rus': 'красный'},
            {'eng': 'blue', 'rus': 'синий'},
            {'eng': 'green', 'rus': 'зеленый'},
            {'eng': 'yellow', 'rus': 'желтый'},
            {'eng': 'white', 'rus': 'белый'},
            {'eng': 'black', 'rus': 'черный'},
            {'eng': 'I', 'rus': 'я'},
            {'eng': 'you', 'rus': 'ты'},
            {'eng': 'he', 'rus': 'он'},
            {'eng': 'she', 'rus': 'она'}
        ]


    @session_decorator
    def add_words(self, session):
        translator_objects = [Translator(**word_data) for word_data in self.common_words_data]
        session.bulk_save_objects(translator_objects)
        session.commit()
