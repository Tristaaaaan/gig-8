from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivy.config import Config
from Database import verify_credentials, register_user
from kivy.lang import Builder
from configparser import ConfigParser

# Create the 'login' section if it doesn't exist
if not Config.has_section('login'):
    Config.add_section('login')
# Set up the configuration options
Config.set('login', 'remember', '0')
Config.set('login', 'logged_in', '0')


# Load the KV file
Builder.load_file('login.kv')

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize the config parser
        self.config = ConfigParser()
        self.config.read('config.ini')

    def save_config(self):
        # Save the changes to the config file
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def show_dialog(self, title, text, close_callback):
        content = MDFlatButton(text='OK', on_release=close_callback)
        self.dialog = MDDialog(title=title, text=text, buttons=[content])
        self.dialog.open()


class LoginScreen(BaseScreen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    remember_checkbox = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize the config parser
        self.config = ConfigParser()
        self.config.read('config.ini')

        # Set the username and password fields if they were previously saved
        self.ids.username.text = self.config.get('login', 'username', fallback='')
        self.ids.password.text = self.config.get('login', 'password', fallback='')

        # Assign the 'remember_checkbox' widget to the ObjectProperty
        #self.remember_checkbox = self.ids.remember_checkbox

    def verify_credentials(self):
        entered_username = self.ids.username.text
        entered_password = self.ids.password.text
        if verify_credentials(entered_username, entered_password):
            # Set the 'logged_in' config value to '1'
            self.config.set('login', 'logged_in', '1')

            # Save the username and password
            self.config.set('login', 'username', entered_username)
            self.config.set('login', 'password', entered_password)

            # Set the 'remember' config value to '1'
            self.config.set('login', 'remember', '1')

            # Save the changes to the config file
            self.config.write(open('config.ini', 'w'))

            self.manager.current = 'main'

            self.manager.get_screen('main').username = entered_username
        else:
            # Show an error dialog box
            self.show_dialog('Login Error!', 'Invalid credentials!', self.close_dialog)

        # Save the changes to the config file
        self.save_config()

    def logout(self):
        #self.manager.current = 'login'
        # Set the 'logged_in' and 'username' config values to '0' and ''
        #self.config.set('login', 'logged_in', '0')
        #self.config.set('login', 'username', '')  # set username to ''
        #self.config.write(open('config.ini', 'w'))

        # Create the dialog content
        content = "Do you want to log out?"

        # Create the buttons
        yes_button = MDFlatButton(text="Yes", on_release=self.confirm_logout)
        no_button = MDFlatButton(text="No", on_release=self.close_dialog)

        # Create and show the dialog
        self.dialog = MDDialog(title="Log Out", text=content, buttons=[yes_button, no_button], size_hint=(0.8, 0.4))
        self.dialog.open()



    def confirm_logout(self, instance):
        # Close the dialog
        self.dialog.dismiss()

        # Initialize the config parser
        config = ConfigParser()
        config.read('config.ini')

        # Set the 'logged_in' config value back to '0'
        config.set('login', 'logged_in', '0')

        # Clear the username and password
        #config.remove_option('login', 'username')
        config.set('login', 'username', '')
        config.remove_option('login', 'password')

        # Set the 'remember' config value back to '0'
        config.set('login', 'remember', '0')

        # Save the changes to the config file
        config.write(open('config.ini', 'w'))

        # Empty the text fields
        self.ids.username.text = ''
        self.ids.password.text = ''

        self.manager.current = 'login'



    def close_dialog(self, obj):
        # Save the changes to the config file
        self.save_config()
        self.dialog.dismiss()

class SignupScreen(BaseScreen):
    username = ObjectProperty(None)
    full_name = ObjectProperty(None)
    password = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def signup(self):
        username = self.ids.username.text
        full_name = self.ids.full_name.text
        password = self.ids.password.text

        # Validate the values
        # Validate the values
        if not all([username, full_name, password]):
            self.show_dialog('SignUp Error !', 'Invalid credentials !', self.close_dialog)

        # Insert the data into the database
        register_user(username, full_name, password)

        # Display a success message
        content = MDFlatButton(text='OK', on_release=self.close_dialog_success)
        self.dialog = MDDialog(title='Success', text='SignUp Successfully',
                               buttons=[content])
        self.dialog.open()

        # Clear the input fields
        self.ids.username.text = ''
        self.ids.full_name.text = ''
        self.ids.password.text = ''

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def close_dialog_success(self, obj):
        self.manager.current = 'login'
        self.dialog.dismiss()



