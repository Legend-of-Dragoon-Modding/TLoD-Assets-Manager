"""

Conversion Window: Conversion module for TLoD Assets Manager GUI, 
here only exist the GUI code

Version: Beta 0.1

GUI Module: PyQt

Copyright (C) 2024 DooMMetaL


"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QGridLayout, QWidget, QScrollBar, QTreeView, QListWidget, QGroupBox, QLabel, QPushButton
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtCore import QAbstractItemModel, Qt
import database_handler
from file_handlers import asunder_binary_data, binary_to_dict, folder_handler, debug_files_writer
from gltf_handlers import gltf_compiler

class BattleConversionMainWindow(QMainWindow):
    def __init__(self, parent, icon=str, assets_database=dict, sc_folder=str):
        super().__init__(parent=parent)
        self.icon = icon
        self.assets_database = assets_database
        self.sc_folder = sc_folder
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.full_screen_available_x = self.screen().availableGeometry().width() # Maybe i should use this to generate the calcs for the OpenGL Window Widget
        self.full_screen_available_y = self.screen().availableGeometry().height()
        self.initializate_window()
    
    def initializate_window(self):
        self.setWindowTitle('TLoD Assets Manager - Battle Models')
        self.setWindowIcon(QIcon(self.icon))
        self.generate_window()
        minimum_size__x = self.full_screen_available_x - 150
        minimum_size__y = self.full_screen_available_y - 150
        self.setMinimumSize(minimum_size__x,minimum_size__y)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.showMaximized()

    def generate_window(self):
        self.build_actions()
        self.create_menu() # -> Creation of menu always after Building Actions
        self.create_window_layout()
        self.create_treeview()
        self.create_opengl_window()
        self.create_conversion_queue()
        self.create_conversion_controls_panel()
    
    # Actions for the Menu Bar

    def build_actions(self):
        self.add_all_action = QAction('Add All to Convert', self)
        self.add_all_action.setShortcut(QKeySequence('Ctrl+A'))
        self.add_all_action.setStatusTip('Add all elements from the Main Parent to be converted')
        self.add_all_action.triggered.connect(self.add_all_models_to_conversion_queue)
    
    def add_all_models_to_conversion_queue(self):
        print(f'Adding all models to be Converted')
    
    def create_menu(self):
        queue_tools_menu = self.menuBar().addMenu('Queue Tools')
        queue_tools_menu.addAction(self.add_all_action)

    # Creation of Widgets
    
    def create_window_layout(self):
        # Create Main Widget to hold other widgets
        self.main_widget = QWidget(self)
        # First will create the Layout for them
        self.main_window_layout = QGridLayout(self.main_widget)
        # Setting the Central Widget
        self.setCentralWidget(self.main_widget)

    def create_treeview(self):
        # Create Treeview and filling it with data
        self.treeview = QTreeView()
        self.treeview.setHeaderHidden(True)
        self.create_treeview_data()
        # Adding the TreeView to the Layout
        adjust_treeview_x = self.full_screen_available_x // 4
        adjust_treeview_y = self.full_screen_available_y
        self.treeview.setMaximumSize(adjust_treeview_x,adjust_treeview_y)
        self.main_window_layout.addWidget(self.treeview,0,0,0,1)
        self.tree_view_scrollbar = QScrollBar()
        self.treeview.setVerticalScrollBar(self.tree_view_scrollbar)
    
    def create_opengl_window(self):
        # Create the ListWidget for data
        self.opengl_window = QGroupBox('OpenGL Window')
        self.main_window_layout.addWidget(self.opengl_window,0,1)
    
    def create_conversion_queue(self):
        # Create the ListWidget for data
        self.conversion_queue_listwidget = QListWidget()
        adjust_conv_queue_x = self.full_screen_available_x // 2
        adjust_conv_queue_y = self.full_screen_available_y // 3
        self.conversion_queue_listwidget.setMaximumSize(adjust_conv_queue_x, adjust_conv_queue_y)
        self.main_window_layout.addWidget(self.conversion_queue_listwidget,1,1)
        self.conversion_queue_scrollbar = QScrollBar()
        self.conversion_queue_listwidget.setVerticalScrollBar(self.conversion_queue_scrollbar)
    
    def create_conversion_controls_panel(self):
        self.control_panel_box = QGroupBox('Conversion Controls')
        self.main_window_layout.addWidget(self.control_panel_box,0,2,0,1)
        self.control_panel_layout = QGridLayout(self.control_panel_box)
        self.text_label_controls = QLabel('Here you can control everything related to Conversion')
        self.control_panel_layout.addWidget(self.text_label_controls)
        self.convert_model_button = QPushButton('Convert Models')
        self.convert_model_button.setMaximumSize(150, 100)
        self.convert_model_button.setToolTip('Process the selected models')
        self.control_panel_layout.addWidget(self.convert_model_button,0,1)
        self.convert_model_button.clicked.connect(self.convert_model_selected)
        self.treeview.clicked.connect(self.check_if_selected)
        self.convert_model_button.setEnabled(False)


    # Specific Methods for each Widget
    def create_treeview_data(self):
        self.treeview_model = QStandardItemModel()
        self.root_node = self.treeview_model.invisibleRootItem()
        this_top_parent = self.assets_database.get('Battle')
        for parent in this_top_parent:
            parent_change_text = parent.replace("_", " ")
            this_parent = TreeviewItem(treeview_text=parent_change_text, font_size=16, set_bold=True)
            self.root_node.appendRow(this_parent)
            get_subparent = this_top_parent.get(f'{parent}')
            for subparent in get_subparent:
                subparent_change_text = subparent.replace("_", " ")
                this_subparent = TreeviewItem(treeview_text=subparent_change_text, font_size=14, set_bold=False)
                this_parent.appendRow(this_subparent)
                #get_child = get_subparent.get(f'{subparent}') # --> This is the data of this Child
        self.treeview.setModel(self.treeview_model)
        self.treeview.setExpandsOnDoubleClick(True)

    def check_if_selected(self):
        name_black_list: list = ['Characters', 'CutScenes', 'Battle Stages', 'Bosses', 'Enemies', 'Tutorial']
        selected_items = self.treeview.selectionModel().selectedIndexes()
        self.current_battle_model_selected = f''
        self.parent_battle_model_selected = f''
        for current_selection in selected_items:
            name_selected = self.treeview_model.data(current_selection, 0)
            parent_selected = self.treeview_model.parent(current_selection)
            parent_name = self.treeview_model.data(parent_selected, 0)
            if name_selected not in name_black_list:
                self.convert_model_button.setEnabled(True)
                self.current_battle_model_selected = name_selected
                self.parent_battle_model_selected = parent_name
            else:
                self.convert_model_button.setEnabled(False)
                self.current_battle_model_selected = f''
                self.parent_battle_model_selected = f''

    def convert_model_selected(self):
        get_battle_model_dict = self.assets_database.get(f'Battle')
        get_parent_dict = get_battle_model_dict.get(f'{self.parent_battle_model_selected}')
        get_current_battle_model = get_parent_dict.get(f'{self.current_battle_model_selected}')
        file_fantasy_name = self.current_battle_model_selected.replace(' ', '_')
        for current_object_to_convert in get_current_battle_model:
            this_conversion_obj = get_current_battle_model.get(f'{current_object_to_convert}')
            if current_object_to_convert == 'Texture':
                print('Texture path...', f'{self.sc_folder}{this_conversion_obj}')
            else:
                final_file_name = f'{file_fantasy_name}_{current_object_to_convert}'
                get_model_path = this_conversion_obj.get(f'ModelFolder')
                get_model_file = this_conversion_obj.get(f'ModelFile')
                model_file_path = f'{self.sc_folder}{get_model_path}/{get_model_file}'
                file_model_specs = {'Format': 'TMD_CContainer', 'Path': model_file_path, 'Name': f'{final_file_name}', 'isAnimated': False, 'isTextured': False}
                file_model_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=file_model_specs)
                processed_data_model = asunder_binary_data.Asset(bin_to_split=file_model_bin.bin_data_dict)
                process_to_gltf = gltf_compiler.NewModel(model_data=processed_data_model.model_converted_data, animation_data=None)
                #debug_files_dict = {'TMDReport': True, 'PrimPerObj': True, 'PrimData': True} # This is only pass one, even in batch
                #new_folder = folder_handler.Folders(deploy_folder_path=f'C:\\Users\\Axel\\Desktop\\TMD_DUMP\\', file_nesting='Dart_Test, Animation', file_name=final_file_name)
                #debug_data = debug_files_writer.DebugData(converted_file_path=new_folder.new_file_name, debug_files_flag=debug_files_dict, file_data=processed_data_model.model_converted_data)

class TreeviewItem(QStandardItem):
    def __init__(self, treeview_text=str, font_size=int, set_bold=bool, color=QColor(0, 0, 0)):
        """
        This Standard Item is used to create the Text shown in the Treeviews
        """
        super().__init__()
        text_font = QFont('Arial', font_size) # Creating the Text Object
        text_font.setBold(set_bold) # Setting if Bold
        self.setEditable(False) # Avoid overwritting the Text Object
        self.setForeground(color) # Text font Color
        self.setFont(text_font)
        self.setText(treeview_text)

if __name__ == '__main__':
    absolute_path_current = os.path.abspath(os.getcwd())
    absolute_path_databases = f'{absolute_path_current}\\Databases'
    icon_app = f'{absolute_path_current}\\Resources\\DD_Eye.ico'
    testapp = QApplication(sys.argv)
    build_database = database_handler.DatabaseHandler(database_path=absolute_path_databases)
    testwindow = BattleConversionMainWindow(icon=icon_app, assets_database=build_database.full_database)
    sys.exit(testapp.exec())
