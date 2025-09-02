# This file is not very interesting (it handles the settings)

import os
from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QWidget, QScrollArea, QGroupBox, Qt, QDialogButtonBox, QFrame, QEvent
)
from aqt.utils import tooltip, showInfo

from . import utils
from . import config
from .template_manager import apply_template_injections

class NoScrollComboBox(QComboBox):
    """
    A custom QComboBox that:
    1. Disables changing items with the mouse wheel.
    2. Shows a popup with a fixed max height and a scrollbar.
    3. Perfectly aligns the popup with the combo box.
    4. Uses a clean frame, removing the extra top/bottom scroll buttons.
    5. Hides the corner resize handle (QSizeGrip).
    """
    def wheelEvent(self, event: QEvent):
        # Ignore the wheel event to prevent scrolling.
        event.ignore()

    def showPopup(self):
        super().showPopup()
        
        # Get the popup's view and its container window
        popup_view = self.view()
        popup_window = popup_view.window()

        # --- 1. Calculate height dynamically instead of using a fixed value ---
        
        # Define a reasonable maximum height in pixels
        MAX_HEIGHT = 400 

        # Calculate the ideal height needed to display all items.
        # sizeHintForRow(0) gets the height of a single item.
        # frameWidth() accounts for the top and bottom borders.
        content_height = self.count() * popup_view.sizeHintForRow(0) + 2 * popup_view.frameWidth()
        
        # The final height is the smaller of the content height and the max height
        final_height = min(content_height, MAX_HEIGHT)

        # Apply this calculated height to the main popup container
        popup_window.setFixedHeight(final_height)
        
        # Ensure scrollbar appears only if content is taller than the popup
        popup_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # --- 2. Align popup and match width (your alignment code is good) ---
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        popup_window.move(global_pos)

        # Optional but recommended: Match the popup width to the combo box width
        popup_window.setFixedWidth(self.width())

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CodeMirror Configuration")
        self.setMinimumWidth(550)
        self.resize(550, 600)

        self.all_models = sorted(mw.col.models.all(), key=lambda m: m['name'])
        
        layout = QVBoxLayout(self)
        layout.addWidget(self._create_theme_group())

        self.injection_widgets = []
        self.injection_rows_layout = QVBoxLayout()
        layout.addWidget(self._create_dynamic_notetype_group(
            "2. Inject CodeMirror into Note Types",
            "Select note types where you want to use CodeMirror code blocks.",
            self.injection_rows_layout,
            lambda: self._add_row_ui(self.injection_rows_layout, self.injection_widgets)
        ), 1)

        self.bypass_widgets = []
        self.bypass_rows_layout = QVBoxLayout()
        layout.addWidget(self._create_dynamic_notetype_group(
            "3. Bypass 'Empty Field' Check",
            "Select note types to bypass Anki's check for empty fields.",
            self.bypass_rows_layout,
            lambda: self._add_row_ui(self.bypass_rows_layout, self.bypass_widgets)
        ), 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_settings()

    def _create_theme_group(self):
        group = QGroupBox("1. Select Global Code Theme")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Choose the one theme to be used everywhere (editor and reviewer)."))
        
        self.theme_combo = NoScrollComboBox()
        self.theme_combo.setToolTip("This theme will be used for all code blocks.")
        self.theme_combo.setMaxVisibleItems(20)
        
        theme_path = utils.USER_FILES_PATH / "codemirror" / "theme"
        if theme_path.exists():
            for filename in sorted(os.listdir(theme_path)):
                if filename.endswith(".css"):
                    self.theme_combo.addItem(os.path.splitext(filename)[0])
        
        layout.addWidget(self.theme_combo)
        group.setLayout(layout)
        return group
    
    def _create_dynamic_notetype_group(self, title, description_text, rows_layout, add_function):
        group = QGroupBox(title)
        main_layout = QVBoxLayout(group)
        
        description = QLabel(description_text)
        description.setWordWrap(True)
        main_layout.addWidget(description)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_content.setLayout(rows_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)

        add_button = QPushButton("Add Note Type")
        add_button.clicked.connect(add_function)
        main_layout.addWidget(add_button)
        
        return group
    
    def _add_row_ui(self, rows_layout, widget_list, selected_id=None):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0,0,0,0)

        combo = NoScrollComboBox()
        combo.addItem("Select Note Type...", None)
        for model in self.all_models:
            combo.addItem(model['name'], model['id'])

        # NEW: Apply the fixes to this dynamically created combo box.
        combo.setMaxVisibleItems(15)
        
        remove_button = QPushButton("Remove")
        row_layout.addWidget(combo, 1)
        row_layout.addWidget(remove_button)

        widget_tuple = (row_widget, combo)
        widget_list.append(widget_tuple)

        remove_button.clicked.connect(lambda: self._remove_row_ui(widget_tuple, widget_list, rows_layout))
        rows_layout.addWidget(row_widget)

        if selected_id:
            index = combo.findData(selected_id)
            if index != -1:
                combo.setCurrentIndex(index)

    def _remove_row_ui(self, widget_tuple, widget_list, rows_layout):
        if widget_tuple in widget_list:
            row_widget, _ = widget_tuple
            widget_list.remove(widget_tuple)
            rows_layout.removeWidget(row_widget)
            row_widget.deleteLater()

    def load_settings(self):
        current_theme = config.CONFIG.get(config.CONFIG_KEY_GLOBAL_THEME, 'dracula')
        self.theme_combo.setCurrentText(current_theme)

        inject_ids = config.CONFIG.get(config.CONFIG_KEY_INJECT_MODELS, [])
        for model_id in inject_ids:
            self._add_row_ui(self.injection_rows_layout, self.injection_widgets, model_id)

        bypass_ids = config.CONFIG.get(config.CONFIG_KEY_BYPASS_MODELS, [])
        for model_id in bypass_ids:
            self._add_row_ui(self.bypass_rows_layout, self.bypass_widgets, model_id)

    def _get_selected_ids_from_widgets(self, widget_list):
        selected_ids = []
        seen_ids = set()
        has_duplicates = False
        for _, combo in widget_list:
            model_id = combo.currentData()
            if model_id:
                if model_id in seen_ids:
                    has_duplicates = True
                    continue
                selected_ids.append(model_id)
                seen_ids.add(model_id)
        
        if has_duplicates:
            showInfo("One or more Note Types were selected multiple times. Duplicates have been ignored.")
        
        return selected_ids

    def on_save(self):
        selected_theme = self.theme_combo.currentText()
        if not selected_theme:
            showInfo("Please select a theme.")
            return

        injected_ids = self._get_selected_ids_from_widgets(self.injection_widgets)
        bypassed_ids = self._get_selected_ids_from_widgets(self.bypass_widgets)

        config.CONFIG[config.CONFIG_KEY_GLOBAL_THEME] = selected_theme
        config.CONFIG[config.CONFIG_KEY_INJECT_MODELS] = injected_ids
        config.CONFIG[config.CONFIG_KEY_BYPASS_MODELS] = bypassed_ids
        
        config.save_config()
        tooltip("Applying changes to note types...")
        apply_template_injections()
        tooltip("Configuration saved and applied.")
        self.accept()

def show_config_dialog():
    dialog = ConfigDialog(mw)
    dialog.exec()