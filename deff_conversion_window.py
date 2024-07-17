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
from deff_handlers import DeffScript, DeffFile

class DeffConversionMainWindow(QMainWindow):
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
        self.setWindowTitle('TLoD Assets Manager - DEFF')
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
        self.add_all_action = QAction('Close', self)
        self.add_all_action.setShortcut(QKeySequence('Ctrl+Q'))
        self.add_all_action.setStatusTip('Close DEFF Conversion Window')
        self.add_all_action.triggered.connect(self.close_window)
    
    def close_window(self):
        self.close()
    
    def create_menu(self):
        queue_tools_menu = self.menuBar().addMenu('Window')
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
        self.convert_deff_button = QPushButton('Convert Battle Models')
        self.convert_deff_button.setMaximumSize(150, 100)
        self.convert_deff_button.setToolTip('Convert selected DEFF')
        self.control_panel_layout.addWidget(self.convert_deff_button,0,1)
        self.convert_deff_button.clicked.connect(self.convert_deff)
        self.treeview.clicked.connect(self.check_if_selected)
        self.convert_deff_button.setEnabled(False)

    # Specific Methods for each Widget
    def create_treeview_data(self):
        self.treeview_model = QStandardItemModel()
        self.root_node = self.treeview_model.invisibleRootItem()
        this_top_parent = self.assets_database.get('DEFF')
        for parent in this_top_parent:
            parent_change_text = parent.replace("_", " ")
            this_parent = TreeviewItem(treeview_text=parent_change_text, font_size=16, set_bold=True)
            self.root_node.appendRow(this_parent)
            get_subparent = this_top_parent.get(f'{parent}')
            for subparent in get_subparent:
                subparent_change_text = subparent.replace("_", " ")
                this_subparent = TreeviewItem(treeview_text=subparent_change_text, font_size=14, set_bold=False)
                this_parent.appendRow(this_subparent)
        self.treeview.setModel(self.treeview_model)
        self.treeview.setExpandsOnDoubleClick(True)
    
    def check_if_selected(self):
        name_black_list: list = ['Bosses', 'CutScenes', 'Dragoon', 'Enemies', 'General', 'Magic and Special Attacks']
        selected_items = self.treeview.selectionModel().selectedIndexes()
        self.current_deff_selected = f''
        self.parent_deff_selected = f''
        for current_selection in selected_items:
            name_selected = self.treeview_model.data(current_selection, 0)
            parent_selected = self.treeview_model.parent(current_selection)
            parent_name = self.treeview_model.data(parent_selected, 0)
            if name_selected not in name_black_list:
                self.convert_deff_button.setEnabled(True)
                self.current_deff_selected = name_selected
                self.parent_deff_selected = parent_name
            else:
                self.convert_deff_button.setEnabled(False)
                self.current_deff_selected = f''
                self.parent_deff_selected = f''
    
    def convert_deff(self):
        get_deff_dict = self.assets_database.get(f'DEFF')
        get_parent_dict = get_deff_dict.get(f'{self.parent_deff_selected}')
        get_current_deff = get_parent_dict.get(f'{self.current_deff_selected}')
        sort_deff_sequence = DeffScript(deff_sequence=get_current_deff, deff_name=self.current_deff_selected, deff_parent=self.parent_deff_selected)
        convert_deff_data = DeffFile(deff_sequence=sort_deff_sequence.sequenced_deff, sc_folder=self.sc_folder)


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
    testwindow = DeffConversionMainWindow(icon=icon_app, assets_database=build_database.full_database)
    sys.exit(testapp.exec())