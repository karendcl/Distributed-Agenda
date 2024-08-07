import sys
import os
from typing import List

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from utils import *



class QLineEdit(QLineEdit):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid gray;")
        self.setFixedHeight(30)

        #set font Calibri, 10
        font = QFont("Calibri", 10)
        self.setFont(font)

class QLabel(QLabel):
    def __init__(self, text, parent = None):
        super().__init__(text, parent)
        font = QFont("Calibri", 12)
        font.setBold(True)
        self.setFont(font)

        style_sheet = "color: maroon;"
        self.setStyleSheet(style_sheet)

class QTitleLabel(QLabel):
    def __init__(self, text, parent = None):
        super().__init__(text, parent)
        font = QFont("Calibri", 16)
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        style_sheet = "text-decoration: underline;"
        style_sheet += "color: darkred;"
        self.setStyleSheet(style_sheet)

class QSubTitleLabel(QLabel):
    def __init__(self, text, parent = None):
        super().__init__(text, parent)
        font = QFont("Calibri", 14)
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)

        style_sheet = "color: firebrick;"
        self.setStyleSheet(style_sheet)


class QPushButton(QPushButton):
    def __init__(self, text, parent = None):
        super().__init__(text, parent)
        self.setStyleSheet("border: 1px solid gray;")
        self.setFixedHeight(30)
        self.setFixedWidth(10 * len(text) + 20)

        #set font Calibri, 10
        font = QFont("Calibri", 10)
        self.setFont(font)

class PasswordLineEdit(QLineEdit):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.iconShow = QIcon('icons/eye.png')
        self.iconHide = QIcon('icons/closed_eye.png')

        self.showPassAction = QAction(self.iconShow, 'Show Password', self)
        self.addAction(self.showPassAction, QLineEdit.TrailingPosition)
        self.showPassAction.setCheckable(True)
        self.showPassAction.toggled.connect(self.togglePasswordVisibility)

        #do border
        self.setFixedHeight(30)
        self.setFixedWidth(200)

    def togglePasswordVisibility(self, show):
        if show:
            self.setEchoMode(QLineEdit.Normal)
            self.showPassAction.setIcon(self.iconHide)
        else:
            self.setEchoMode(QLineEdit.Password)
            self.showPassAction.setIcon(self.iconShow)

