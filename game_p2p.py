import sys
import socket
import threading
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QMessageBox, QLabel, QVBoxLayout, QInputDialog
from PySide6.QtCore import Qt, Signal, QObject
import db_manager

class CommunicationSignals(QObject):
    msg_received = Signal(str)

class TicTacToe(QWidget):
    def __init__(self, my_name, opp_name, role):
        super().__init__()
        self.my_name = my_name
        self.opp_name = opp_name
        self.role = role # "server" sau "client"
        self.my_mark = "X" if role == "server" else "0"
        self.opp_mark = "0" if role == "server" else "X"
        self.my_turn = (role == "server")
        self.board = [""] * 9
        self.signals = CommunicationSignals()
        self.signals.msg_received.connect(self.handle_remote_move)
        
        db_manager.init_db()
        self.init_ui()
        self.setup_network()

    def init_ui(self):
        self.setWindowTitle(f"X si 0 - {self.my_name} ({self.my_mark})")
        layout = QVBoxLayout()
        s1, s2 = db_manager.get_score(self.my_name, self.opp_name)
        self.score_label = QLabel(f"Scor: {self.my_name} {s1} - {s2} {self.opp_name}")
        self.score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.score_label)

        self.grid = QGridLayout()
        self.buttons = []
        for i in range(9):
            btn = QPushButton("")
            btn.setFixedSize(100, 100)
            btn.setStyleSheet("font-size: 24px; font-weight: bold;")
            btn.clicked.connect(lambda ch, idx=i: self.make_move(idx))
            self.grid.addWidget(btn, i // 3, i % 3)
            self.buttons.append(btn)
        
        layout.addLayout(self.grid)
        self.setLayout(layout)

    def setup_network(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.role == "server":
            self.sock.bind(('localhost', 5555))
            self.sock.listen(1)
            threading.Thread(target=self.accept_connection, daemon=True).start()
        else:
            self.sock.connect(('localhost', 5555))
            threading.Thread(target=self.receive_data, args=(self.sock,), daemon=True).start()

    def accept_connection(self):
        self.conn, _ = self.sock.accept()
        self.receive_data(self.conn)

    def receive_data(self, sock):
        while True:
            try:
                data = sock.recv(1024).decode()
                if data: self.signals.msg_received.emit(data)
            except: break

    def make_move(self, idx):
        if self.my_turn and self.board[idx] == "":
            self.update_cell(idx, self.my_mark)
            target = self.conn if self.role == "server" else self.sock
            target.send(str(idx).encode())
            self.my_turn = False

    def handle_remote_move(self, data):
        idx = int(data)
        self.update_cell(idx, self.opp_mark)
        self.my_turn = True

    def update_cell(self, idx, mark):
        self.board[idx] = mark
        self.buttons[idx].setText(mark)
        self.check_game_over()

    def check_game_over(self):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] != "":
                winner = self.my_name if self.board[a] == self.my_mark else self.opp_name
                QMessageBox.information(self, "Final", f"Castigator: {winner}")
                db_manager.update_score(self.my_name, self.opp_name, winner)
                self.close()
                return
        if "" not in self.board:
            QMessageBox.information(self, "Remiza", "Egalitate!")
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    name, _ = QInputDialog.getText(None, "Login", "Numele tau:")
    opp, _ = QInputDialog.getText(None, "Login", "Numele adversarului:")
    role, _ = QInputDialog.getItem(None, "Rol", "Esti Jucator 1 sau 2?", ["1 (Creeaza joc)", "2 (Conectare)"], 0, False)
    
    is_server = "1" in role
    game = TicTacToe(name, opp, "server" if is_server else "client")
    game.show()
    sys.exit(app.exec())