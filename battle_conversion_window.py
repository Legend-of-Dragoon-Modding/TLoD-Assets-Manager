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
    def __init__(self, parent, icon=str, assets_database=dict, sc_folder=str, deploy_folder=str):
        super().__init__(parent=parent)
        self.icon = icon
        self.assets_database = assets_database
        self.sc_folder = sc_folder
        self.deploy_folder = deploy_folder
        self.check_sc_folder()
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
        # Create the Main Widget
        self.opengl_window = QGroupBox('OpenGL Window')
        self.main_window_layout.addWidget(self.opengl_window,0,1)
    
    def create_conversion_queue(self):
        # Create the Main Widget and Setup it
        self.conversion_queue_listwidget = QListWidget()
        adjust_conv_queue_x = self.full_screen_available_x // 2
        adjust_conv_queue_y = self.full_screen_available_y // 3
        self.conversion_queue_listwidget.setMaximumSize(adjust_conv_queue_x, adjust_conv_queue_y)
        self.main_window_layout.addWidget(self.conversion_queue_listwidget,1,1)
        self.conversion_queue_scrollbar = QScrollBar()
        self.conversion_queue_listwidget.setVerticalScrollBar(self.conversion_queue_scrollbar)
    
    def create_conversion_controls_panel(self):
        # Create Main Widget
        self.control_panel_box = QGroupBox('Conversion Controls')
        self.main_window_layout.addWidget(self.control_panel_box,0,2,0,1)
        # Create Layout
        self.control_panel_layout = QGridLayout(self.control_panel_box)
        # Create Label to show Text
        self.text_label_controls = QLabel('Here you can control everything related to Conversion')
        # Create Buttons
        self.convert_model_button = QPushButton('Convert Models')

        # Setup all the Widgets
        self.convert_model_button.setMaximumSize(150, 100)
        self.convert_model_button.setToolTip('Process the selected models')
        self.control_panel_layout.addWidget(self.text_label_controls)
        self.control_panel_layout.addWidget(self.convert_model_button,0,1)
        
        # Setup Actions for Pushable/Selectable Widgets
        self.convert_model_button.clicked.connect(self.convert_model_selected)
        self.treeview.clicked.connect(self.check_if_selected)
        self.convert_model_button.setEnabled(False)

    # Specific Methods for each Widget
    def create_treeview_data(self):
        self.name_black_list: list = []
        self.super_parent_selected_nodes: str = f''
        self.parent_selected_nodes: str = f''
        self.children_selected_nodes: str = f''
        self.treeview_model = QStandardItemModel()
        self.root_node = self.treeview_model.invisibleRootItem()
        this_top_parent = self.assets_database.get('Battle')
        parent_contain_sub_list: list = ['Characters', 'CutScenes']
        for parent in this_top_parent:
            self.name_black_list.append(parent)
            parent_change_text = parent.replace("_", " ")
            this_parent = TreeviewItem(treeview_text=parent_change_text, font_size=16, set_bold=True)
            self.root_node.appendRow(this_parent)
            get_subparent = this_top_parent.get(f'{parent}')
            for subparent in get_subparent:
                subparent_change_text = subparent.replace("_", " ")
                this_subparent = TreeviewItem(treeview_text=subparent_change_text, font_size=14, set_bold=False)
                this_parent.appendRow(this_subparent)
                if parent in parent_contain_sub_list:
                    self.name_black_list.append(subparent)
                    get_child = get_subparent.get(f'{subparent}')
                    for child in get_child:
                        if 'Texture' not in child:
                            child_change_text = child.replace("_", " ")
                            this_child = TreeviewItem(treeview_text=child_change_text, font_size=12, set_bold=True)
                            this_subparent.appendRow(this_child)

        self.treeview.setModel(self.treeview_model)
        self.treeview.setExpandsOnDoubleClick(True)

    def check_if_selected(self):
        selected_items = self.treeview.selectionModel().selectedIndexes()
        for current_selection in selected_items:
            name_selected = self.treeview_model.data(current_selection, 0)
            parent_selected = self.treeview_model.parent(current_selection)
            parent_name = self.treeview_model.data(parent_selected, 0)
            have_children = self.treeview_model.hasChildren(current_selection)
            if parent_name == None:
                self.convert_model_button.setEnabled(False)
                self.super_parent_selected_nodes = name_selected
            elif have_children == False:
                self.children_selected_nodes = name_selected
                self.parent_selected_nodes = parent_name
                self.convert_model_button.setEnabled(True)
            
            if (parent_name != None) and (have_children == True):
                self.convert_model_button.setEnabled(False)

    def convert_model_selected(self):
        get_battle_model_dict = self.assets_database.get(f'Battle')
        selected_items_list: list = [self.super_parent_selected_nodes, self.parent_selected_nodes, self.children_selected_nodes]
        """Clean the Selected Items List to fit the following logic:
        Parent->Child (Model Object to Convert)
        SuperParent->Parent->Child (Model Object to Convert) ==> This is used in CutScenes and Characters list due to the nesting"""
        clean_selected_items: list = []
        for this_selection in selected_items_list:
            if this_selection not in clean_selected_items:
                clean_selected_items.append(this_selection)
        
        if len(clean_selected_items) == 2:
            # Get Data to be Converted
            parent_name_denest = clean_selected_items[0].replace(" ", "_")
            model_name_denest = clean_selected_items[1]
            final_folder_model = model_name_denest.replace(" ", "_")
            get_complete_objects_dict = get_battle_model_dict.get(f'{parent_name_denest}')
            get_current_object_dict = get_complete_objects_dict.get(f'{model_name_denest}')
            get_model_folder_path = get_current_object_dict.get(f'ModelFolder')
            get_model_file = get_current_object_dict.get(f'ModelFile')
            get_model_passive_anim_path = get_current_object_dict.get(f'PassiveFolder')
            get_model_passive_anim_files = get_current_object_dict.get(f'PassiveFiles')
            get_model_attack_anim_path = get_current_object_dict.get(f'AttackFolder')
            get_model_attack_anim_files = get_current_object_dict.get(f'AttackFiles')
            get_model_textures = get_current_object_dict.get(f'Textures')
            # Setting up some Properties to Finish the Conversion
            model_complete_file_path = f'{self.sc_folder}/{get_model_folder_path}/{get_model_file}'
            folder_nesting = f'{parent_name_denest}, {final_folder_model}'
            file_model_specs = {'Format': 'TMD_CContainer', 'Path': model_complete_file_path, 'Name': f'{model_name_denest}', 'isAnimated': False, 'isTextured': False}
            debug_files_dict = {'TMDReport': True, 'PrimPerObj': True, 'PrimData': True} # This is only pass one, even in batch
            # Start Conversion
            new_folder = folder_handler.Folders(deploy_folder_path=self.deploy_folder, file_nesting=folder_nesting, file_name=model_name_denest)
            file_model_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=file_model_specs)
            processed_data_model = asunder_binary_data.Asset(bin_to_split=file_model_bin.bin_data_dict)
            debug_data = debug_files_writer.DebugData(converted_file_path=new_folder.new_file_name, debug_files_flag=debug_files_dict, file_data=processed_data_model.model_converted_data)
            process_to_gltf = gltf_compiler.NewModel(model_data=processed_data_model.model_converted_data, animation_data=None)

    def check_sc_folder(self) -> None:
        init_sc_folder = self.sc_folder
        new_sc_folder = f'{init_sc_folder}/SECT/DRGN0.BIN'
        self.sc_folder = new_sc_folder

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
