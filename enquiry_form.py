from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
import re
from kivymd.uix.list import OneLineIconListItem, OneLineListItem
import Database
from kivy.lang import Builder
Builder.load_file('enquiry_form.kv')

class EnquiryFormScreen(Screen,MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_name = self.ids.parent_name
        self.student_name = self.ids.student_name
        self.class_name = self.ids.class_name
        self.address = self.ids.address
        self.phone_number1 = self.ids.phone_number1
        self.phone_number2 = self.ids.phone_number2
        self.other_details = self.ids.other_details
        self.follow_date = self.ids.follow_date

        d_items = ['enquiry', "interested", "confirm", 'rejected']
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": i,
                "height": dp(40),
                "on_release": lambda x=i: self.set_item(x),
            } for i in d_items
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=menu_items,
            position="center",
            width_mult=2,
        )
        self.menu.bind()

    def set_item(self, text_item):
        self.ids.drop_item.text = text_item
        self.menu.dismiss()

    def validate_phone_number(self, phone_number_id):
        phone_object = self.ids[phone_number_id]
        phone_text = str(phone_object.text)

        if 1 <= len(phone_text) < 10:
            phone_object.error = True
            phone_object.line_color = (1, 0, 0, 1)  # set line color to red
        else:
            phone_object.error = False
            phone_object.line_color = (0, 0, 0, 1)  # set line color to default

        return phone_text

    def submit_form(self):
        parents_name = self.parent_name.text
        student_name = self.student_name.text
        class_name = self.class_name.text
        address = self.address.text
        other_details = self.other_details.text
        follow_date = self.follow_date.text
        # Get the value of the selected item in the dropdown menu
        selected_item = self.ids.drop_item.text

        # Check if no item is selected in the dropdown menu
        if selected_item == '':
            content = MDFlatButton(text='OK', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Error!', text='Please select an item in the dropdown menu.',
                                   buttons=[content])
            self.dialog.open()
            return

        # get the value of the phone number text field as a string
        phone1 = self.validate_phone_number('phone_number1')
        phone2 = self.validate_phone_number('phone_number2')



        # Phone 1 ensure that the phone number only contains digits
        # check if phone1 or phone2 is blank, then skip the if condition
        if phone1 and not re.match("^[0-9]+$", phone1):
            content = MDFlatButton(text='OK', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Phone Number !', text='Digits Only.', buttons=[content])
            self.dialog.open()
            return

        # Phone 1 ensure that the phone number has ten digits
        if phone1 and len(phone1) != 10:
            content = MDFlatButton(text='OK', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Phone Number !', text='Must be 10 Digits', buttons=[content])
            self.dialog.open()
            return

        # check if phone2 is blank, then skip the if condition
        if phone2 and not re.match("^[0-9]+$", phone2):
            content = MDFlatButton(text='OK', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Phone Number !', text='Digits Only.', buttons=[content])
            self.dialog.open()
            return

        # Phone 2 ensure that the phone number has ten digits
        if phone2 and len(phone2) != 10:
            content = MDFlatButton(text='OK', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Phone Number !', text='Must be 10 Digits', buttons=[content])
            self.dialog.open()
            return

        if parents_name == '' and student_name == '' and class_name == '' and address == '' and phone1 == '' and phone2 == '' and other_details == '' and follow_date == '':
             print("Please input value")
             dialog = MDDialog(
                 title="Error !!!",
                 text="Please Enter Details!",
                 buttons=[
                     MDFlatButton(
                         text="OK",
                         on_release=lambda *args: dialog.dismiss()
                     )
                 ]
             )
             dialog.open()
        else:

             Database.put_data(parents_name, student_name, class_name, address, phone1, phone2, other_details, follow_date,selected_item)

             # Refresh the enquiry list screen
             enquiry_list_screen = self.manager.get_screen('enquiry_list')
             enquiry_list_screen.load_data()

             # changing screen
             #self.manager.current = 'enquiry_list'
             # form submit dialog box
             content = MDFlatButton(text='OK', on_release=self.close_dialog)
             self.dialog = MDDialog(title='Form Submitted !', text='Successfully.',
                                   buttons=[content])

             self.dialog.open()



    def reset_form(self):
        # Reset all the text fields to their default values
        self.parent_name.text = ''
        self.student_name.text = ''
        self.class_name.text = ''
        self.address.text = ''
        self.phone_number1.text = ''
        self.phone_number2.text = ''
        self.follow_date.text = ''
        self.other_details.text = ''
        self.follow_date.text = ''


        # Reset the color of all fields to default
        self.ids.phone_number1.error = False
        self.ids.phone_number1.line_color = (0, 0, 0, 1)
        self.ids.phone_number2.error = False
        self.ids.phone_number2.line_color = (0, 0, 0, 1)

        # form clear dialog box
        content = MDFlatButton(text='OK', on_release=self.close_dialog)
        self.dialog = MDDialog(title='Form Clear!', text='Successfully.',
                               buttons=[content])
        self.dialog.open()


    def close_dialog(self, obj):
        # Close the dialog box
        self.dialog.dismiss()