import sys
import sqlite3
import re
from PyQt5.QtWidgets import QMessageBox
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, \
    QTextEdit, QScrollArea, QComboBox


class RegistrationWindow(PyQt5.QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.register_button = PyQt5.QtWidgets.QPushButton('Зарегистрироваться')
        self.mail_input = PyQt5.QtWidgets.QLineEdit()
        self.mail_label = PyQt5.QtWidgets.QLabel('Введите логин (почту):')
        self.password_input = PyQt5.QtWidgets.QLineEdit()
        self.password_label = PyQt5.QtWidgets.QLabel('Введите безопасный пароль:')
        self.nickname_input = PyQt5.QtWidgets.QLineEdit()
        self.nickname_label = PyQt5.QtWidgets.QLabel('Введите желаемый никнейм:')
        self.surname_input = PyQt5.QtWidgets.QLineEdit()
        self.surname_label = PyQt5.QtWidgets.QLabel('Введите фамилию:')
        self.name_input = PyQt5.QtWidgets.QLineEdit()
        self.name_label = PyQt5.QtWidgets.QLabel('Введите имя:')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Регистрация')
        self.setGeometry(730, 550, 400, 200)
        self.register_button.clicked.connect(self.register_user)
        layout = PyQt5.QtWidgets.QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.surname_label)
        layout.addWidget(self.surname_input)
        layout.addWidget(self.nickname_label)
        layout.addWidget(self.nickname_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.mail_label)
        layout.addWidget(self.mail_input)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register_user(self):
        name = self.name_input.text()
        surname = self.surname_input.text()
        nickname = self.nickname_input.text()
        password = self.password_input.text()
        mail = self.mail_input.text()
        if not name or not surname:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Имя и фамилия должны быть заполнены')
            return
        if name != name.capitalize() or surname != surname.capitalize():
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Имя и фамилия должны начинаться с заглавной буквы')
            return
        if len(password) < 8:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Пароль слишком короткий')
            return
        if re.search(r'\d', password) is None or re.search(r'[A-Z]', password) is None:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка',
                                                 'Пароль должен содержать хотя бы одну цифру и одну заглавную букву')
            return
        if not nickname:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Никнейм должен быть заполнен')
            return
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('SELECT nickname FROM Users WHERE nickname = ?', (nickname,))
        already_exist_nickname = cursor.fetchone()
        connection.close()
        if already_exist_nickname:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка',
                                                 'В базе данных уже есть пользователь с введенным никнеймом')
            return

        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('SELECT mail FROM Users WHERE mail = ?', (mail,))
        already_exist_mail = cursor.fetchone()
        connection.close()
        if already_exist_mail:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Данный никнейм уже есть в базе')
            return

        if not mail or not re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+', mail):
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Почта введена некорректно')
            return
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Users (name, surname, nickname, password, mail) VALUES (?, ?, ?, ?, ?)',
                       (name, surname, nickname, password, mail))
        connection.commit()
        connection.close()
        PyQt5.QtWidgets.QMessageBox.information(self, 'Успешно', 'Пользователь успешно зарегистрирован')
        self.close()
        self.name_input.clear()
        self.surname_input.clear()
        self.nickname_input.clear()
        self.mail_input.clear()
        self.password_input.clear()


