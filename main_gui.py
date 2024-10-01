"""

Main GUI: Main module for TLoD Assets Manager GUI, 
here only exist the GUI code

Version: Beta 0.1

GUI Module: PyQt

Copyright (C) 2024 DooMMetaL


"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QDialog, QLabel, QGridLayout, QComboBox, QLineEdit, QMessageBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6 import QtCore
import config_handler
import database_handler
from battle_conversion_window import BattleConversionMainWindow
from submap_conversion_window import SubMapConversionMainWindow
from texture_only_conversion_window import TextOnlyConversionMainWindow
#from deff_conversion_window import DeffConversionMainWindow

class MainWindow(QMainWindow):
    def __init__(self, title=str, init_config=dict, init_config_path=str, assets_database=dict, icon=str, bg_img=str):
        super().__init__()
        # Constructor also hold a lot of init data and configurations
        # Get the Start-up Configuration from the file and the Databases already processed
        self.init_config = init_config
        self.init_config_path = init_config_path
        self.assets_database = assets_database
        self.bg_img = bg_img
        self.icon = icon
        # Minimum and Maximum Window Size
        self.setMinimumSize(640, 360)
        self.full_screen_available_x = self.screen().availableGeometry().width()
        self.full_screen_available_y = self.screen().availableGeometry().height()
        self.startup_x = 0
        self.startup_y = 0
        # Default Geometry and Centering the Window
        self.get_startup_resolution()
        self.center_window()
        # Setting Init Visuals
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        # Start the other Widgets after setting the Main Window Properly
        self.initial_window_widgets()
        # Setting Background Image for the Window
        self.set_window_background()
        # Get rid of the Maximize Button
        self.setWindowFlags(QtCore.Qt.WindowType.WindowMinimizeButtonHint | QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.show() #---> This method ALWAYS at the VERY LAST BOTTOM of the options/attributes
    
    def get_startup_resolution(self) -> None:
        """
        Here we get Startup Resolution from the Configuration file
        get_startup_resolution() -> None
        """
        get_startup_resolution_value_x: str = self.init_config.get('SizeX')
        get_startup_resolution_value_y: str = self.init_config.get('SizeY')
        
        if get_startup_resolution_value_x.isdigit():
            self.startup_x = int(get_startup_resolution_value_x)
        else:
            emergency_x_value = 640
            self.startup_x = emergency_x_value
        
        if get_startup_resolution_value_y.isdigit():
            self.startup_y = int(get_startup_resolution_value_y)
        else:
            emergency_y_value = 360
            self.startup_y = emergency_y_value

    def center_window(self):
        screen_empty_space_x = self.full_screen_available_x - self.startup_x
        screen_empty_space_y = self.full_screen_available_y - self.startup_y
        divided_screen_space_x = screen_empty_space_x // 2
        divided_screen_space_y = (screen_empty_space_y // 2) + 40
        self.setGeometry(divided_screen_space_x, divided_screen_space_y, self.startup_x, self.startup_y)

    def initial_window_widgets(self):
        # Create Background Image and Main Widget container
        self.main_background_image = QWidget(self)
        self.main_background_image.setObjectName("BackgroundImageMain")
        self.setCentralWidget(self.main_background_image)
        # Create Widgets Layout
        self.main_buttons_layout = QGridLayout(self.main_background_image)
        # Buttons Creation
        self.configuration_button = QPushButton('CONFIG')
        self.about_button = QPushButton('About')
        self.convert_batttle_models_button = QPushButton('Convert Battle Models')
        self.convert_submap_models_button = QPushButton('Convert SubMap Models')
        self.convert_texture_only_button = QPushButton('Textures Only')
        self.convert_deff_button = QPushButton('Convert DEFF')
        # Set Widgets Minimums and Maximum Sizes
        self.convert_batttle_models_button.setMaximumSize(150, 100)
        self.convert_submap_models_button.setMaximumSize(150, 100)
        self.convert_texture_only_button.setMaximumSize(150, 100)
        self.convert_deff_button.setMaximumSize(150, 100)
        self.configuration_button.setMaximumSize(150, 100)
        self.about_button.setMaximumSize(150, 100)
        # Widgets Tooltips
        self.convert_batttle_models_button.setToolTip('Convert Models and Textures from Battles TLoD')
        self.configuration_button.setToolTip('Configure the Tool to your needs...')
        self.about_button.setToolTip('Show up the About window...')
        self.convert_submap_models_button.setToolTip('Convert Models and Textures from SubMaps TLoD')
        self.convert_texture_only_button.setToolTip('Convert Textures that are not associated directly to a Model in TLoD')
        self.convert_deff_button.setToolTip('Convert DEFF Files into a Single Scene')
        # Set the Layout to place the objects in the Window
        self.main_background_image.setLayout(self.main_buttons_layout)
        # Configure Layout
        self.main_buttons_layout.setColumnMinimumWidth(0, 25)
        self.main_buttons_layout.setRowStretch(0, 100)
        # Add Widgets to the Layout
        self.main_buttons_layout.addWidget(self.convert_batttle_models_button,0,1)
        self.main_buttons_layout.addWidget(self.convert_submap_models_button,0,2)
        self.main_buttons_layout.addWidget(self.convert_texture_only_button,0,3)
        self.main_buttons_layout.addWidget(self.convert_deff_button,2,2)
        self.main_buttons_layout.addWidget(self.configuration_button,2,0)
        self.main_buttons_layout.addWidget(self.about_button,3,0)
        # Pressing Buttons bindings
        self.configuration_button.clicked.connect(self.configure_tool_window)
        self.about_button.clicked.connect(self.about_asset_manager)
        self.convert_batttle_models_button.clicked.connect(self.battle_conversion_window)
        self.convert_submap_models_button.clicked.connect(self.submap_conversion_window)
        self.convert_texture_only_button.clicked.connect(self.textonly_conversion_window)
        self.convert_deff_button.setDisabled(True)
        #self.convert_deff_button.clicked.connect(self.deff_conversion_window)

    def set_window_background(self):
        self.main_background_image.setStyleSheet("QWidget#BackgroundImageMain {background-image: url(\""+ self.bg_img + "\");" + "background-repeat: no-repeat;}")
    
    def configure_tool_window(self):
        # Objects creation
        self.configuration_window = QDialog(self)
        resolution_combobox_label = QLabel(self.configuration_window)
        self.resolution_combobox = QComboBox(self.configuration_window)
        change_sc_folder_view_label = QLabel(self.configuration_window)
        self.change_sc_folder_view = QLineEdit(self.configuration_window)
        change_sc_folder_button = QPushButton(self.configuration_window)
        change_deploy_folder_view_label = QLabel(self.configuration_window)
        self.change_deploy_folder_view = QLineEdit(self.configuration_window)
        change_deploy_folder_button = QPushButton(self.configuration_window)
        self.save_config_button = QPushButton(self.configuration_window)
        self.cancel_config_button = QPushButton(self.configuration_window)
        # Configure_Labels and Buttons
        change_sc_folder_button.setText('Change SC Files Folder')
        change_deploy_folder_button.setText('Change Deploy Files Folder')
        resolution_combobox_label.setText('Select a Resolution')
        change_sc_folder_view_label.setText('Current SC Folder')
        change_deploy_folder_view_label.setText('Current Deploy Folder')
        self.save_config_button.setText('SAVE CONFIG')
        self.cancel_config_button.setText('CANCEL')
        self.cancel_config_button.setDefault(True)
        # Labels Text Show
        self.change_sc_folder_view.setText(f'{self.init_config.get('SC_Folder')}')
        self.change_deploy_folder_view.setText(f'{self.init_config.get('Deploy_Folder')}')
        # Tooltips
        self.resolution_combobox.setToolTip('Change the tool Resolution')
        change_sc_folder_button.setToolTip('Change SC files folder to a desired one.\nRemember that files folder must exist')
        change_deploy_folder_button.setToolTip('Change Deploy files folder to a desired one.\nTo avoid problems, we recommend do not using the same folder\nas Severed Chains')
        self.save_config_button.setToolTip('Save the current Configuration into the config file')
        self.cancel_config_button.setToolTip('Cancel the current configuration and keeps everything as it is')

        # Generate Layout
        configuration_window_layout = QGridLayout()
        # Positioning Labels and Other Widgets
        configuration_window_layout.addWidget(resolution_combobox_label,1,0)
        configuration_window_layout.addWidget(self.resolution_combobox,1,2,1,1)
        configuration_window_layout.addWidget(change_sc_folder_view_label,2,0)
        configuration_window_layout.addWidget(self.change_sc_folder_view,2,2,1,6)
        configuration_window_layout.addWidget(change_sc_folder_button,3,2)
        configuration_window_layout.addWidget(change_deploy_folder_view_label,4,0)
        configuration_window_layout.addWidget(self.change_deploy_folder_view,4,2,1,6)
        configuration_window_layout.addWidget(change_deploy_folder_button,7,2)
        configuration_window_layout.addWidget(self.save_config_button,8,0)
        configuration_window_layout.addWidget(self.cancel_config_button,8,7)
        configuration_window_layout.setVerticalSpacing(30)
        configuration_window_layout.setHorizontalSpacing(30)
        change_sc_folder_button.setMinimumHeight(50)
        change_deploy_folder_button.setMinimumHeight(50)
        self.save_config_button.setMinimumSize(150, 100)
        self.cancel_config_button.setMinimumSize(150, 100)
        # Configure top bar and Layout
        self.configuration_window.setWindowTitle('Configuration')
        self.configuration_window.setLayout(configuration_window_layout)
        # Size and place Configuration for Configuration Window
        self.configuration_window.setMinimumSize(640, 360)
        self.configuration_window.setModal(True)
        # ComboBox Data Fill
        self.calculate_resolution_to_list()
        # Configure Buttons
        self.change_sc_folder_view.setDisabled(True)
        self.change_deploy_folder_view.setDisabled(True)
        # Show the window
        self.configuration_window.show()

        # Buttons Bindings
        change_sc_folder_button.clicked.connect(self.change_sc_folder)
        change_deploy_folder_button.clicked.connect(self.change_deploy_folder)
        self.save_config_button.clicked.connect(self.save_current_config)
        self.cancel_config_button.clicked.connect(self.cancel_current_config)
    
    def calculate_resolution_to_list(self):
        """
        Calculate Resolution List: this method will calculate all the available resolution for the tool
        based in the current monitor desktop resolution
        first one is the current resolution, then cames the "maximimum" and after the rest of possibles value for 16:9
        """
        full_screen_available_string = f'{self.full_screen_available_x}x{self.full_screen_available_y}'
        default_listed = [[self.startup_x, self.startup_y], [7680, 4320], [3840, 2160], [2560, 1440], [1920, 1080], [1280, 720], [854, 480], [640, 360]]
        calculated_resolution_list = []
        for check_on_this_resolution in default_listed:
            default_x = check_on_this_resolution[0]
            default_y = check_on_this_resolution[1]
            if (default_x < self.full_screen_available_x) and (default_y < self.full_screen_available_y):
                this_permited_resolution = f'{default_x}x{default_y}'
                calculated_resolution_list.append(this_permited_resolution)
        calculated_resolution_list.insert(1, full_screen_available_string)
        self.resolution_combobox.addItems(calculated_resolution_list)

    def change_sc_folder(self):
        """
        Change Severed Chains Folder
        Used during Configuration Window, change the current SC Folder to a new one
        """
        new_severed_chains_files_path = config_handler.ConfigurationHandler.select_sc_folder()
        self.change_sc_folder_view.setText(new_severed_chains_files_path)

    def change_deploy_folder(self):
        new_deploy_folder = config_handler.ConfigurationHandler.select_deploy_folder()
        self.change_deploy_folder_view.setText(new_deploy_folder)
    
    def save_current_config(self):
        save_ask = QMessageBox.question(self.save_config_button, 'Please Confirm', 
                                          'Are you sure to Save last changes?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                          QMessageBox.StandardButton.No)
        if save_ask == QMessageBox.StandardButton.Yes:
            get_new_resolution = self.resolution_combobox.currentText().split('x')
            new_resolution_x = int(get_new_resolution[0])
            new_resolution_y = int(get_new_resolution[1])
            get_new_sc_folder = self.change_sc_folder_view.text()
            get_new_deploy_folder = self.change_deploy_folder_view.text()
            self.init_config.update({'SizeX': f'{new_resolution_x}', 'SizeY': f'{new_resolution_y}', 'SC_Folder': get_new_sc_folder, 'Deploy_Folder': get_new_deploy_folder})
            config_handler.ConfigurationHandler.write_config_file(config_file_path=self.init_config_path, configuration_dict=self.init_config)
            self.setGeometry(250, 200, new_resolution_x, new_resolution_y)
            self.startup_x = new_resolution_x
            self.startup_y = new_resolution_y
            self.center_window()
            self.configuration_window.destroy(True, True)

    def cancel_current_config(self):
        cancel_ask = QMessageBox.question(self.cancel_config_button, 'Please Confirm', 
                                          'Are you sure to discard last changes?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                          QMessageBox.StandardButton.No)
        if cancel_ask == QMessageBox.StandardButton.Yes:
            self.configuration_window.destroy(True, True)

    def about_asset_manager(self):
        # CREATING ABOUT WINDOW
        self.about_window = QDialog(self)
        # Label with Text
        about_label_1 = QLabel(self.about_window)
        about_label_2 = QLabel(self.about_window)
        about_label_3 = QLabel(self.about_window)
        about_label_4_url = QLabel(self.about_window)
        # Text in Labels
        about_label_1.setText(f'TLoD Assets Manager:\nBorn merging of two previous Tools:\nTLoD-TMD-Converter and TLoD-Texture-Converter. Bringing the BEST of the two Worlds\nalso adding more functionality for the user')
        about_label_2.setText(f'As in my previous tools, said:\nThis Tool was made from fans to fans!, keep it as it is!\nCoded By DooMMetal (AKA DragoonSouls) 2024 ©')
        about_label_3.setText(f'Visit my Github for updates and issues tracking at:')
        about_label_4_url.setText(f'<a href=\"https://github.com/Legend-of-Dragoon-Modding/TLoD-Assets-Manager\">TLoD Assets Manager GitHub</a>')
        about_label_4_url.setOpenExternalLinks(True)
        # Generate Layout
        about_window_layout = QGridLayout()
        # Add widgets to the Layout
        about_window_layout.addWidget(about_label_1,0,0)
        about_window_layout.addWidget(about_label_2,1,0)
        about_window_layout.addWidget(about_label_3,2,0)
        about_window_layout.addWidget(about_label_4_url,3,0)
        # Size and place Configuration for About Window
        self.about_window.setMinimumSize(640, 360)
        # Settings for the About Window and Layout
        self.about_window.setModal(True)
        self.about_window.setWindowTitle('About TLoD Assets Manager Beta v0.1')
        self.about_window.setLayout(about_window_layout)
        # Settings for the Labels
        about_label_1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        about_label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        about_label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        about_label_4_url.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        about_label_4_url.setFont(QFont('Arial', 14))

        # SHOW THE ABOUT WINDOW AND IT'S WIDGETS
        self.about_window.show()

    def battle_conversion_window(self):
        sc_folder_get = self.init_config.get(f'SC_Folder')
        deploy_folder = self.init_config.get(f'Deploy_Folder')
        battle_conversion_window = BattleConversionMainWindow(self, icon=self.icon, assets_database=self.assets_database, sc_folder=sc_folder_get, deploy_folder=deploy_folder)
    
    def submap_conversion_window(self):
        sc_folder_get = self.init_config.get(f'SC_Folder')
        deploy_folder = self.init_config.get(f'Deploy_Folder')
        submap_conversion_window = SubMapConversionMainWindow(self, icon=self.icon, assets_database=self.assets_database, sc_folder=sc_folder_get, deploy_folder=deploy_folder )
    
    def textonly_conversion_window(self):
        sc_folder_get = self.init_config.get(f'SC_Folder')
        deploy_folder = self.init_config.get(f'Deploy_Folder')
        textonly_conversion_window = TextOnlyConversionMainWindow(self, icon=self.icon, assets_database=self.assets_database, sc_folder=sc_folder_get, deploy_folder=deploy_folder)
    
    def deff_conversion_window(self):
        pass
        #sc_folder_get = self.init_config.get(f'SC_Folder')
        #deff_conversion_window = DeffConversionMainWindow(self, icon=self.icon, assets_database=self.assets_database, sc_folder=sc_folder_get)

if __name__ == '__main__':
    absolute_path_current = os.path.abspath(os.getcwd())
    absolute_path_config = f'{absolute_path_current}\\Resources\\Manager.config'
    absolute_path_databases = f'{absolute_path_current}\\Databases'
    background_image = f'{absolute_path_current}\\Resources\\Ruff_GUI.png'.replace('\\', '/')
    icon_app = f'{absolute_path_current}\\Resources\\DD_Eye.ico'
    app = QApplication(sys.argv)
    init_data = config_handler.ConfigurationHandler(option_file=absolute_path_config)
    build_database = database_handler.DatabaseHandler(database_path=absolute_path_databases)
    window = MainWindow(title='TLoD Assets Manager Beta v0.1', init_config=init_data.option_dict, init_config_path=absolute_path_config, assets_database=build_database.full_database, icon=icon_app, bg_img=background_image)
    sys.exit(app.exec())