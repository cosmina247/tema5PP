import sys
import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QTextEdit, QFileDialog, QMessageBox

try:
    import win32pipe, win32file
except ImportError:
    print("Atentie: Ruleaza 'uv add pywin32' pentru a putea trimite date catre C!")

def convert_text_to_html(content):
    lines = content.strip().split('\n')
    if not lines:
        return ""
    
    html = f"<h1>{lines[0]}</h1>\n"
    
    for line in lines[1:]:
        if line.strip(): 
            html += f"<p>{line.strip()}</p>\n"
            
    return html

def main():
    loader = QUiLoader()
    app = QApplication(sys.argv)

    ui_file = QFile("appp.ui")
    if not ui_file.exists():
        print("Eroare: Nu am gasit fisierul appp.ui! Verifica numele.")
        return
        
    ui_file.open(QFile.ReadOnly)
    window = loader.load(ui_file)
    ui_file.close()

    path_input = window.findChild(QLineEdit, "pathLineEdit")
    result_display = window.findChild(QTextEdit, "resultTextEdit")
    
    btn_browse = window.findChild(QPushButton, "browseButton")
    btn_convert = window.findChild(QPushButton, "convertButton")
    btn_send = window.findChild(QPushButton, "sendButton")

    def handle_browse():
        file_path, _ = QFileDialog.getOpenFileName(window, "Selecteaza fisierul text", "", "Text Files (*.txt)")
        if file_path:
            path_input.setText(file_path)

    def handle_convert():
        path = path_input.text()
        if not os.path.exists(path):
            QMessageBox.warning(window, "Eroare", "Te rugam sa selectezi un fisier valid!")
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                html_output = convert_text_to_html(raw_content)
                result_display.setPlainText(html_output) 
        except Exception as e:
            QMessageBox.critical(window, "Eroare", f"Nu am putut citi fisierul: {e}")

    def handle_send():
        html_content = result_display.toPlainText()
        if not html_content:
            QMessageBox.warning(window, "Eroare", "Nu exista continut de trimis! Apasa Convert mai intai.")
            return

        try:
            handle = win32file.CreateFile(
                r"\\.\pipe\Lab5Pipe",
                win32file.GENERIC_WRITE, 0, None,
                win32file.OPEN_EXISTING, 0, None
            )
            win32file.WriteFile(handle, html_content.encode('utf-8'))
            win32file.CloseHandle(handle)
            QMessageBox.information(window, "Succes", "Mesaj trimis cu succes catre aplicatia C!")
        except Exception as e:
            QMessageBox.critical(window, "Eroare", f"Asigura-te ca programul C (receiver.exe) ruleaza!\n{e}")

    if btn_browse: btn_browse.clicked.connect(handle_browse)
    if btn_convert: btn_convert.clicked.connect(handle_convert)
    if btn_send: btn_send.clicked.connect(handle_send)

    window.show()
    app.exec()

if __name__ == "__main__":
    main()