import sys
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt5.QtWidgets import QDialogButtonBox, QLineEdit, QDialog, QFormLayout, QHeaderView, QVBoxLayout


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('recipes')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Выбор блюд')
        self.resize(360, 355)

        self.layout = QHBoxLayout(self)
        self.layout2 = QVBoxLayout(self)

        self.layout.addLayout(self.layout2)

        self.comboBox = QComboBox(self)
        self.layout2.addWidget(self.comboBox)
        self.comboBox.addItems(['Все', 'Завтрак', 'Обед', 'Ужин'])

        self.tableWidget = QTableWidget(self)
        self.layout.addWidget(self.tableWidget)
        self.update_result()

        self.btn = QPushButton(self)
        self.layout2.addWidget(self.btn)
        self.btn.setText('Поиск')
        self.btn.clicked.connect(self.update_result)

        self.btn_add = QPushButton(self)
        self.layout2.addWidget(self.btn_add)
        self.btn_add.setText('Добавить')
        self.btn_add.clicked.connect(self.add_item)

        self.btn_del = QPushButton(self)
        self.layout.addWidget(self.btn_del)
        self.layout2.addWidget(self.btn_del)
        self.btn_del.setText('Удалить')
        self.btn_del.clicked.connect(self.del_item)

    def update_result(self):
        # функция, которая выводит базу данных в нужном формате
        cur = self.con.cursor()
        result = ''
        if self.comboBox.currentText() == 'Все':
            result = cur.execute("""SELECT name, time FROM My_Recipes""").fetchall()
        elif self.comboBox.currentText() == 'Завтрак':
            result = cur.execute("""SELECT name, time FROM My_Recipes
                                    WHERE type = 'завтрак'""").fetchall()
        elif self.comboBox.currentText() == 'Обед':
            result = cur.execute("""SELECT name, time FROM My_Recipes
                                    WHERE type = 'обед'""").fetchall()
        elif self.comboBox.currentText() == 'Ужин':
            result = cur.execute("""SELECT name, time FROM My_Recipes
                                    WHERE type = 'ужин'""").fetchall()
        self.count = len(result)
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['Название', 'Время приготов.'])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def add_item(self):
        # добавление значения с использованием диалогового окна
        global dialog
        dialog = InputDialog()
        dialog.show()
        # если тип выбран, то он автоматически записывается в поле ввода
        if self.comboBox.currentText() == 'Завтрак':
            dialog.third.setText('завтрак')
        elif self.comboBox.currentText() == 'Обед':
            dialog.third.setText('обед')
        elif self.comboBox.currentText() == 'Ужин':
            dialog.third.setText('ужин')
        res = dialog.exec()
        # добавление введенных значений в таблицу
        if res:
            self.count += 1
            cur = self.con.cursor()
            cur.execute("""INSERT INTO My_Recipes(id,name,time,type) VALUES(?,?,?,?)""", (self.count,
                                                                                          dialog.first.text(),
                                                                                          dialog.second.text(),
                                                                                          dialog.third.text().lower()))
        self.con.commit()

    def del_item(self):
        # удаление выбранного по id значения
        global dialog
        dialog = GetIdDialog()
        dialog.show()
        res = dialog.exec()
        if res:
            self.count -= 1
            cur = self.con.cursor()
            cur.execute("""DELETE from My_Recipes
                           WHERE id = ?""", (dialog.get_id.text(),))
            self.con.commit()


class InputDialog(QDialog):
    def __init__(self, parent=None):
        # диалоговое окно, которое появляется для добавления значений
        super().__init__(parent)

        self.setWindowTitle('Введите данные')
        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        self.third = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow('Название', self.first)
        layout.addRow('Время', self.second)
        layout.addRow('Приём пищи', self.third)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)


class GetIdDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # диалоговое окно, которое появляется для удаления значений
        self.setWindowTitle('Введите id')
        self.get_id = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow('id', self.get_id)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())
