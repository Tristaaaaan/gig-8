
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from enquiry_form import EnquiryFormScreen
from enquirylist import EnquiryListScreen
from chatscreen import ChatScreen
from loginscreen import LoginScreen, SignupScreen

from kivy.properties import ListProperty, StringProperty, NumericProperty, DictProperty
from kivy.lang import Builder
from configparser import ConfigParser
import ssl
from enquirylist import ChatListItem  # for list item count update
from Database import DatabaseManager, LocalStorage


Builder.load_file('enquiryscreen_main.kv')
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:

    pass
else:
    ssl._create_default_htttps_context = _create_unverified_https_context


class MainScreen(Screen):
    username = StringProperty('')
    enquiry_count = NumericProperty(0)
    interested_count = NumericProperty(0)
    confirm_count = NumericProperty(0)
    rejected_count = NumericProperty(0)
    count_types = ['enquiry', 'interested', 'confirm', 'rejected']
    counts = DictProperty({count_type: NumericProperty(0)
                          for count_type in count_types})
    # counts = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counts = {count_type: 0 for count_type in self.count_types}

    def update_counts(self):
        enquiry_list_screen = self.manager.get_screen('enquiry_list')
        count_dict = {'enquiries_list': 'enquiry_count', 'interested_list': 'interested_count',
                      'confirm_list': 'confirm_count', 'rejected_list': 'rejected_count'}

        for list_id, count_property in count_dict.items():
            setattr(self, count_property, len([child for child in getattr(enquiry_list_screen.ids, list_id).children
                                               if isinstance(child, ChatListItem)]))

    def logout(self, instance):
        self.manager.get_screen('login').logout()

    def on_enter(self):
        config = ConfigParser()
        config.read('config.ini')
        if not config.getboolean('login', 'logged_in'):
            self.manager.current = 'login'
        else:
            self.username = config.get('login', 'username')

    def on_pre_enter(self):      # for list item count update
        self.update_counts()


class ScreenInitializer:
    def __init__(self):
        self.sm = ScreenManager()

    def initialize_screens(self):
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(SignupScreen(name='signup'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(EnquiryFormScreen(name='enquiry_form'))
        self.sm.add_widget(EnquiryListScreen(name='enquiry_list'))
        self.sm.add_widget(ChatScreen(name='chat'))
        return self.sm


class Admission_enquiry(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.config = ConfigParser()
        self.screen_initializer = ScreenInitializer()

    def build(self):
        self.db_manager.load_data_from_database()
        self.config.read('config.ini')

        sm = self.screen_initializer.initialize_screens()
        sm.current = 'login'
        sm.get_screen('main').username = self.config.get('login', 'username')
        if self.config.getboolean('login', 'logged_in'):
            sm.current = 'main'
        return sm


if __name__ == '__main__':

    Admission_enquiry().run()
