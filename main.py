import sys
import os
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
                           QHeaderView, QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

from UI.main_ui import Ui_MainWindow
from UI.addEditCoffeeForm import Ui_Dialog

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_database_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'data', 'coffee.sqlite')

class AddEditCoffeeForm(QDialog, Ui_Dialog):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.coffee_id = coffee_id
        self.setup_validators()
        
        if self.coffee_id:
            self.load_coffee_data()
            self.setWindowTitle("Редактирование кофе")
        else:
            self.setWindowTitle("Добавление нового кофе")
            
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.clicked.connect(self.accept)
        
    def setup_validators(self):
        price_validator = QDoubleValidator()
        price_validator.setBottom(0)
        self.priceEdit.setValidator(price_validator)
        
        volume_validator = QDoubleValidator()
        volume_validator.setBottom(0)
        self.volumeEdit.setValidator(volume_validator)
            
    def load_coffee_data(self):
        try:
            db_path = get_database_path()
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee WHERE id = ?", (self.coffee_id,))
            coffee_data = cursor.fetchone()
            conn.close()
            
            if coffee_data:
                self.nameEdit.setText(coffee_data[1])
                self.roastCombo.setCurrentText(coffee_data[2])
                self.typeCombo.setCurrentText(coffee_data[3])
                self.descriptionEdit.setPlainText(coffee_data[4])
                self.priceEdit.setText(str(coffee_data[5]))
                self.volumeEdit.setText(str(coffee_data[6]))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")
    
    def get_data(self):
        return {
            'name': self.nameEdit.text().strip(),
            'roast_degree': self.roastCombo.currentText(),
            'type': self.typeCombo.currentText(),
            'description': self.descriptionEdit.toPlainText().strip(),
            'price': self.priceEdit.text().strip(),
            'volume': self.volumeEdit.text().strip()
        }
    
    def validate_data(self, data):
        if not data['name']:
            QMessageBox.warning(self, "Ошибка", "Введите название кофе")
            return False
        if not data['price'] or float(data['price']) <= 0:
            QMessageBox.warning(self, "Ошибка", "Введите корректную цену")
            return False
        if not data['volume'] or float(data['volume']) <= 0:
            QMessageBox.warning(self, "Ошибка", "Введите корректный объем")
            return False
        return True

class CoffeeApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)
        self.deleteButton.clicked.connect(self.delete_coffee)
        self.tableWidget.itemSelectionChanged.connect(self.on_selection_changed)
        self.on_selection_changed()
        
    def on_selection_changed(self):
        has_selection = len(self.tableWidget.selectedItems()) > 0
        self.editButton.setEnabled(has_selection)
        self.deleteButton.setEnabled(has_selection)
        
    def load_data(self):
        try:
            db_path = get_database_path()
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS coffee (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roast_degree TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                volume REAL NOT NULL
            )
            ''')
            
            cursor.execute("SELECT * FROM coffee")
            data = cursor.fetchall()
            
            if not data:
                self.initialize_sample_data(cursor)
                conn.commit()
                cursor.execute("SELECT * FROM coffee")
                data = cursor.fetchall()
            
            self.tableWidget.setRowCount(len(data))
            self.tableWidget.setColumnCount(7)
            self.tableWidget.setHorizontalHeaderLabels([
                'ID', 'Название сорта', 'Степень обжарки', 'Молотый/в зернах', 
                'Описание вкуса', 'Цена (руб)', 'Объем упаковки (г)'
            ])
            
            for row_num, row_data in enumerate(data):
                for col_num, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(Qt.GlobalColor.black)
                    self.tableWidget.setItem(row_num, col_num, item)
            
            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
            
            self.tableWidget.verticalHeader().setDefaultSectionSize(40)
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {e}")
    
    def initialize_sample_data(self, cursor):
        coffee_data = [
            ('Эфиопия Иргачефф', 'Средняя', 'Зерна', 'Цветочные и цитрусовые ноты с яркой кислотностью', 1250.0, 250.0),
            ('Колумбия Супремо', 'Темная', 'Молотый', 'Шоколадный вкус с ореховыми нотами', 980.0, 250.0),
            ('Кения АА', 'Светлая', 'Зерна', 'Ягодные тона с винным послевкусием', 1450.0, 200.0),
            ('Бразилия Сантос', 'Средняя', 'Молотый', 'Ореховый вкус с сладким карамельным послевкусием', 850.0, 500.0),
            ('Гватемала Антивей', 'Темная', 'Зерна', 'Дымный аромат с пряными нотами', 1100.0, 300.0),
            ('Эспрессо Бленд', 'Темная', 'Молотый', 'Сбалансированный вкус для эспрессо', 920.0, 400.0),
            ('Коста Рика Тарразу', 'Средняя', 'Зерна', 'Яркий вкус с нотками карамели и орехов', 1350.0, 250.0)
        ]
        
        cursor.executemany('''
        INSERT INTO coffee (name, roast_degree, type, description, price, volume)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', coffee_data)
    
    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if dialog.validate_data(data):
                self.save_coffee(data)
    
    def edit_coffee(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            coffee_id = int(self.tableWidget.item(selected_row, 0).text())
            dialog = AddEditCoffeeForm(self, coffee_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if dialog.validate_data(data):
                    self.save_coffee(data, coffee_id)
    
    def delete_coffee(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            coffee_id = int(self.tableWidget.item(selected_row, 0).text())
            coffee_name = self.tableWidget.item(selected_row, 1).text()
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления", 
                f"Вы уверены, что хотите удалить кофе '{coffee_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    db_path = get_database_path()
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM coffee WHERE id = ?", (coffee_id,))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    QMessageBox.information(self, "Успех", "Кофе удален успешно")
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
    
    def save_coffee(self, data, coffee_id=None):
        try:
            db_path = get_database_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if coffee_id:
                cursor.execute('''
                    UPDATE coffee 
                    SET name=?, roast_degree=?, type=?, description=?, price=?, volume=?
                    WHERE id=?
                ''', (data['name'], data['roast_degree'], data['type'], 
                      data['description'], float(data['price']), float(data['volume']), coffee_id))
                message = "Кофе обновлен успешно"
            else:
                cursor.execute('''
                    INSERT INTO coffee (name, roast_degree, type, description, price, volume)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['name'], data['roast_degree'], data['type'], 
                      data['description'], float(data['price']), float(data['volume'])))
                message = "Кофе добавлен успешно"
            
            conn.commit()
            conn.close()
            self.load_data()
            QMessageBox.information(self, "Успех", message)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())