class QListWidget(QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid gray;")
        self.setSpacing(5)

class QComboBox(QComboBox):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid gray;")
        self.setFixedHeight(30)

        #set font Calibri, 10
        font = QFont("Calibri", 10)
        self.setFont(font)

        #set spacing between options
        self.view().setSpacing(5)

        self.setStyleSheet("QComboBox::down-arrow {image: url(icons/down-arrow.png);}")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Agenda")
        self.setGeometry(100, 100, 400, 200)
        self.initial()

    def initial(self):
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        label = QTitleLabel("Your personal agenda")
        layout.addWidget(label)

        button_log_in = QPushButton("Log In")
        button_log_in.clicked.connect(self.on_login_click)
        layout.addWidget(button_log_in, alignment=Qt.AlignCenter)

        button_sign_up = QPushButton("Sign Up")
        button_sign_up.clicked.connect(self.on_signup_click)
        layout.addWidget(button_sign_up, alignment=Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def on_login_click(self):
        layout = QVBoxLayout()

        label = QTitleLabel("Log In")

        label_username = QLabel("Username")
        label_password = QLabel("Password")
        username_input = QLineEdit()
        password_input = PasswordLineEdit()

        signup_btn = QPushButton("Sign Up Instead")
        layout.addWidget(label)
        layout.addWidget(label_username)
        layout.addWidget(username_input)
        layout.addWidget(label_password)
        layout.addWidget(password_input)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_log_in(username_input.text(), password_input.text()))
        layout.addWidget(button_submit, alignment = Qt.AlignCenter)

        layout.addWidget(signup_btn, alignment = Qt.AlignCenter)
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

        label = QTitleLabel("Sign Up")

        label_username = QLabel("Username")
        label_password = QLabel("Password")
        username_input = QLineEdit()
        password_input = PasswordLineEdit()
        log_in_btn = QPushButton("Have an account? Log In")
        layout.addWidget(label)
        layout.addWidget(label_username)
        layout.addWidget(username_input)
        layout.addWidget(label_password)
        layout.addWidget(password_input)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_sign_up(username_input.text(), password_input.text()))
        layout.addWidget(button_submit, alignment = Qt.AlignCenter)

        layout.addWidget(log_in_btn, alignment = Qt.AlignCenter)
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
            self.my_account(username)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Sign up failed")
            msg.exec_()

    def create_group(self, username):

        self.setMaximumSize(400, 600)
        self.setGeometry(100, 100, 400, 600)

        all_users = get_all_users(username)

        layout = QVBoxLayout()

        label = QTitleLabel("Create Group")

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

        print(all_users)

        list_widget = QListWidget()
        for user in all_users:
            item = QListWidgetItem(str(user))
            item.setCheckState(0)
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_create_group(group_name_input.text(), get_Selected_users(list_widget), hierarchical.isChecked(), username))
        layout.addWidget(button_submit, alignment = Qt.AlignCenter)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account(username))
        layout.addWidget(back_btn, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def try_create_group(self, group_name, selected_users, hierarchical, username):
        success = create_group(group_name, selected_users, hierarchical, username)
        if success:
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Group created")
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Group creation failed")
            msg.exec_()

    def my_account(self, username):

        self.setMaximumSize(400, 300)
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        label = QTitleLabel("My Account")

        label_username = QSubTitleLabel(f"Username: {username}")

        view_agenda_btn = QPushButton("View Agenda")
        view_agenda_btn.clicked.connect(lambda: self.view_agenda(get_meetings(username), username))
        layout.addWidget(label)
        layout.addWidget(label_username)
        layout.addWidget(view_agenda_btn, alignment = Qt.AlignCenter)

        view_pending_meetings_btn = QPushButton("View Pending Meetings")
        view_pending_meetings_btn.clicked.connect(lambda: self.view_pending_meetings(username))
        layout.addWidget(view_pending_meetings_btn, alignment=Qt.AlignCenter)

        create_meeting_btn = QPushButton("Create Meeting")
        create_meeting_btn.clicked.connect(lambda: self.create_meeting(username))
        layout.addWidget(create_meeting_btn, alignment=Qt.AlignCenter)

        create_group_btn = QPushButton("Create Group")
        create_group_btn.clicked.connect(lambda: self.create_group(username))
        layout.addWidget(create_group_btn, alignment=Qt.AlignCenter)

        view_others_agenda_btn = QPushButton("View Other's Agenda")
        view_others_agenda_btn.clicked.connect(lambda: self.view_others_agenda(username))
        layout.addWidget(view_others_agenda_btn, alignment=Qt.AlignCenter)

        delete_events_btn = QPushButton("Delete Events")
        delete_events_btn.clicked.connect(lambda: self.delete_events(username))
        layout.addWidget(delete_events_btn, alignment=Qt.AlignCenter)

        create_containers_btn = QPushButton("Create Containers")
        create_containers_btn.clicked.connect(lambda: self.create_containers(username))
        layout.addWidget(create_containers_btn, alignment=Qt.AlignCenter)

        log_out_btn = QPushButton("Log Out")
        log_out_btn.clicked.connect(lambda: self.logout(username))
        layout.addWidget(log_out_btn, alignment=Qt.AlignCenter)


        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def delete_events(self, username):
        self.setMaximumSize(800, 600)
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label = QTitleLabel("Delete Events")
        layout.addWidget(label)

        events = get_created_events(username)
        table = self.createTable(events, username, to_remove=True)
        layout.addWidget(table)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account(username))
        layout.addWidget(back_btn, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_containers(self, username):
        layout = QVBoxLayout()
        name = QTitleLabel("Create Containers")

        label = QLabel("Number of Containers")
        num = QLineEdit()
        layout.addWidget(name)
        layout.addWidget(label)
        layout.addWidget(num)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self._create_containers(num.text(), username))
        layout.addWidget(button_submit, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def _create_containers(self, num, username):
        num = int(num)
        success = create_cont(num)

        if success:
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("Containers created")
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Container creation failed")
            msg.exec_()

        self.my_account(username)

    def remove_event(self, username, id):
        delete_event(username, id)
        self.delete_events(username)


    def logout(self, username):
        logout_(username)
        self.initial()

    def view_others_agenda(self, username):
        self.setMaximumSize(400, 300)
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        label = QTitleLabel("View Other's Agenda")
        layout.addWidget(label)

        label_username = QLabel("Select user")
        layout.addWidget(label_username)

        allusers = get_all_users(username)
        #drop down menu for users
        list_box = QComboBox()
        for user in allusers:
            list_box.addItem(user)
        layout.addWidget(list_box)

        button_submit = QPushButton("View")
        button_submit.clicked.connect(lambda: self.intermediate(username, list_box))
        layout.addWidget(button_submit, alignment = Qt.AlignCenter)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account(username))
        layout.addWidget(back_btn, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def intermediate(self, username, combo_box):
        #get the selected user
        selected_user = combo_box.currentText()
        self.view_agenda(get_meetings(selected_user), username, selected_user)

    def view_agenda(self, agenda, username, other = None):
        self.setMaximumSize(800, 600)
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label = QTitleLabel(f"Agenda: {other if other is not None else username}")
        layout.addWidget(label)

        table = self.createTable(agenda, username) if other is None else self.createTable(agenda, other)
        layout.addWidget(table)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account(username))
        layout.addWidget(back_btn, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def view_pending_meetings(self, username):
        self.setMaximumSize(800, 600)
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label = QTitleLabel("Pending Meetings")
        layout.addWidget(label)

        accepted = get_meetings(username)
        tabulate = get_pending_meetings(username)
        table = self.createTable(tabulate, username, need_to_accept=True, pending=accepted)
        layout.addWidget(table)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account(username))
        layout.addWidget(back_btn, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_meeting(self, username):
        self.setMaximumSize(400, 600)
        self.setGeometry(100, 100, 400, 600)
        layout = QVBoxLayout()

        label = QTitleLabel("Create Meeting")

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

        label_time = QLabel("Start Time (HH:MM)")
        time_input = QLineEdit()
        layout.addWidget(label_time)
        layout.addWidget(time_input)

        end_time_label = QLabel("End Time (HH:MM)")
        end_time_input = QLineEdit()
        layout.addWidget(end_time_label)
        layout.addWidget(end_time_input)

        allusers = get_all_users(username)
        label_users = QLabel("Add Users")
        layout.addWidget(label_users)

        list_widget = QListWidget()
        for user in allusers:
            item = QListWidgetItem(str(user))
            item.setCheckState(0)
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        groups = get_all_groups()
        label_groups = QLabel("Add Groups")
        layout.addWidget(label_groups)

        list_widget_groups = QListWidget()
        for group in groups:
            item = QListWidgetItem(str(group))
            item.setCheckState(0)
            list_widget_groups.addItem(item)
        layout.addWidget(list_widget_groups)

        button_submit = QPushButton("Submit")
        button_submit.clicked.connect(lambda: self.try_create_meeting(meeting_name_input.text(), description_input.text(),
                                                                      time_input.text(), end_time_input.text(), get_Selected_users(list_widget),
                                                                      date_input.selectedDate().toString("yyyy-MM-dd"),
                                                                      get_Selected_users(list_widget_groups), username))
        layout.addWidget(button_submit, alignment = Qt.AlignCenter)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.my_account(username))
        layout.addWidget(back_btn, alignment = Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def try_create_meeting(self, name, description, time, endtime, users, date, groups, username):
        success = create_meeting(name, description, time,endtime, date, users, groups, username)
        msg = QMessageBox()

        if success:
            msg.setWindowTitle("Success")
            msg.setText("Meeting created")
            msg.exec_()
        else:
            msg.setWindowTitle("Error")
            msg.setText("Meeting creation failed")
            msg.exec_()


    def accept_decline(self, username, id):
        #pop up question
        msg = QMessageBox()
        msg.setWindowTitle("Accept meeting")
        msg.setText("Do you want to accept the meeting?")
        accept_btn = QPushButton("Yes")
        decline_btn = QPushButton("No")
        msg.addButton(accept_btn, QMessageBox.AcceptRole)
        msg.addButton(decline_btn, QMessageBox.RejectRole)
        msg.exec_()
        if msg.clickedButton() == accept_btn:
            accept_meeting(username, id)
        else:
            decline_meeting(username, id)

        self.view_pending_meetings(username)


    def createTable(self, agenda : List[AgendaItem], username, need_to_accept = False, pending = None, to_remove=False):
        conflicts = identify_conflicts(agenda, pending)
        table = QTableWidget()
        table.setRowCount(len(agenda))
        table.setColumnCount(5) if not need_to_accept and not to_remove else table.setColumnCount(6)
        headings = ["Name", "Description", "Start", "End", "Date"]
        headings = headings + ["Accept"] if need_to_accept else headings
        headings = headings + ["Accept"] if to_remove else headings
        table.setHorizontalHeaderLabels(headings)
        for i, item in enumerate(agenda):
            table.setItem(i, 0, QTableWidgetItem(item.name))
            table.setItem(i, 1, QTableWidgetItem(item.description))
            table.setItem(i, 2, QTableWidgetItem(item.time_start))
            table.setItem(i, 3, QTableWidgetItem(item.time_end))
            table.setItem(i, 4, QTableWidgetItem(str(item.date)))
            if need_to_accept:
                button = QPushButton("Accept")
                button.clicked.connect(lambda: self.accept_decline(username, item.id))
                table.setCellWidget(i, 5, button)
            if to_remove:
                button = QPushButton("Remove")
                button.clicked.connect(lambda: self.remove_event(username, item.id))
                table.setCellWidget(i, 5, button)

            if item.id in conflicts:
                table.item(i, 0).setBackground(QColor(255, 0, 0))
            else:
                table.item(i, 0).setBackground(QColor(0, 255, 0))


        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        return table


#main function
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

