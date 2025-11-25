import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
                           QHeaderView, QMessageBox, Qdig, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                           QTextEdit, QPushButton, QFormLayout, QWidget,
                           QTableWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

class AddEditCoffeeForm(Qdig):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.coffee_id = coffee_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Добавление/Редактирование кофе")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.nameEdit = QLineEdit()
        self.nameEdit.setPlaceholderText("Введите название кофе")
        form_layout.addRow("Название сорта:", self.nameEdit)
        
        self.roastCombo = QComboBox()
        self.roastCombo.addItems(["Светлая", "Средняя", "Темная"])
        form_layout.addRow("Степень обжарки:", self.roastCombo)
        
        self.typeCombo = QComboBox()
        self.typeCombo.addItems(["Зерна", "Молотый"])
        form_layout.addRow("Тип:", self.typeCombo)
        
        self.priceEdit = QLineEdit()
        self.priceEdit.setPlaceholderText("0.00")
        price_validator = QDoubleValidator()
        price_validator.setBottom(0)
        self.priceEdit.setValidator(price_validator)
        form_layout.addRow("Цена (руб):", self.priceEdit)
        
        self.volumeEdit = QLineEdit()
        self.volumeEdit.setPlaceholderText("0")
        volume_validator = QDoubleValidator()
        volume_validator.setBottom(0)
        self.volumeEdit.setValidator(volume_validator)
        form_layout.addRow("Объем упаковки (г):", self.volumeEdit)
        
        self.descriptionEdit = QTextEdit()
        self.descriptionEdit.setMaximumHeight(80)
        self.descriptionEdit.setPlaceholderText("Описание вкусовых характеристик")
        form_layout.addRow("Описание вкуса:", self.descriptionEdit)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        
        self.cancelButton = QPushButton("Отмена")
        self.cancelButton.clicked.connect(self.reject)
        
        self.saveButton = QPushButton("Сохранить")
        self.saveButton.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancelButton)
        button_layout.addWidget(self.saveButton)
        
        layout.addLayout(button_layout)
        
        if self.coffee_id:
            self.load_coffee_data()
            self.setWindowTitle("Редактирование кофе")
        else:
            self.setWindowTitle("Добавление нового кофе")
            
    def load_coffee_data(self):
        try:
            conn = sqlite3.connect('coffee.sqlite')
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

class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог кофе")
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        title_label = QLabel("Каталог кофе")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #8B4513; margin: 10px;")
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        
        self.addButton = QPushButton("Добавить кофе")
        self.addButton.clicked.connect(self.add_coffee)
        
        self.editButton = QPushButton("Редактировать")
        self.editButton.clicked.connect(self.edit_coffee)
        self.editButton.setEnabled(False)
        
        self.deleteButton = QPushButton("Удалить")
        self.deleteButton.clicked.connect(self.delete_coffee)
        self.deleteButton.setEnabled(False)
        
        button_layout.addWidget(self.addButton)
        button_layout.addWidget(self.editButton)
        button_layout.addWidget(self.deleteButton)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.tableWidget)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #e0e0e0;
                alternate-background-color: #f8f8f8;
            }
            QHeaderView::section {
                background-color: #8B4513;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #8B4513;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A0522D;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
    def on_selection_changed(self):
        has_selection = len(self.tableWidget.selectedItems()) > 0
        self.editButton.setEnabled(has_selection)
        self.deleteButton.setEnabled(has_selection)
        
    def load_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM coffee")
        data = cursor.fetchall()
        
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            'ID', 'Название сорта', 'Степень обжарки', 'Молотый/в зернах', 
            'Описание вкуса', 'Цена (руб)', 'Объем упаковки (г)'
        ])
        
        for rw_nm, data in enumerate(data):
            for col_num, col_data in enumerate(data):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(Qt.GlobalColor.black)
                self.tableWidget.setItem(rw_nm, col_num, item)
        
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
                
    def add_coffee(self):
        dig = AddEditCoffeeForm(self)
        if dig.exec() == Qdig.digCode.Accepted:
            data = dig.get_data()
            if dig.validate_data(data):
                self.save_coffee(data)
    
    def edit_coffee(self):
        rw = self.tableWidget.currentRow()
        if rw >= 0:
            coffee_id = int(self.tableWidget.item(rw, 0).text())
            dig = AddEditCoffeeForm(self, coffee_id)
            if dig.exec() == Qdig.digCode.Accepted:
                data = dig.get_data()
                if dig.validate_data(data):
                    self.save_coffee(data, coffee_id)
    
    def delete_coffee(self):
        rw = self.tableWidget.currentRow()
        if rw >= 0:
            coffee_id = int(self.tableWidget.item(rw, 0).text())
            coffee_name = self.tableWidget.item(rw, 1).text()
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления", 
                f"Вы уверены, что хотите удалить кофе '{coffee_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect('coffee.sqlite')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM coffee WHERE id = ?", (coffee_id,))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    QMessageBox.information(self, "Успех", "Кофе удален успешно")
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
    
    def save_coffee(self, data, coffee_id=None):
        conn = sqlite3.connect('coffee.sqlite')
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
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())