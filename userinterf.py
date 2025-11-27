# user interface
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
)


class GameGUI(QWidget):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Baseball Scoreboard")
        self.layout = QVBoxLayout()

        # Undo button and history section
        undo_section = QVBoxLayout()

        self.undo_button = QPushButton("Undo Last Play")
        self.undo_button.clicked.connect(self.undo_last_play)
        undo_section.addWidget(self.undo_button)

        # Visual history of last 3 plays
        self.history_label = QLabel("Recent Plays:")
        self.history_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-top: 10px;"
        )
        undo_section.addWidget(self.history_label)

        self.play_history_display = QLabel("No plays yet")
        self.play_history_display.setStyleSheet(
            """
            background-color: #404040;
            border: 2px solid #3E6B65;
            border-radius: 5px;
            padding: 10px;
            font-size: 12px;
            font-weight: normal;
        """
        )
        self.play_history_display.setWordWrap(True)
        undo_section.addWidget(self.play_history_display)

        self.layout.addLayout(undo_section)

        # Score label
        self.score_label = QLabel()
        self.layout.addWidget(self.score_label)

        # Inning label
        self.inning_label = QLabel()
        self.layout.addWidget(self.inning_label)

        # Outs label
        self.outs_label = QLabel()
        self.layout.addWidget(self.outs_label)

        # Count label (balls-strikes) - NOW DISPLAYED
        self.count_label = QLabel()
        self.layout.addWidget(self.count_label)

        # Bases label
        self.bases_label = QLabel()
        self.layout.addWidget(self.bases_label)

        # Current batter label
        self.batter_label = QLabel()
        self.layout.addWidget(self.batter_label)

        # Batter management section
        self.batter_input = QLineEdit()
        self.batter_input.setPlaceholderText("Enter batter name")
        self.layout.addWidget(self.batter_input)

        self.set_batter_button = QPushButton("Set Current Batter")
        self.set_batter_button.clicked.connect(self.set_current_batter)
        self.layout.addWidget(self.set_batter_button)

        # Pitch recording section
        pitch_layout = QHBoxLayout()
        self.strike_button = QPushButton("Strike")
        self.strike_button.clicked.connect(lambda: self.record_pitch("strike"))
        self.ball_button = QPushButton("Ball")
        self.ball_button.clicked.connect(lambda: self.record_pitch("ball"))
        self.foul_button = QPushButton("Foul")
        self.foul_button.clicked.connect(lambda: self.record_pitch("foul"))

        pitch_layout.addWidget(self.strike_button)
        pitch_layout.addWidget(self.ball_button)
        pitch_layout.addWidget(self.foul_button)
        self.layout.addLayout(pitch_layout)

        # Optional: button to manually refresh display
        self.refresh_button = QPushButton("Refresh Display")
        self.refresh_button.clicked.connect(self.update_display)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)
        self.update_display()  # initialize display

        self.setStyleSheet(
            """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
                font-size: 20px;
            }
            QLabel {
                font-weight: bold;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton {
                background-color: #3E6B65;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4E7B75;
            }
            QPushButton:disabled {
                background-color: #808080;
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #404040;
                color: white;
                border: 2px solid #3E6B65;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #5E8B85;
            }
        """
        )

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

        # Count (balls-strikes) - NOW PROPERLY DISPLAYED
        balls = self.game_state.balls
        strikes = self.game_state.strikes
        self.count_label.setText(f"Count: {balls}-{strikes}")

        # Bases
        bases_state = self.game_state.bases.snapshot()
        bases_text = (
            f"1st: {bases_state['first'] or 'empty'}, "
            f"2nd: {bases_state['second'] or 'empty'}, "
            f"3rd: {bases_state['third'] or 'empty'}"
        )
        self.bases_label.setText(f"Bases: {bases_text}")

        # Current batter (if you have this method)
        if (
            hasattr(self.game_state, "current_batter")
            and self.game_state.current_batter
        ):
            batter_name = self.game_state.current_batter
        else:
            batter_name = "None"
        self.batter_label.setText(f"Batter: {batter_name}")

        # Update play history display
        self.update_play_history()

    def refresh_after_play(self, play):
        """Call after each play is applied to update UI."""
        self.update_display()

    def update_play_history(self):
        """Update the visual display of recent plays."""
        plays = self.game_state.get_last_n_plays(3)
        history_text = "\n".join(plays)
        self.play_history_display.setText(history_text)

    def undo_last_play(self):
        """Undo the last play with confirmation dialog."""
        # Check if there are plays to undo
        if not self.game_state.history:
            QMessageBox.information(self, "Undo", "No plays to undo")
            return

        # Get the last play description for the confirmation message
        last_play_info = (
            self.game_state.get_last_n_plays(1)[0]
            if self.game_state.history
            else "Unknown play"
        )

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Undo",
            f"Are you sure you want to undo:\n\n{last_play_info}\n\nThis will revert the game state.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,  # Default to No for safety
        )

        # If user confirms, perform undo
        if reply == QMessageBox.Yes:
            success = self.game_state.undo_last_play()
            if success:
                self.update_display()
                QMessageBox.information(
                    self, "Undo Successful", "Play has been undone."
                )
            else:
                QMessageBox.warning(self, "Undo Failed", "Failed to undo play.")

    def set_current_batter(self):
        """Set the current batter from the input field."""
        batter_name = self.batter_input.text().strip()
        if batter_name:
            # Store current batter in game_state
            self.game_state.current_batter = batter_name
            self.batter_input.clear()
            self.update_display()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a batter name")

    def record_pitch(self, pitch_type: str):
        """Record a pitch and update the display."""
        # Check if batter is set
        current_batter = getattr(self.game_state, "current_batter", None)
        if not current_batter:
            QMessageBox.warning(self, "Warning", "Please set a current batter first")
            return

        # Record the pitch
        event, should_continue = self.game_state.record_pitch(
            pitch_type, current_batter
        )
        self.update_display()

        # Show outcome messages for automatic events
        if event == "walk":
            QMessageBox.information(self, "Walk!", f"{current_batter} walked!")
            # Clear current batter after walk
            self.game_state.current_batter = None
        elif event == "strikeout":
            QMessageBox.information(self, "Strikeout!", f"{current_batter} struck out!")
            # Clear current batter after strikeout
            self.game_state.current_batter = None
