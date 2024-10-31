from PySide6.QtWidgets import *
import csv

tally_answers = {
    "Math": 0,
    "Science": 0,
    "Language": 0,
    "English": 0,
    "History": 0
}


def export():
    file_path, _ = QFileDialog.getSaveFileName(window, "Save File", "", "CSV Files (*.csv)")
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Selected Subject", "Count"])
            
            for answer, number in tally_answers.items():
                writer.writerow([answer, number])

def submit():
    if math.isChecked():
        tally_answers["Math"] += 1
    if science.isChecked():
        tally_answers["Science"] += 1
    if language.isChecked():
        tally_answers["Language"] += 1
    if english.isChecked():
        tally_answers["English"] += 1
    if history.isChecked():
        tally_answers["History"] += 1

    msg = QMessageBox()
    msg.setText("Thanks For Your Answer")
    msg.exec()

    math.setChecked(False)
    science.setChecked(False)
    language.setChecked(False)
    english.setChecked(False)
    history.setChecked(False)

app = QApplication([])
window = QWidget()
window.setWindowTitle("Roan Cowan")
window.resize(400, 300)

grid = QGridLayout()
label = QLabel("What is the best class at Loomis?")
grid.addWidget(label, 0, 0)


math = QCheckBox("Math")
science = QCheckBox("Science")
language = QCheckBox("Language")
english = QCheckBox("English")
history = QCheckBox("History")

grid.addWidget(math, 1, 0)
grid.addWidget(science, 2, 0)
grid.addWidget(language, 3, 0)
grid.addWidget(english, 4, 0)
grid.addWidget(history, 5, 0)


submit_button = QPushButton("Submit")
submit_button.clicked.connect(submit)
grid.addWidget(submit_button, 6, 0)

export_button = QPushButton("Export")
export_button.clicked.connect(export)
grid.addWidget(export_button, 7, 0)


window.setLayout(grid)
window.show()
app.exec()
