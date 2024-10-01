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
                             QListWidget, QGroupBox, QLabel, QPushButton, QCheckBox, QComboBox, QMessageBox, QProgressBar)
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSlot, pyqtSignal
import database_handler
from conversion_interfaces import WorldMapConversionInterface


class WorldMapConversionMainWindow(QMainWindow):
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
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.initializate_window()
    
    def initializate_window(self):
        self.setWindowTitle('TLoD Assets Manager - World Map Models')
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
        self.create_preview_window()
        self.create_conversion_queue()
        self.create_conversion_controls_panel()
    
    # Actions for the Menu Bar
    def build_actions(self):
        self.add_all_action = QAction('Quit World Map Conversion', self)
        self.add_all_action.setShortcut(QKeySequence('Ctrl+X'))
        self.add_all_action.setStatusTip('Quit this Conversion Window')
        self.add_all_action.triggered.connect(self.quit_worldmap_window)
    
    def create_menu(self):
        queue_tools_menu = self.menuBar().addMenu('Window')
        queue_tools_menu.addAction(self.add_all_action)

    def quit_worldmap_window(self):
        # close() closes the window and deleteLater() will destroy the PyQt object avoiding keep everything in Memory
        self.close()
        self.deleteLater()

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
    
    def create_treeview_data(self):
        self.name_black_list: list = []
        self.parent_selected_nodes: str = f''
        self.children_selected_nodes: str = f''
        self.treeview_model = QStandardItemModel()
        self.root_node = self.treeview_model.invisibleRootItem()
        this_top_parent = self.assets_database.get('World Map')
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

        self.treeview.setModel(self.treeview_model)
        self.treeview.setExpandsOnDoubleClick(True)
        self.treeview.setExpanded(this_parent.index(), True)
    
    def create_preview_window(self):
        # Create the Main Widget
        self.preview_window_layout = QGroupBox('Preview Window') # OpenGL Window and other if needed
        self.main_window_layout.addWidget(self.preview_window_layout,0,1)
    
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
        # Bool Values needed for Conversion by Default this are the values at startup of the Battle Conversion Window
        # This will help people that want just a very fast thing to do
        self.anim_convert: bool = True
        self.texture_convert: bool = False
        self.tmd_report: bool = False
        self.prim_report: bool = False
        self.generate_primdata: bool = False
        self.mode_selected: str = 'Single'
        self.combobox_selection: str = 'None'
        # Create Main Widget
        self.control_panel_box = QGroupBox('Conversion Controls')
        self.main_window_layout.addWidget(self.control_panel_box,0,2,0,1)
        # Create Layouts, Adding them to the Main Panel Layout and sorting them
        self.main_panel_layout = QGridLayout(self.control_panel_box)
        self.mode_selection_layout = QGridLayout()
        self.mode_options_layout = QGridLayout()
        self.convert_layout = QGridLayout()
        self.main_panel_layout.addLayout(self.mode_selection_layout, 0, 0)
        self.main_panel_layout.addLayout(self.mode_options_layout, 1, 0)
        self.main_panel_layout.addLayout(self.convert_layout, 2, 0)
        # Create Mode Buttons
        self.change_conversion_mode_single = QPushButton('Single Model Mode')
        self.change_conversion_mode_batch = QPushButton('Batch Models Mode')
        # Create Label to show Text
        self.text_label_controls = QLabel('Select the Mode\nyou want to work on')
        # Create Convert Button
        self.convert_model_button = QPushButton('Convert Models')
        # Create Progress bar for conversion
        self.progressbar_conversion = QProgressBar()
        # Sizes
        self.change_conversion_mode_single.setMaximumSize(300, 100)
        self.change_conversion_mode_single.setMinimumSize(150, 50)
        self.change_conversion_mode_batch.setMaximumSize(300, 100)
        self.change_conversion_mode_batch.setMinimumSize(150, 50)
        self.text_label_controls.setMaximumSize(200, 100)
        self.convert_model_button.setMaximumSize(200, 100)
        self.progressbar_conversion.setMinimumSize(200, 50)
        # Tooltips
        self.change_conversion_mode_single.setToolTip('Change Conversion Mode to: Single.\nYou must select what model you want to convert')
        self.change_conversion_mode_batch.setToolTip('Change Conversion Mode to: Batch.\nWill Convert all the models with all the Animations available.\nWARNING: This Option is the slowest and can take several minutes if not hours to perform!')
        self.convert_model_button.setToolTip('Process the selected model')
        # Positioning
        self.mode_selection_layout.addWidget(self.change_conversion_mode_single,0,0)
        self.mode_selection_layout.addWidget(self.change_conversion_mode_batch,0,2)
        self.convert_layout.addWidget(self.text_label_controls,3,2)
        self.convert_layout.addWidget(self.convert_model_button,4,2)
        self.convert_layout.addWidget(self.progressbar_conversion,5,1,1,3)
        
        # Setup Actions for Pushable/Selectable Widgets
        self.text_label_controls.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.treeview.selectionModel().selectionChanged.connect(self.check_if_selected)
        self.change_conversion_mode_single.setEnabled(True)
        self.change_conversion_mode_batch.setEnabled(True)
        self.convert_model_button.setEnabled(False)
        self.progressbar_conversion.setValue(0)
        self.progressbar_conversion.setDisabled(True)
        self.change_conversion_mode_single.clicked.connect(self.enable_single_conversion)
        self.change_conversion_mode_batch.clicked.connect(self.enable_batch_conversion)
        self.convert_model_button.clicked.connect(self.convert_model_selected)
        
        # Create Checkboxes
        self.check_animations = QCheckBox('Animations')
        self.check_texture = QCheckBox('Textures')
        self.check_tmd_report = QCheckBox('TMD Report')
        self.check_prim_report = QCheckBox('Primitives Report')
        self.check_generate_primdata = QCheckBox('PrimData File')
        # Create ComboBox
        self.parent_combobox = QComboBox()
        # Sizes
        self.check_animations.setMaximumSize(200, 200)
        self.check_texture.setMaximumSize(200, 200)
        self.check_tmd_report.setMaximumSize(200, 200)
        self.check_prim_report.setMaximumSize(200, 200)
        self.check_generate_primdata.setMaximumSize(200, 200)
        # Tooltips
        self.check_animations.setToolTip('Enable/Disable conversion of Base Animations')
        self.check_texture.setToolTip('Enable/Disable conversion of Textures if available,\nWARNING: Enable this Option will slow down the conversion')
        self.check_tmd_report.setToolTip('Create a TMD Report File to check Model integrity')
        self.check_prim_report.setToolTip('Create a Primitive per Object Report file to know which types and number this types are used in the original Model')
        self.check_generate_primdata.setToolTip('Create a PrimData file, which is used along with the Blender to TLoD tool for modding 3D Models')
        self.parent_combobox.setToolTip('Select a Parent to be Converted')
        # Positioning
        self.mode_options_layout.addWidget(self.check_animations,1,0, Qt.AlignmentFlag.AlignCenter)
        self.mode_options_layout.addWidget(self.check_texture,1,2, Qt.AlignmentFlag.AlignCenter)
        self.mode_options_layout.addWidget(self.check_tmd_report,2,0, Qt.AlignmentFlag.AlignCenter)
        self.mode_options_layout.addWidget(self.check_prim_report,2,1, Qt.AlignmentFlag.AlignCenter)
        self.mode_options_layout.addWidget(self.check_generate_primdata,2,2, Qt.AlignmentFlag.AlignCenter)
        self.mode_options_layout.addWidget(self.parent_combobox,3,1, Qt.AlignmentFlag.AlignCenter)
        # Add items to the Combobox
        for parent in self.assets_database.get('World Map'):
            self.parent_combobox.addItem(parent)
        # Setup Basic Actions for Pushable/Selectable Widgets
        self.parent_combobox.setDisabled(True)
        self.check_animations.setChecked(True)
        self.check_texture.setChecked(False)
        self.check_tmd_report.setChecked(False)
        self.check_prim_report.setChecked(False)
        self.check_generate_primdata.setChecked(False)
        self.parent_combobox.setDisabled(True)

    # Specific Methods for each Widget in Single Mode Conversion
    def check_if_selected(self):
        self.parent_selected_nodes: str = ''
        self.children_selected_nodes: str = ''
        selected_items = self.treeview.selectionModel().selectedIndexes()
        for current_selection in selected_items:
            this_selection = self.treeview.model().itemFromIndex(current_selection)
            parent_item = this_selection.parent()
            child_item = this_selection.child(0)
            if child_item == None:
                self.convert_model_button.setEnabled(True)
                self.parent_selected_nodes = parent_item.text()
                self.children_selected_nodes = this_selection.text()
            else:
                self.convert_model_button.setEnabled(False)

    def check_animation_bool(self):
        this_bool = self.sender().isChecked()
        self.anim_passive_convert = this_bool

    def check_texture_bool(self):
        this_bool = self.sender().isChecked()
        self.texture_convert = this_bool
    
    def check_tmd_report_bool(self):
        this_bool = self.sender().isChecked()
        self.tmd_report = this_bool
    
    def check_prim_report_bool(self):
        this_bool = self.sender().isChecked()
        self.prim_report = this_bool
    
    def check_generate_primdata_bool(self):
        this_bool = self.sender().isChecked()
        self.generate_primdata = this_bool

    def convert_model_selected(self):
        self.progressbar_conversion.setEnabled(True)
        self.finished_conversion_item: str = ''
        worldmap_assets_dict = self.assets_database.get(f'World Map')
        selected_items_list: list = []

        if self.mode_selected == 'Single':
            check_list = [self.parent_selected_nodes, self.children_selected_nodes]            
            clean_list = []
            for this_selection in check_list:
                if (this_selection not in clean_list):
                    clean_list.append(this_selection)
            selected_items_list.append(clean_list)
            self.finished_conversion_item = f'{check_list[-2]} - {check_list[-1]}'
        
        elif self.mode_selected == 'All':
            warning_message = f'Are you sure want to Convert All Models?.\nKeep in mind this Option could take much time\ndepending on your hardware speed.\nTexture Conversion also will slow down the conversion a lot in this Mode.'
            warning_messagebox = QMessageBox.warning(self, 'CAUTION!', warning_message, QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
            
            if warning_messagebox == QMessageBox.StandardButton.Ok:
                for parent in worldmap_assets_dict:
                    child_data = worldmap_assets_dict.get(f'{parent}')
                    for child in child_data:
                        this_convert_list = [parent, child]
                        selected_items_list.append(this_convert_list)
                self.finished_conversion_item = f'Batch Conversion'
                
            elif warning_messagebox == QMessageBox.StandardButton.Cancel:
                info_message = f'Batch Conversion Cancelled.'
                selected_items_list = []
                info_cancelled_messagebox = QMessageBox.information(self, 'Information', info_message, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        
        total_files_to_convert = len(selected_items_list)

        if total_files_to_convert > 0:
            self.change_conversion_mode_single.setDisabled(True)
            self.change_conversion_mode_batch.setDisabled(True)
            self.convert_model_button.setDisabled(True)
            self.parent_combobox.setDisabled(True)
            self.check_animations.setDisabled(True)
            self.check_texture.setDisabled(True)
            self.check_tmd_report.setDisabled(True)
            self.check_prim_report.setDisabled(True)
            self.check_generate_primdata.setDisabled(True)
            self.parent_combobox.setDisabled(True)
            self.progressbar_conversion.setMinimum(0)
            self.progressbar_conversion.setMaximum(total_files_to_convert)
            self.thread_conversion_queue = QThreadConverting(parent=self, conversion_list=selected_items_list, worldmap_asset_dict=worldmap_assets_dict, 
                                                             anim_convert=self.anim_convert, texture_convert=self.texture_convert, sc_folder=self.sc_folder, 
                                                             tmd_report=self.tmd_report, prim_report=self.prim_report, generate_primdata=self.generate_primdata, 
                                                             deploy_folder=self.deploy_folder)
            self.thread_conversion_queue.start()
            self.thread_conversion_queue.progress_signal.connect(self.update_progress)

    @pyqtSlot(int)
    def update_progress(self, progress=int) -> None:
        self.progressbar_conversion.setValue(progress)
        self.finished_conversion()

    # Specific Methods for each Widget in Single Mode Conversion
    def enable_single_conversion(self):
        self.anim_convert: bool = True
        self.texture_convert = True
        self.tmd_report = True
        self.prim_report = True
        self.generate_primdata = True
        self.convert_model_button.setDisabled(True)
        self.treeview.setEnabled(True)
        self.parent_combobox.setDisabled(True)
        self.mode_selected = 'Single'
        self.change_conversion_mode_single.setEnabled(False)
        self.change_conversion_mode_batch.setEnabled(True)
        self.text_label_controls.setText('After you made your selection\nPress the Conversion Button')
        # Setup Actions for Pushable/Selectable Widgets
        self.check_animations.setChecked(True)
        self.check_animations.setDisabled(True)
        self.check_texture.setChecked(True)
        self.check_tmd_report.setChecked(True)
        self.check_prim_report.setChecked(True)
        self.check_generate_primdata.setChecked(True)
        self.treeview.expandAll()
        self.check_animations.toggled.connect(self.check_animation_bool)
        self.check_texture.toggled.connect(self.check_texture_bool)
        self.check_tmd_report.toggled.connect(self.check_tmd_report_bool)
        self.check_prim_report.toggled.connect(self.check_prim_report_bool)
        self.check_generate_primdata.toggled.connect(self.check_generate_primdata_bool)
        
    # Specific Methods for each Widget in Batch Mode Conversion
    def enable_batch_conversion(self):
        self.anim_convert: bool = True
        self.texture_convert = False
        self.tmd_report = False
        self.prim_report = False
        self.generate_primdata = False
        self.mode_selected = 'All'
        self.treeview.setDisabled(True)
        self.treeview.collapseAll()
        self.parent_combobox.setDisabled(True)
        self.change_conversion_mode_single.setEnabled(True)
        self.change_conversion_mode_batch.setEnabled(False)
        self.text_label_controls.setText('After you made your selection\nPress the Conversion Button')
        # Setup default behavior of Checkboxes
        self.check_animations.setChecked(True)
        self.check_animations.setDisabled(True)
        self.check_texture.setChecked(False)
        self.check_tmd_report.setChecked(False)
        self.check_prim_report.setChecked(False)
        self.check_generate_primdata.setChecked(False)
        self.convert_model_button.setEnabled(True)
        self.check_animations.toggled.connect(self.check_animation_bool)
        self.check_texture.toggled.connect(self.check_texture_bool)
        self.check_tmd_report.toggled.connect(self.check_tmd_report_bool)
        self.check_prim_report.toggled.connect(self.check_prim_report_bool)
        self.check_generate_primdata.toggled.connect(self.check_generate_primdata_bool)
    
    def finished_conversion(self):
        if self.progressbar_conversion.value() == self.progressbar_conversion.maximum():
            this_conversion_done = f'Conversion: {self.finished_conversion_item} Complete...'
            conversion_done_qmessagebox = QMessageBox.information(self, 'SUCCESS!', this_conversion_done, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            if (conversion_done_qmessagebox == QMessageBox.StandardButton.Ok) or (conversion_done_qmessagebox == QMessageBox.StandardButton.Close):
                self.progressbar_conversion.setValue(0)
                self.progressbar_conversion.setDisabled(True)
                self.convert_model_button.setEnabled(True)
                if self.mode_selected == 'Single':
                    self.change_conversion_mode_batch.setEnabled(True)
                    self.parent_combobox.setDisabled(True)
                elif self.mode_selected == 'All':
                    self.change_conversion_mode_single.setEnabled(True)
                    self.parent_combobox.setDisabled(True)
                self.check_animations.setEnabled(True)
                self.check_texture.setEnabled(True)
                self.check_tmd_report.setEnabled(True)
                self.check_prim_report.setEnabled(True)
                self.check_generate_primdata.setEnabled(True)

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
    def __init__(self, parent: QObject | None = ..., conversion_list=list, worldmap_asset_dict=dict, 
                 anim_convert=bool, texture_convert=bool, sc_folder=str, tmd_report=bool, 
                 prim_report=bool, generate_primdata=bool, deploy_folder=str) -> None:
        super().__init__(parent)
        self.conversion_list = conversion_list
        self.worldmap_asset_dict = worldmap_asset_dict
        self.anim_convert = anim_convert
        self.texture_convert = texture_convert
        self.sc_folder = sc_folder
        self.tmd_report = tmd_report
        self.prim_report = prim_report
        self.generate_primdata = generate_primdata
        self.deploy_folder = deploy_folder
    
    def run(self):
        progress_conversion = 0
        for this_model_to_convert in self.conversion_list:
            self.single_convert = WorldMapConversionInterface(list_convert=this_model_to_convert, 
                                                            assets_worldmap_database=self.worldmap_asset_dict, 
                                                            conv_anims=self.anim_convert, 
                                                            conv_text=self.texture_convert, 
                                                            sc_folder=self.sc_folder, 
                                                            tmd_report=self.tmd_report, 
                                                            prim_report=self.prim_report, 
                                                            generate_primdata=self.generate_primdata, 
                                                            deploy_folder=self.deploy_folder)
            progress_conversion += 1
            self.progress_signal.emit(progress_conversion)

if __name__ == '__main__':
    absolute_path_current = os.path.abspath(os.getcwd())
    absolute_path_databases = f'{absolute_path_current}\\Databases'
    icon_app = f'{absolute_path_current}\\Resources\\DD_Eye.ico'
    testapp = QApplication(sys.argv)
    build_database = database_handler.DatabaseHandler(database_path=absolute_path_databases)
    testwindow = WorldMapConversionMainWindow(icon=icon_app, assets_database=build_database.full_database)
    sys.exit(testapp.exec())