class AuthorizationWindow(PyQt5.QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.login_button = PyQt5.QtWidgets.QPushButton('Войти')
        self.password_input = PyQt5.QtWidgets.QLineEdit()
        self.password_label = PyQt5.QtWidgets.QLabel('Введите пароль:')
        self.mail_input = PyQt5.QtWidgets.QLineEdit()
        self.mail_label = PyQt5.QtWidgets.QLabel('Введите почту:')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Авторизация')
        self.setGeometry(730, 600, 400, 200)
        self.password_input.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.login_button.clicked.connect(self.login_user)
        layout = PyQt5.QtWidgets.QVBoxLayout()
        layout.addWidget(self.mail_label)
        layout.addWidget(self.mail_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def login_user(self):
        mail = self.mail_input.text()
        password = self.password_input.text()
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('SELECT password FROM Users WHERE mail = ?', (mail,))
        db_password = cursor.fetchone()
        connection.close()
        if db_password and password == db_password[0]:
            self.main_window.set_user_login(mail)
            PyQt5.QtWidgets.QMessageBox.information(self, 'Успешно', 'Пользователь успешно авторизован')
            text = self.main_window.user_activity_label1.text()
            if text:
                text += '\n'
            self.main_window.user_activity_label1.setText(text + f'{mail} вошел в аккаунт')
            self.close()
            self.mail_input.clear()
            self.password_input.clear()
            self.main_window.comments_text_edit.setVisible(True)
            self.main_window.send_button.setVisible(True)
            self.main_window.clear_button.setVisible(True)
            self.main_window.logout_button.setVisible(True)
            self.main_window.user_activity_label.setVisible(True)
            self.main_window.registration_button.setVisible(False)
            self.main_window.authorization_button.setVisible(False)
            self.main_window.event1_button.setVisible(True)
            self.main_window.event2_button.setVisible(True)
            self.main_window.user_activity_label1.setVisible(True)
            connection = sqlite3.connect('library.db')
            cursor = connection.cursor()
            cursor.execute('SELECT meet FROM Meets WHERE login = ?', (mail,))
            meets = cursor.fetchall()
            connection.commit()
            cursor.execute('SELECT place FROM Meets WHERE login = ? AND meet = ?', (mail, 1))
            place1 = cursor.fetchall()
            connection.commit()
            cursor.execute('SELECT place FROM Meets WHERE login = ? AND meet = ?', (mail, 2))
            place2 = cursor.fetchall()
            connection.close()
            if len(meets) == 2:
                self.main_window.event1_button.setVisible(False)
                self.main_window.event2_button.setVisible(False)
                self.main_window.out1_button.setVisible(True)
                self.main_window.out2_button.setVisible(True)
                PyQt5.QtWidgets.QMessageBox.information(self, 'Напоминание', 'Вы записаны 2 мероприятия\n'
                                                                             f'Мероприятие 1 в библиотеке {place1[0][0]}\n'
                                                                             f'Мероприятие 2 в библиотеке {place2[0][0]}\n')
            elif len(meets) == 1:
                if meets[0][0] == 1:
                    self.main_window.event1_button.setVisible(False)
                    self.main_window.event2_button.setVisible(True)
                    self.main_window.out1_button.setVisible(True)
                    self.main_window.out2_button.setVisible(False)
                    PyQt5.QtWidgets.QMessageBox.information(self, 'Напоминание',
                                                            f'Вы записаны мероприятие 1 в библиотеку {place1[0][0]}')
                elif meets[0][0] == 2:
                    self.main_window.event1_button.setVisible(True)
                    self.main_window.event2_button.setVisible(False)
                    self.main_window.out1_button.setVisible(False)
                    self.main_window.out2_button.setVisible(True)
                    PyQt5.QtWidgets.QMessageBox.information(self,
                                                            'Напоминание', f'Вы записаны мероприятие 2 в библиотеку {place2[0][0]}')

        else:
            PyQt5.QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Вы ввели неверные данные')


class MainWindow(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.registration_window = RegistrationWindow()
        self.authorization_window = AuthorizationWindow(self)
        self.header_label = QLabel("Личный кабинет пользователя сети библиотек города")
        self.header_label.setStyleSheet("font-size: 25px")
        self.login_label = QLabel("Логин: Гость")
        self.login_label.setStyleSheet("font-size: 20px")
        self.registration_button = PyQt5.QtWidgets.QPushButton('Регистрация')
        self.registration_button.setStyleSheet("font-size: 20px")
        self.authorization_button = PyQt5.QtWidgets.QPushButton('Авторизация')
        self.authorization_button.setStyleSheet("font-size: 20px")
        self.logout_button = QPushButton('Выйти из аккаунта')
        self.logout_button.setStyleSheet("font-size: 20px")
        self.logout_button.setVisible(False)
        self.dropdown_list = QComboBox()
        self.login_mail = ''
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Интерфейс личного кабинета библиотеки')
        self.setGeometry(400, 200, 1100, 700)
        self.registration_button.clicked.connect(self.show_registration)
        self.authorization_button.clicked.connect(self.show_authorization)
        self.logout_button.clicked.connect(self.logout_user)
        layout = PyQt5.QtWidgets.QVBoxLayout()
        layout.addWidget(self.header_label)
        layout.addWidget(self.login_label)
        layout.addWidget(self.logout_button)
        layout.addWidget(self.registration_button)
        layout.addWidget(self.authorization_button)
        container = PyQt5.QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        news_and_poster_container = QWidget()
        news_and_poster_layout = QHBoxLayout(news_and_poster_container)
        news_block = QWidget()
        news_block.setObjectName("Block1")
        news_block.setStyleSheet("background-color: #D6DBDF")
        news_block_layout = QVBoxLayout(news_block)
        news_label = QLabel("<u>Новости<u><br>")
        news_label.setStyleSheet("font-size: 25px")
        news_text1 = QLabel("• В ближайшее время в библиотеках будут <br> проведены мероприятия"
                            " - ознакомиться<br> вы можете в блоке 'Афиша.'<br>")
        news_text2 = QLabel("• В библотеке 2 будет проведено <br>техническое обслуживание ПК.<br>"
                            "Если Вы нуждаетесь в ПО оповестите<br> об этом при помощи комментария.<br>")
        news_text3 = QLabel("• В библиотеке 1 будет проведен<br> капитальный ремонт.")
        news_block_layout.addWidget(news_label)
        news_block_layout.addWidget(news_text1)
        news_block_layout.addWidget(news_text2)
        news_block_layout.addWidget(news_text3)
        news_text1.setStyleSheet("font-size: 20px")
        news_text2.setStyleSheet("font-size: 20px")
        news_text3.setStyleSheet("font-size: 20px")
        poster_block = QWidget()
        poster_block.setObjectName("Block2")
        poster_block_layout = QVBoxLayout(poster_block)
        poster_block.setStyleSheet("background-color: #D6DBDF")
        poster_label = QLabel("<u>Афиша<u><br>")
        poster_label.setStyleSheet("font-size: 25px")
        mettup1 = QLabel("<b>Мероприятие 1:</b> Всемирный день поэзии")
        mettup1.setStyleSheet("font-size: 20px")
        event1_button = QPushButton('Записаться на мероприятие 1')
        mettup2 = QLabel("<b>Мероприятие 2:</b> Безопасность данных")
        mettup2.setStyleSheet("font-size: 20px")
        event2_button = QPushButton('Записаться на мероприятие 2')
        out1_button = QPushButton('Отменить запись на мероприятие 1')
        out2_button = QPushButton('Отменить запись на мероприятие 2')
        event1_button.setStyleSheet("font-size: 25px; background-color: #F8F9F9")
        event2_button.setStyleSheet("font-size: 25px; background-color: #F8F9F9")
        out2_button.setStyleSheet('font-size: 25px; background-color: #F8F9F9')
        out1_button.setStyleSheet('font-size: 25px; background-color: #F8F9F9')
        self.dropdown_list = QComboBox()
        self.dropdown_list.addItem("Библиотека 1")
        self.dropdown_list.addItem("Библиотека 2")
        self.dropdown_list.addItem("Библиотека 3")
        self.dropdown_list.setStyleSheet("font-size: 20px; background-color: #F8F9F9")
        out1_button.setVisible(False)
        out2_button.setVisible(False)
        self.out1_button = out1_button
        self.out2_button = out2_button
        self.event1_button = event1_button
        self.event2_button = event2_button
        self.event1_button.clicked.connect(self.meet1)
        self.event2_button.clicked.connect(self.meet2)
        self.out1_button.clicked.connect(self.out1)
        self.out2_button.clicked.connect(self.out2)
        poster_block_layout.addWidget(poster_label)
        poster_block_layout.addWidget(self.dropdown_list)
        poster_block_layout.addWidget(mettup1)
        poster_block_layout.addWidget(event1_button)
        poster_block_layout.addWidget(out1_button)
        poster_block_layout.addWidget(mettup2)
        poster_block_layout.addWidget(event2_button)
        poster_block_layout.addWidget(out2_button)
        news_and_poster_layout.addWidget(news_block)
        news_and_poster_layout.addWidget(poster_block)
        main_layout.addWidget(news_and_poster_container)
        comments_block = QWidget()
        comments_block.setObjectName("Block3")
        comments_layout = QHBoxLayout(comments_block)
        comments_text_edit = QTextEdit()
        comments_text_edit.setFixedHeight(50)
        comments_text_edit.setFixedWidth(500)
        comments_text_edit.setPlaceholderText("Оставьте комментарий...")
        send_button = QPushButton('Отправить')
        clear_button = QPushButton('Очистить')
        send_button.setStyleSheet("font-size: 20px")
        clear_button.setStyleSheet("font-size: 20px")
        self.send_button = send_button
        self.clear_button = clear_button
        comments_layout.addWidget(comments_text_edit)
        comments_layout.addWidget(send_button)
        comments_layout.addWidget(clear_button)
        self.send_button.clicked.connect(self.send_comms)
        comments_text_edit.setVisible(False)
        send_button.setVisible(False)
        clear_button.setVisible(False)
        event1_button.setVisible(False)
        event2_button.setVisible(False)
        self.clear_button.clicked.connect(self.clear_comms)
        self.comments_text_edit = comments_text_edit
        user_activity_block = QWidget()
        user_activity_block.setObjectName("Block4")
        user_activity_layout = QVBoxLayout(user_activity_block)
        user_activity_label = QLabel("<u>Активность пользователей<u>")
        user_activity_label.setStyleSheet("font-size: 20px")
        self.user_activity_label = user_activity_label
        user_activity_label.setVisible(False)
        user_activity_layout.addWidget(user_activity_label)
        user_activity_label1 = QLabel("")
        self.user_activity_label1 = user_activity_label1
        user_activity_label1.setVisible(False)
        user_activity_layout.addWidget(user_activity_label1)
        main_layout.addWidget(comments_block)
        main_layout.addWidget(user_activity_block)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(main_widget)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def show_registration(self):
        self.registration_window.show()

    def show_authorization(self):
        self.authorization_window.show()

    def set_user_login(self, mail):
        self.login_mail = mail
        self.login_label.setText(f"Логин: {self.login_mail}")

    def hide_log_reg_buttons(self):
        self.main_window.registration_button.setVisible(True)
        self.main_window.authorization_button.setVisible(True)

    def show_logout_button(self):
        self.main_window.logout_button.setVisible(True)

    def logout_user(self):
        text = self.user_activity_label1.text()
        if text:
            text += '\n'
        self.user_activity_label1.setText(text + f'{self.login_mail} вышел с аккаунта')
        self.login_mail = ""
        self.login_label.setText("Логин: Гость")
        self.comments_text_edit.setVisible(False)
        self.send_button.setVisible(False)
        self.clear_button.setVisible(False)
        self.event1_button.setVisible(False)
        self.event2_button.setVisible(False)
        self.logout_button.setVisible(False)
        self.user_activity_label.setVisible(False)
        self.registration_button.setVisible(True)
        self.authorization_button.setVisible(True)
        self.out1_button.setVisible(False)
        self.out2_button.setVisible(False)
        self.user_activity_label1.setVisible(False)





    def clear_comms(self):
        self.comments_text_edit.setPlainText("")

    def send_comms(self):
        comment_text = self.comments_text_edit.toPlainText()
        if len(comment_text) == 0:
            QMessageBox.critical(self, 'Ошибка', 'Пустое воле ввода')
            return

        if len(comment_text) > 60:
            QMessageBox.critical(self, 'Ошибка', 'Комментарий слишком длинный. Максимум 60 символов.')
            self.comments_text_edit.setPlainText("")
            return

        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Comments (login, commentary) VALUES (?, ?)', (self.login_mail, comment_text))
        connection.commit()
        connection.close()
        QMessageBox.information(self, 'Успешно', 'Комментарий успешно отправлен.')
        self.comments_text_edit.clear()
        text = self.user_activity_label1.text()
        if text:
            text += '\n'
        self.user_activity_label1.setText(text + f'{self.login_mail} оставили комментарий')

    def meet1(self):
        PyQt5.QtWidgets.QMessageBox.information(self, 'Успешно', f'Вы зарегистровались на мероприятие 1')
        self.event1_button.setVisible(False)
        self.out1_button.setVisible(True)
        text1 = self.dropdown_list.currentText()[-1]
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Meets (login, meet, place) VALUES (?, ?, ?)', (self.login_mail, 1,  text1))
        connection.commit()
        connection.close()
        text = self.user_activity_label1.text()
        if text:
            text += '\n'
        self.user_activity_label1.setText(text + f'{self.login_mail} записались на мероприятие 1 в библиотеку {text1}')

    def meet2(self):
        PyQt5.QtWidgets.QMessageBox.information(self, 'Успешно', f'Вы зарегистровались на мероприятие 2')
        self.event2_button.setVisible(False)
        self.out2_button.setVisible(True)
        text2 = self.dropdown_list.currentText()[-1]
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Meets (login, meet, place) VALUES (?, ?, ?)', (self.login_mail, 2,  text2))
        connection.commit()
        connection.close()
        text = self.user_activity_label1.text()
        if text:
            text += '\n'
        self.user_activity_label1.setText(text + f'{self.login_mail} записались на мероприятие 2 в библиотеку {text2}')

    def out1(self):
        PyQt5.QtWidgets.QMessageBox.information(self, 'Успешно', f'Вы отменили запись на мероприятие 1')
        self.event1_button.setVisible(True)
        self.out1_button.setVisible(False)
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Meets WHERE login = ? AND meet = 1', (self.login_mail,))
        connection.commit()
        connection.close()
        text = self.user_activity_label1.text()
        if text:
            text += '\n'
        self.user_activity_label1.setText(text + f'{self.login_mail} отменили запись на мероприятие 1')

    def out2(self):
        PyQt5.QtWidgets.QMessageBox.information(self, 'Успешно', f'Вы отменили запись на мероприятие 2')
        self.event2_button.setVisible(True)
        self.out2_button.setVisible(False)
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Meets WHERE login = ? AND meet = 2', (self.login_mail,))
        connection.commit()
        connection.close()
        text = self.user_activity_label1.text()
        if text:
            text += '\n'
        self.user_activity_label1.setText(text + f'{self.login_mail} отменили запись на мероприятие 2')


if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
