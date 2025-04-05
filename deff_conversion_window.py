"""

Conversion Window: Conversion module for TLoD Assets Manager GUI, 
here only exist the GUI code

Version: Beta 0.1

GUI Module: PyQt

Copyright (C) 2024 DooMMetaL


"""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStatusBar, QGridLayout, QWidget, QScrollBar, QTreeView, 
                             QListWidget, QGroupBox, QLabel, QPushButton, QProgressBar, QMessageBox, QCheckBox)
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSlot, pyqtSignal
import database_handler
from conversion_interfaces import DeffConversionInterface

class DeffConversionMainWindow(QMainWindow):
    def __init__(self, parent, icon=str, assets_database=dict, sc_folder=str, deploy_folder=str):
        super().__init__(parent=parent)
        self.icon = icon
        self.assets_database = assets_database
        self.sc_folder = sc_folder
        self.deploy_folder = deploy_folder
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
        # Bool Properties
        self.deff_scene_bool: bool = False
        self.particle_convert_bool: bool = False
        self.texture_convert_bool: bool = False
        # Group Box and Layout set-up
        self.control_panel_box = QGroupBox('Conversion Controls')
        self.main_window_layout.addWidget(self.control_panel_box,0,2,0,1)
        self.control_panel_layout = QGridLayout(self.control_panel_box)
        # Sub-Widgets
        self.text_label_controls = QLabel('Here you can control everything related to Conversion')
        self.deff_scene_checkbox = QCheckBox('Convert Full Scene')
        self.texture_checkbox = QCheckBox('Convert Model Textures')
        self.particles_checkbox = QCheckBox('Convert Particles')
        self.convert_deff_button = QPushButton('Convert DEFF Models')
        # Size for Widgets
        self.text_label_controls.setMaximumSize(900, 50)
        self.deff_scene_checkbox.setMaximumSize(150, 100)
        self.particles_checkbox.setMaximumSize(150, 100)
        self.particles_checkbox.setMaximumSize(150, 100)
        self.convert_deff_button.setMaximumSize(150, 100)
        # Tooltips
        self.deff_scene_checkbox.setToolTip('If check, convert everything as a single glTF File.\nWIP: Sorry for inconvenience.')
        self.deff_scene_checkbox.setDisabled(True)
        self.texture_checkbox.setToolTip('If check, convert DEFF Scene objects Textures\nKEEP IN MIND, Texture Conversion will slow down the process dramatically')
        self.particles_checkbox.setToolTip('If check, convert Particle Files and Generated Particles.\nWIP: Sorry for inconvenience.')
        self.particles_checkbox.setDisabled(True)
        self.convert_deff_button.setToolTip('Convert selected DEFF')
        # Create Progress bar for conversion
        self.progressbar_conversion = QProgressBar()
        self.progressbar_conversion.setMinimumSize(200, 50)
        # Place Widgets in Layout
        self.control_panel_layout.addWidget(self.text_label_controls,1,0)
        self.control_panel_layout.addWidget(self.deff_scene_checkbox,2,0)
        self.control_panel_layout.addWidget(self.texture_checkbox,3,0)
        self.control_panel_layout.addWidget(self.particles_checkbox,4,0)
        self.control_panel_layout.addWidget(self.convert_deff_button,5,0)
        self.control_panel_layout.addWidget(self.progressbar_conversion,6,0)
        # Connection Functions when something toggled/activated
        self.convert_deff_button.clicked.connect(self.convert_deff)
        self.treeview.clicked.connect(self.check_if_selected)
        self.deff_scene_checkbox.toggled.connect(self.check_if_full_scene)
        self.texture_checkbox.toggled.connect(self.check_if_textures)
        self.particles_checkbox.toggled.connect(self.check_if_particles)
        self.convert_deff_button.setEnabled(False)
        self.progressbar_conversion.setValue(0)
        self.progressbar_conversion.setDisabled(True)

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
            for this_subparent_name in get_subparent:
                this_suparent = TreeviewItem(treeview_text=this_subparent_name, font_size=14, set_bold=False)
                this_parent.appendRow(this_suparent)
        self.treeview.setModel(self.treeview_model)
        self.treeview.setExpandsOnDoubleClick(True)
    
    def check_if_selected(self):
        name_black_list: list = ['Bosses', 'CutScenes', 'Dragoon', 'Enemies', 'General', 'Magic and Special Attacks']
        selected_items = self.treeview.selectionModel().selectedIndexes()
        self.parent_deff_selected = f''
        self.current_deff_selected = f''
        for current_selection in selected_items:
            name_selected = self.treeview_model.data(current_selection, 0)
            parent_selected = self.treeview_model.parent(current_selection)
            parent_name = self.treeview_model.data(parent_selected, 0)
            if name_selected not in name_black_list:
                self.convert_deff_button.setEnabled(True)
                self.parent_deff_selected = parent_name
                self.current_deff_selected = name_selected
            else:
                self.convert_deff_button.setEnabled(False)
                self.parent_deff_selected = f''
                self.current_deff_selected = f''
        
    def check_if_full_scene(self):
        this_bool = self.sender().isChecked()
        self.deff_scene_bool = this_bool
    
    def check_if_textures(self):
        this_bool = self.sender().isChecked()
        self.texture_convert_bool = this_bool
    
    def check_if_particles(self):
        this_bool = self.sender().isChecked()
        self.particle_convert_bool = this_bool

    def convert_deff(self):
        self.deff_scene_checkbox.setDisabled(True)
        self.texture_checkbox.setDisabled(True)
        self.particles_checkbox.setDisabled(True)
        get_deff_dict = self.assets_database.get(f'DEFF')
        get_parent_dict = get_deff_dict.get(f'{self.parent_deff_selected}')
        get_selected_deff = get_parent_dict.get(f'{self.current_deff_selected}')
        self.finished_conversion_item = self.current_deff_selected
        self.convert_deff_button.setDisabled(True)
        self.progressbar_conversion.setEnabled(True)
        self.progressbar_conversion.setMinimum(0)
        self.progressbar_conversion.setMaximum(1)
        selected_parent = f'{self.parent_deff_selected}'
        self.thread_conversion_queue = QThreadConverting(parent=self, deff_convert=get_selected_deff, 
                                                         conv_textures=self.texture_convert_bool, conv_particles=self.particle_convert_bool, sc_folder=self.sc_folder, 
                                                         deploy_folder=self.deploy_folder, selected_parent=selected_parent, scene_flag=self.deff_scene_bool)
        self.thread_conversion_queue.start()
        self.thread_conversion_queue.progress_signal.connect(self.update_progress)

    @pyqtSlot(int)
    def update_progress(self, progress=int) -> None:
        self.progressbar_conversion.setValue(progress)
        self.finished_conversion()
    
    def finished_conversion(self):
        if self.progressbar_conversion.value() == self.progressbar_conversion.maximum():
            this_conversion_done = f'Conversion: {self.finished_conversion_item} Complete...'
            conversion_done_qmessagebox = QMessageBox.information(self, 'SUCCESS!', this_conversion_done, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            if (conversion_done_qmessagebox == QMessageBox.StandardButton.Ok) or (conversion_done_qmessagebox == QMessageBox.StandardButton.Close):
                self.progressbar_conversion.setValue(0)
                self.progressbar_conversion.setDisabled(True)
                self.convert_deff_button.setEnabled(True)
                #self.deff_scene_checkbox.setEnabled(True)
                self.texture_checkbox.setEnabled(True)
                #self.particles_checkbox.setEnabled(True)

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

class QThreadConverting(QThread):
    progress_signal = pyqtSignal(int)
    def __init__(self, parent: QObject | None = ..., deff_convert=dict, conv_textures=bool, conv_particles=bool, sc_folder=str, deploy_folder=str, selected_parent=str, scene_flag=bool) -> None:
        super().__init__(parent)
        self.deff_convert = deff_convert
        self.conv_textures = conv_textures
        self.conv_particles = conv_particles
        self.sc_folder = sc_folder
        self.deploy_folder = deploy_folder
        self.selected_parent = selected_parent
        self.scene_flag = scene_flag
    
    def run(self):
        progress_conversion = 0
        self.single_convert = DeffConversionInterface(deff_convert=self.deff_convert, conv_textures=self.conv_textures, conv_particles=self.conv_particles, scene_flag=self.scene_flag, sc_folder=self.sc_folder, deploy_folder=self.deploy_folder, selected_parent=self.selected_parent)
        progress_conversion += 1
        self.progress_signal.emit(progress_conversion)

if __name__ == '__main__':
    absolute_path_current = os.path.abspath(os.getcwd())
    absolute_path_databases = f'{absolute_path_current}\\Databases'
    icon_app = f'{absolute_path_current}\\Resources\\Dragoon_Eyes.ico'
    sc_folder_static = f'D:\\TLoD_Modding\\Severed_Chains\\files\\SECT\\DRGN0.BIN\\'
    deploy_folder_static = f'C:\\Users\\Axel\\Desktop\\TMD_DUMP'
    testapp = QApplication(sys.argv)
    build_database = database_handler.DatabaseHandler(database_path=absolute_path_databases)
    testwindow = DeffConversionMainWindow(parent=None, icon=icon_app, assets_database=build_database.full_database, sc_folder=sc_folder_static, deploy_folder=deploy_folder_static)
    sys.exit(testapp.exec())