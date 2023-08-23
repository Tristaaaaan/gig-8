from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton
from datetime import datetime
from kivy.core.clipboard import Clipboard
from kivymd.uix.menu import MDDropdownMenu
import webbrowser  # phone call
from datetime import datetime, timedelta

import Database

Builder.load_file('chat_screen.kv')


class MessageBubble(BoxLayout):
    text = StringProperty("")
    selected = BooleanProperty(False)
    datetime = ObjectProperty(datetime.now())  # Add this line
    username = StringProperty()  # New property for the sender's name

    def toggle_selected(self):
        self.selected = not self.selected

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.toggle_selected()
            return True
        return super().on_touch_down(touch)


class DatabaseHandler:
    @staticmethod
    def remove_message(list_name, message_to_remove, message_datetime_to_remove):
        result = Database.view_data()
        for row in result:
            if row[0] == list_name:
                messages = row[8]
                message_datetimes = row[9]
                usernames = row[11]

                if messages is not None:
                    messages_list = messages.split("||")
                    message_datetimes_list = message_datetimes.split("||")
                    usernames_list = usernames.split("||")
                else:
                    messages_list = []
                    message_datetimes_list = []
                    usernames_list = []

                index_to_remove = messages_list.index(message_to_remove)
                messages_list.pop(index_to_remove)
                message_datetimes_list.pop(index_to_remove)
                usernames_list.pop(index_to_remove)

                new_messages = "||".join(messages_list)
                new_message_datetimes = "||".join(message_datetimes_list)
                new_usernames = "||".join(usernames_list)

                Database.update_data(
                    list_name, new_messages, new_message_datetimes, new_usernames)
                break


class SelectionMenu(BoxLayout):
    text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(40)
        copy_button = MDIconButton(
            icon="content-copy", on_release=self.copy_text)
        delete_button = MDIconButton(
            icon="delete", on_release=self.delete_text)
        self.add_widget(copy_button)
        self.add_widget(delete_button)

    def copy_text(self, *args):
        Clipboard.copy(self.parent.text)
        self.parent.toggle_selected()

    # def delete_text(self, *args):
        # self.parent.parent.remove_widget(self.parent)
    def delete_text(self, *args):
        print('delete')
        now = datetime.now()
        five_minutes_ago = now - timedelta(minutes=5)
        if self.parent.datetime < five_minutes_ago:
            return

        self.parent.parent.remove_widget(self.parent)

        list_name = self.parent.parent.parent.list_name
        message_to_remove = self.parent.text
        message_datetime_to_remove = self.parent.datetime.strftime(
            '%Y-%m-%d %H:%M:%S')

        DatabaseHandler.remove_message(
            list_name, message_to_remove, message_datetime_to_remove)


class DatabaseInterface:
    @staticmethod
    def get_data_by_list_name(list_name):
        result = Database.view_data()
        for row in result:
            if row['parents_name'] == list_name:
                return row
        return None

    @staticmethod
    def update_chat_data(list_name, message, message_datetime, username):
        row = DatabaseInterface.get_data_by_list_name(list_name)
        new_messages = row['message'] + "||" + \
            message if row['message'] else message
        new_message_datetime = row['message_datetime'] + "||" + \
            message_datetime if row['message_datetime'] else message_datetime
        new_usernames = row['username'] + "||" + \
            username if row['username'] else username
        Database.update_data(list_name, new_messages,
                             new_message_datetime, new_usernames)


class ChatScreen(Screen):
    nav_drawer = ObjectProperty(None)
    list_name = StringProperty("")
    username = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        items_d = ['Interested', 'Confirm', 'Rejected']
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "height": dp(40),
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            } for i in items_d
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.chat,
            items=menu_items,
            width_mult=2,
        )

    def menu_callback(self, text_item):
        print(text_item)
        if text_item == "Interested":
            self.manager.get_screen(
                'enquiry_list').move_to_interested(self.list_name)
        elif text_item == "Confirm":
            self.manager.get_screen(
                'enquiry_list').move_to_confirm(self.list_name)
        elif text_item == "Rejected":
            self.manager.get_screen(
                'enquiry_list').move_to_rejected(self.list_name)
        self.menu.dismiss()

    def display_data(self, list_name):
        self.list_name = list_name
        self.ids.chat_messages.clear_widgets()
        row = DatabaseInterface.get_data_by_list_name(list_name)
        self._update_ui_with_data(row)

    def _update_ui_with_data(self, row):
        self.ids.chat.title = row['parents_name']
        self.ids.parents_name_label.text = row['parents_name']
        self.ids.student_name_label.text = row['student_name']
        self.ids.class_name_label.text = row['class_name']
        self.ids.address_name_label.text = row['address']
        self.ids.phone1_label.text = str(row['phone1'])
        self.ids.phone2_label.text = str(row['phone2'])
        self.ids.other_details_label.text = row['other_details']
        self.ids.follow_date_label.text = str(row['follow_date'])
        self.username = row['username'] if row['username'] is not None else "Unknown User"

        messages = row['message'].split("||") if row['message'] else []
        message_datetimes = row['message_datetime'].split(
            "||") if row['message_datetime'] else []
        usernames = row['username'].split("||") if row['username'] else []
        for i, message in enumerate(messages):
            if message:
                message_datetime = datetime.strptime(message_datetimes[i],
                                                     '%Y-%m-%d %H:%M:%S') if message_datetimes and len(
                    message_datetimes) > i else datetime.now()
                username = usernames[i] if usernames and len(
                    usernames) > i else "Unknown User"
                self.ids.chat_messages.add_widget(
                    MessageBubble(text=message, datetime=message_datetime, username=username))

    def send_message(self, message):
        if message:
            message_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            username = self.manager.get_screen('main').username
            self.ids.chat_messages.add_widget(
                MessageBubble(
                    text=message, datetime=datetime.now(), username=username)
            )
            self.ids.text_input.text = ""
            DatabaseInterface.update_chat_data(
                self.list_name, message, message_datetime, username)

            # Call display_data to refresh the data from database
            # self.display_data(self.list_name)

    # phone call
    def on_phone1_press(self):
        phone_number = self.ids.phone1_label.text
        self.open_phone_dialer(phone_number)

    def on_phone2_press(self):
        phone_number = self.ids.phone2_label.text
        self.open_phone_dialer(phone_number)

    def open_phone_dialer(self, phone_number):
        url = f"tel:{phone_number}"
        webbrowser.open(url)
