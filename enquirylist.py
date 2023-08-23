#from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
#from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, OneLineListItem
from kivymd.uix.tab import MDTabs, MDTabsBase
#from kivymd.uix.button import MDIconButton
#from datetime import datetime
#from kivy.clock import Clock
#from kivy.core.clipboard import Clipboard
#from kivy.uix.dropdown import DropDown
#from kivymd.uix.menu import MDDropdownMenu

import Database

Builder.load_file('enquirylist.kv')

class ChatListItem(OneLineListItem):
    #icon = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print(f"Touched item name: {self.text}")
            list_name = self.text.split('. ')[-1]
            return super().on_touch_down(touch)

class Tab(MDLabel, MDTabsBase):
    title = ""

class EnquiryListScreen(Screen):
    parents_name = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_data()

    def chat_ListScreen(self, list_name):
        self.manager.current = 'chat'
        self.manager.get_screen('chat').display_data(list_name)

    def load_data(self):

        self.ids.enquiries_list.clear_widgets()
        self.ids.interested_list.clear_widgets()
        self.ids.confirm_list.clear_widgets()
        self.ids.rejected_list.clear_widgets()

        result = Database.view_data()
        print(result)
        self.parents_name = [row['parents_name'] for row in reversed(result)]
        #self.parents_name = [row[0] for row in reversed(result)]


        index_map = {"enquiry": 1, "interested": 1, "confirm": 1, "rejected": 1}
        widget_map = {"enquiry": self.ids.enquiries_list, "interested": self.ids.interested_list,
                      "confirm": self.ids.confirm_list, "rejected": self.ids.rejected_list}

        #for name, class_name, status in [(row[0], row[2], row[10]) for row in reversed(result)]:
        for name, class_name, status in [(row['parents_name'], row['class_name'], row['status']) for row in
                                         reversed(result)]:

            item_text = f"{name} ({class_name})"
            if status in index_map:
                chat_list_item = ChatListItem(id=name, text=f"{index_map[status]}. {item_text}",
                                              on_release=lambda instance, name=name: self.chat_ListScreen(name))
                widget_map[status].add_widget(chat_list_item)
                index_map[status] += 1


        #self.update_counts() # for updating total list item available in the list

    def find_chat_item(self, list_name):
        chat_item = None
        current_tab = None
        for child in self.ids.enquiries_list.children:
            if isinstance(child, ChatListItem) and list_name in child.text:
                chat_item = child
                current_tab = "enquiry"
                break

        if not chat_item:
            for child in self.ids.interested_list.children:
                if isinstance(child, ChatListItem) and list_name in child.text:
                    chat_item = child
                    current_tab = "interested"
                    break

        if not chat_item:
            for child in self.ids.confirm_list.children:
                if isinstance(child, ChatListItem) and list_name in child.text:
                    chat_item = child
                    current_tab = "confirm"
                    break

        if not chat_item:
            for child in self.ids.rejected_list.children:
                if isinstance(child, ChatListItem) and list_name in child.text:
                    chat_item = child
                    current_tab = "rejected"
                    break

        return chat_item, current_tab

    def update_list_numbers(self, list_widget, start_number=1):
        for i, chat_item in enumerate(list_widget.children[::-1], start=start_number):
            if hasattr(chat_item, 'text'):
                chat_item.text = f"{i}. {chat_item.text.split('.')[-1]}"

    def get_list_number(self, target_list):
        return len([child for child in target_list.children if isinstance(child, ChatListItem)]) + 1

    def move_to_interested(self, list_name):
        chat_item, current_tab = self.find_chat_item(list_name)

        if chat_item and current_tab != "interested":
            first_time_moving = current_tab == "enquiry"

            if current_tab == "enquiry":
                self.ids.enquiries_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.enquiries_list, start_number=1)
            elif current_tab == "confirm":
                self.ids.confirm_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.confirm_list)
            elif current_tab == "rejected":
                self.ids.rejected_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.rejected_list)

            next_number = self.get_list_number(self.ids.interested_list)
            chat_item.text = f"{next_number}. {chat_item.text.split('. ')[-1]}"

            self.ids.interested_list.add_widget(chat_item)

            if first_time_moving:
                self.update_list_numbers(self.ids.interested_list)

            Database.update_status(list_name, "interested")  # Update the database

        #self.update_counts()  # for updating total list item available in the list

    def move_to_confirm(self, list_name):
        chat_item, current_tab = self.find_chat_item(list_name)

        if chat_item and current_tab != "confirm":
            first_time_moving = current_tab == "interested"

            if current_tab == "enquiry":
                self.ids.enquiries_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.enquiries_list, start_number=1)
            elif current_tab == "interested":
                self.ids.interested_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.interested_list)
            elif current_tab == "rejected":
                self.ids.rejected_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.rejected_list)

            next_number = self.get_list_number(self.ids.confirm_list)
            chat_item.text = f"{next_number}. {chat_item.text.split('. ')[-1]}"

            self.ids.confirm_list.add_widget(chat_item)

            if first_time_moving:
                self.update_list_numbers(self.ids.confirm_list)

            Database.update_status(list_name, "confirm")  # Update the database

        #self.update_counts()  # for updating total list item available in the list

    def move_to_rejected(self, list_name):
        chat_item, current_tab = self.find_chat_item(list_name)

        if chat_item and current_tab != "rejected":
            if current_tab == "enquiry":
                self.ids.enquiries_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.enquiries_list, start_number=1)
            elif current_tab == "interested":
                self.ids.interested_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.interested_list)
            elif current_tab == "confirm":
                self.ids.confirm_list.remove_widget(chat_item)
                self.update_list_numbers(self.ids.confirm_list)

            next_number = self.get_list_number(self.ids.rejected_list)
            chat_item.text = f"{next_number}. {chat_item.text.split('. ')[-1]}"

            self.ids.rejected_list.add_widget(chat_item)

            self.update_list_numbers(self.ids.rejected_list)

            Database.update_status(list_name, "rejected")  # Update the database

        #self.update_counts()  # for updating total list item available in the list

    def on_enter(self, *args):        # for list item count update
        super().on_enter(*args)

        enquiry_count = len(self.ids.enquiries_list.children)
        interested_count = len(self.ids.interested_list.children)
        confirm_count = len(self.ids.confirm_list.children)
        rejected_count = len(self.ids.rejected_list.children)

        main_screen = self.manager.get_screen('main')
        main_screen.enquiry_count = enquiry_count
        main_screen.interested_count = interested_count
        main_screen.confirm_count = confirm_count
        main_screen.rejected_count = rejected_count


