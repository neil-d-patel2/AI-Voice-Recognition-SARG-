# userinterf.py
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton

class GameGUI(QWidget):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.initUI()
    
       

    def initUI(self):
        self.setWindowTitle("Baseball Scoreboard")
        self.layout = QVBoxLayout()

        # Score label
        self.score_label = QLabel()
        self.layout.addWidget(self.score_label)

        # Inning label
        self.inning_label = QLabel()
        self.layout.addWidget(self.inning_label)

        # Outs label
        self.outs_label = QLabel()
        self.layout.addWidget(self.outs_label)

        # Bases label
        self.bases_label = QLabel()
        self.layout.addWidget(self.bases_label)

        # Optional: button to manually refresh display
        self.refresh_button = QPushButton("Refresh Display")
        self.refresh_button.clicked.connect(self.update_display)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)
        self.update_display()  # initialize display

        self.setStyleSheet("""
                            QWidget {
                            background-color: #2E2E2E;
                            color: #FFFFFF;
                            font-family: Roboto;
                            font-size: 20px;
                            }
                            QLabel {
                            font-weight: bold;
                            font-size: 16px;
                            }
                            QPushButton {
                                background-color: #3E6B65;
                                color: white;
                                border-radius: 5px;
                                padding: 5px 10px;
                            }
                            QPushButton:hover {
                                background-color: #3E6B65;
                            }
                            """)
    def update_display(self):
        """Update all labels based on current game state."""
        # Score
        self.score_label.setText(
            f"{self.game_state.away.name}: {self.game_state.away.runs}  |  "
            f"{self.game_state.home.name}: {self.game_state.home.runs}"
        )

        # Inning
        inning_half = "Top" if self.game_state.inning.top else "Bottom"
        inning_number = self.game_state.inning.number
        self.inning_label.setText(f"Inning: {inning_half} {inning_number}")

        # Outs
        self.outs_label.setText(f"Outs: {self.game_state.outs}")

        # Bases
        bases_state = self.game_state.bases.snapshot()
        bases_text = (
            f"1st: {bases_state['first'] or 'empty'}, "
            f"2nd: {bases_state['second'] or 'empty'}, "
            f"3rd: {bases_state['third'] or 'empty'}"
        )
        self.bases_label.setText(f"Bases: {bases_text}")

    def refresh_after_play(self, play):
        """Call after each play is applied to update UI."""
        self.update_display()

