import sys
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QLineEdit
from SetupIK_launcher import get_dir_path, delete_path

parent = None

def getMayaMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

try:
    import maya.cmds as cmds
    from ..utils.MayaUtils import MayaUtilsIKHandle
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    in_maya = True
    parent = getMayaMainWindow()
except ImportError:
    in_maya = False

try:
    from pymxs import runtime as rt # type: ignore
    from qtmax import GetQMaxMainWindow # type: ignore
    from ..utils.MaxUtils import MaxUtilsIKChain
    in_max = True
    parent = GetQMaxMainWindow()
except ImportError:
    in_max = False

class SetupUi(QDialog):
    def __init__(self, parent=parent):
        super(SetupUi, self).__init__(parent)
        
        if in_maya:
            self.Handle = "Handle"
        elif in_max:
            self.Handle = "Chain"
            
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setWindowTitle(f'Setup IK {self.Handle}')
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.init_ui()

    def init_ui(self):
        self.label = QLabel(f"<p style='text-align: center;'>Select one or more IK {self.Handle}</p>")
        
        self.hbox = QHBoxLayout()
        self.label_edit = QLabel("Prefix:")
        self.edit_line = QLineEdit()
        self.edit_line.setPlaceholderText("Enter prefix...")
        self.hbox.addWidget(self.label_edit)
        self.hbox.addWidget(self.edit_line)
        
        self.button = QPushButton("Setup")
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.clicked.connect(self.on_button_click)
        
        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.hbox)
        self.main_layout.addWidget(self.button) 

    def on_button_click(self):
        prefix = f"{self.edit_line.text()}_" if self.edit_line.text() else ""
        if in_maya:
            self.maya_utils = MayaUtilsIKHandle(prefix)
            self.maya_utils.setup_ik_handle()
        elif in_max:
            self.max_utils = MaxUtilsIKChain(prefix)
            self.max_utils.setup_ik_chain()
            
    def closeEvent(self, e):
        # from SplitBlendshapes_Launcher import get_dir_path, delete_path
        # dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        dir_path = get_dir_path()
        delete_path(dir_path)
        e.accept()


# DCC start
def start():
    global win
    if 'win' in globals() and win.isVisible():
            win.close()
    dir_path = get_dir_path()
    if dir_path != sys.path[0]:
        sys.path.insert(0, dir_path)
    win = SetupUi()
    win.show()