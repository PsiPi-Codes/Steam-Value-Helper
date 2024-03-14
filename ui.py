from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import Screen
from main import MainLogic
import globals

Window.size = (395, 730)
Window.minimum_width = 395
Window.minimum_height = 730

class SteamValue(MDApp):    
    
    def build(self):
        
        
        self.MainLogic = MainLogic()
        
        self.theme_cls.theme_style = "Dark"
        
        self.layout = MDBoxLayout(orientation='vertical')
        self.app_list = MDDataTable(
            use_pagination=True,
            check=False,
            column_data=[
                ("", dp(10)),
                ("Name", dp(30)),
                ("Value", dp(30))
            ],
            size_hint=(1, 2)
        )
        
        self.app_list.bind(on_row_press=self.on_row_press)
         
        self.current_app_layout = MDGridLayout(cols=1, rows=2, orientation='lr-tb')
        self.current_app_name = MDLabel(text='', font_style='H5', halign='center')
        self.current_app_value = MDLabel(text='', font_style='H3', halign='center', valign='center', size_hint=(1, 4))
        self.current_app_layout.add_widget(self.current_app_name)
        self.current_app_layout.add_widget(self.current_app_value)
        self.top_window_bar = MDTopAppBar()
        self.top_window_bar.right_action_items = [
            ['account-circle', self.set_account_screen]
        ]
        self.bottom_window_bar = MDBottomAppBar(MDTopAppBar(left_action_items=[
            ['help-circle', self.help_pop_up]
        ], right_action_items=[
            ['information', self.set_about_screen]
        ], icon='loupe', type='bottom', id='bottom_window_bar'))
        
        self.bottom_window_bar.children[1].bind(on_action_button=self.set_expand_current_app_screen)
        
        self.home_layout = Screen(name='home')
        self.home_box_layout = MDGridLayout(cols=1, rows=2, orientation='lr-tb')
        self.home_box_layout.add_widget(self.current_app_layout)
        self.home_box_layout.add_widget(self.app_list)
        self.home_layout.add_widget(self.home_box_layout)
        
        
        self.about_layout = Screen(name='about')
        self.about_layout.add_widget(MDLabel(text='test_about'))
        
        self.account_layout = Screen(name='account')
        self.account_layout.add_widget(MDLabel(text="test_account"))
        
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(self.home_layout)
        self.screen_manager.add_widget(self.account_layout)
        self.screen_manager.add_widget(self.about_layout)
        
        
        self.layout.add_widget(self.top_window_bar)
        self.layout.add_widget(self.screen_manager)
        self.layout.add_widget(self.bottom_window_bar)
        
        
        self.first_time_logic()
        
        return self.layout

    def generate_app_list(self):
        i = 0
        for value in self.MainLogic.fetch_file_app_list():
            self.app_list.add_row([i] + value)
            i += 1

    def first_time_logic(self):
        if globals.current_user == "":
            users = self.MainLogic.find_users()
            first_time_user_select_screen = Screen(name='user')
            self.screen_manager.add_widget(first_time_user_select_screen)
            user_select_layout = MDRelativeLayout()
            user_select_text = MDLabel(font_style = 'H5', text='Thank you for using SteamValue! It seems there is at least one account connected to your Steam, select it from the dropdown or just ignore this!', halign='center')
            user_select_menu_button = MDRaisedButton(text='Select', pos_hint={'x':0 , 'y':0.25 }, size_hint=(1, 0))
            
            user_menu_items = []
            for user in users:
                user_menu_items.append(
                    {
                    'viewclass' : 'OneLineListItem',
                    'text': users[user]['PersonaName'], 
                    'on_release': lambda x=user: self.selected_user(x)
                    }
                )
            
            user_select_menu = MDDropdownMenu(caller = user_select_menu_button, items = user_menu_items, width_mult = 4)
            
            user_select_menu_button.bind(on_release = lambda x : user_select_menu.open())
            
            self.screen_manager.transition = SlideTransition(direction='right')
            self.set_back_button('close')
            self.screen_manager.current = 'user'
            first_time_user_select_screen.add_widget(user_select_layout)
            user_select_layout.add_widget(user_select_text)
            user_select_layout.add_widget(user_select_menu_button)
            
        else:
            self.generate_app_list()
    
    def selected_user(self, user):
        globals.current_user = user
        self.generate_app_list()
        self.screen_manager.current = 'home'
    
    def on_row_press(self, instance_table, instance_row):
        # get start index from selected row item range
        start_index, end_index = instance_row.table.recycle_data[instance_row.index]['range']
        app_index = instance_row.table.recycle_data[start_index]['text']
        app = self.MainLogic.fetch_file_app_info(int(app_index))
        self.current_app_name.text = app[0]
        self.current_app_value.text = app[1]
        
    def set_account_screen(self, temp):
        print('account screen!')
        self.screen_manager.transition = SlideTransition(direction='left')
        self.screen_manager.current = 'account'
        self.set_back_button('arrow-left')
    
    def help_pop_up(self, temp):
        print('pop up!')
        dialog = MDDialog(text='Select a game from the list, then press the magnify button for more info. \n\nYou can connect your steam account, set up a custom steam API key, and set a password in the account page!')
        dialog.open()
     
    def set_about_screen(self, temp):
        print('info!')
        self.screen_manager.transition = SlideTransition(direction='up')
        self.screen_manager.current = 'about'
        self.set_back_button('arrow-up')
    

    def set_back_button(self, icon):
        self.bottom_window_bar.children[0].icon = icon
        self.bottom_window_bar.children[1].bind(on_action_button=self.return_to_home)
        
    def set_expand_current_app_screen(self, temp):
        print('expand')
    
    def return_to_home(self, temp):
        print('return!')
        if self.screen_manager.current == 'account':
            self.screen_manager.transition = SlideTransition(direction='right')
        elif self.screen_manager.current == 'about':
            self.screen_manager.transition = SlideTransition(direction='down')
        else:
            self.screen_manager.transition = SlideTransition(direction='left')
        self.screen_manager.current = 'home'
        self.bottom_window_bar.children[0].icon = 'loupe'
        self.bottom_window_bar.children[1].bind(on_action_button=self.set_expand_current_app_screen)

SteamValue().run()