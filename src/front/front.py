import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from utils import *

#main window includes a welcome message and a button

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Welcome")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        label = QLabel("Welcome to the app")
        label.setAlignment(Qt.AlignCenter)
        font = QFont("Comic Sans MS", 16)
        font.setBold(True)
        label.setFont(font)

        layout.addWidget(label)


        button_log_in = QPushButton("Log In")
        button_log_in.clicked.connect(self.on_login_click)
        layout.addWidget(button_log_in)

        button_sign_up = QPushButton("Sign Up")
        button_sign_up.clicked.connect(self.on_signup_click)
        layout.addWidget(button_sign_up)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def on_login_click(self):
        layout = QVBoxLayout()

        label = QLabel("Log In")

        label_username = QLabel("Username")
        label_password = QLabel("Password")
        username_input = QLineEdit()
        password_input = QLineEdit()
        signup_btn = QPushButton("Sign Up Instead")
        layout.addWidget(label)
        layout.addWidget(label_username)
        layout.addWidget(username_input)
        layout.addWidget(label_password)
        layout.addWidget(password_input)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_log_in(username_input.text(), password_input.text()))
        layout.addWidget(button_submit)

        layout.addWidget(signup_btn)
        signup_btn.clicked.connect(self.on_signup_click)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def try_log_in(self, username, password):
        success = login(username, password)
        if success:
        #show pop up message
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("Login successful")
            msg.exec_()
            self.my_account(username)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Login failed")
            msg.exec_()
    def on_signup_click(self):
        layout = QVBoxLayout()

        label = QLabel("Sign Up")

        label_username = QLabel("Username")
        label_password = QLabel("Password")
        username_input = QLineEdit()
        password_input = QLineEdit()
        log_in_btn = QPushButton("Have an account? Log In")
        layout.addWidget(label)
        layout.addWidget(label_username)
        layout.addWidget(username_input)
        layout.addWidget(label_password)
        layout.addWidget(password_input)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_sign_up(username_input.text(), password_input.text()))
        layout.addWidget(button_submit)

        layout.addWidget(log_in_btn)
        log_in_btn.clicked.connect(self.on_login_click)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def try_sign_up(self, username, password):
        success = signup(username, password)
        if success:
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("Sign up successful")
            msg.exec_()
            self.on_login_click()

        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Sign up failed")
            msg.exec_()

    def create_group(self, all_users = [1,2,3,4]):
        layout = QVBoxLayout()

        label = QLabel("Create Group")

        label_group_name = QLabel("Group Name")
        group_name_input = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(label_group_name)
        layout.addWidget(group_name_input)

        #boolean if it's hierarchical
        hierarchical = QCheckBox("Hierarchical")
        layout.addWidget(hierarchical)


        label_users = QLabel("Add Users")
        layout.addWidget(label_users)

        list_widget = QListWidget()
        for user in all_users:
            item = QListWidgetItem(str(user))
            item.setCheckState(0)
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_create_group(group_name_input.text(), get_Selected_users(list_widget), hierarchical.isChecked()))
        layout.addWidget(button_submit)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def try_create_group(self, group_name, selected_users, hierarchical):
        success = create_group(group_name, selected_users, hierarchical)
        if success:
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("Group created")
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Group creation failed")
            msg.exec_()

    def my_account(self, username):
        layout = QVBoxLayout()

        label = QLabel("My Account")

        label_username = QLabel(f"Username: {username}")

        view_agenda_btn = QPushButton("View Agenda")
        view_agenda_btn.clicked.connect(lambda: self.view_agenda(get_meetings(username)))
        layout.addWidget(label)
        layout.addWidget(label_username)
        layout.addWidget(view_agenda_btn)

        view_pending_meetings_btn = QPushButton("View Pending Meetings")
        view_pending_meetings_btn.clicked.connect(lambda: self.view_pending_meetings(get_pending_meetings(username)))
        layout.addWidget(view_pending_meetings_btn)

        create_meeting_btn = QPushButton("Create Meeting")
        create_meeting_btn.clicked.connect(self.create_meeting)
        layout.addWidget(create_meeting_btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def view_agenda(self, agenda):
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label = QLabel("Agenda")
        layout.addWidget(label)

        table = self.createTable(agenda)
        layout.addWidget(table)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account("username"))
        layout.addWidget(back_btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def view_pending_meetings(self, username):
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label = QLabel("Pending Meetings")
        layout.addWidget(label)

        meetings = get_pending_meetings(username)
        table = self.createTable(meetings, True)
        layout.addWidget(table)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account("username"))
        layout.addWidget(back_btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_meeting(self):
        layout = QVBoxLayout()

        label = QLabel("Create Meeting")

        label_meeting_name = QLabel("Meeting Name")
        meeting_name_input = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(label_meeting_name)
        layout.addWidget(meeting_name_input)

        label_description = QLabel("Description")
        description_input = QLineEdit()
        layout.addWidget(label_description)
        layout.addWidget(description_input)

        date_label = QLabel("Date")
        date_input = QCalendarWidget()
        layout.addWidget(date_label)
        layout.addWidget(date_input)

        label_time = QLabel("Time")
        time_input = QLineEdit()
        layout.addWidget(label_time)
        layout.addWidget(time_input)

        allusers = [1,2,3,4]
        label_users = QLabel("Add Users")
        layout.addWidget(label_users)

        list_widget = QListWidget()
        for user in allusers:
            item = QListWidgetItem(str(user))
            item.setCheckState(0)
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_create_meeting(meeting_name_input.text(), description_input.text(), time_input.text(), get_Selected_users(list_widget), date_input.selectedDate().toString("yyyy-MM-dd")))
        layout.addWidget(button_submit)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account("username"))
        layout.addWidget(back_btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def try_create_meeting(self, name, description, time, users, date):
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText("Meeting created")
        msg.exec_()
        self.my_account("username")


    def accept_decline(self, username, id):
        #pop up question
        msg = QMessageBox()
        msg.setWindowTitle("Accept/Decline")
        msg.setText("Do you want to accept or decline the meeting?")
        accept_btn = QPushButton("Accept")
        decline_btn = QPushButton("Decline")
        msg.addButton(accept_btn, QMessageBox.AcceptRole)
        msg.addButton(decline_btn, QMessageBox.RejectRole)
        msg.exec_()
        if msg.clickedButton() == accept_btn:
            accept_meeting(username, id)
        else:
            decline_meeting(username, id)

        self.view_pending_meetings(username)


    def createTable(self, agenda : [AgendaItem], need_to_accept = False):
        table = QTableWidget()
        table.setRowCount(len(agenda))
        table.setColumnCount(4) if not need_to_accept else table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Description", "Time", "Date"]) if not need_to_accept else (
            table.setHorizontalHeaderLabels(["Name", "Description", "Time", "Date", "Accept/Decline"]))
        for i, item in enumerate(agenda):
            table.setItem(i, 0, QTableWidgetItem(item.name))
            table.setItem(i, 1, QTableWidgetItem(item.description))
            table.setItem(i, 2, QTableWidgetItem(item.time))
            table.setItem(i, 3, QTableWidgetItem(str(item.date)))
            if need_to_accept:
                button = QPushButton("Accept/Decline")
                button.clicked.connect(lambda: self.accept_decline("username", i))
                table.setCellWidget(i, 4, button)


        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        return table


#main function
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())