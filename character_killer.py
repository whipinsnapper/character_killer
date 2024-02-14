import sys, os, shutil

def check_dependencies(programs):
    errors = 0
    for program in programs:
        if shutil.which(program) is None:
            sys.stderr.write(f"{program} is not installed or is not added to PATH.")
            errors += 1
    if errors > 0:
        raise SystemExit(1)

try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QComboBox, QPushButton, QLabel, QFileDialog, QDialog, QFrame, QProgressBar
    from PyQt5.QtGui import QFont
    from PyQt5.QtCore import Qt
except:
    sys.stderr.write("PyQt5 is not installed. Install it with the command: pip install PyQt5")
    check_dependencies(["wit", "wszst"])
    raise SystemExit(1)

def get_filenames(size, id):
    """Returns a list of all MKWii character filenames."""
    
    filenames = []
    vehicles = ["a_bike-", "a_kart-", "b_bike-", "b_kart-", "c_bike-", "c_kart-",
                "df_bike-", "df_kart-", "d_bike-", "d_kart-", "e_bike-", "e_kart-"]
    for vehicle in vehicles:
        filenames.append(f"{size}{vehicle}{id}.szs")
    return filenames

def extract_from_iso(iso_location, filenames, output_directory):
    """Extract all necessary files from original MKWii ISO with WIT"""

    for file in filenames:
        os.system(f'wit extract "{iso_location}" --files "+{file}" --DEST "{output_directory}/.tmp/{file[:-4]}"')
        gui.updateProgressBar()
    for file in filenames:
        for root, dirs, files in os.walk(f"{output_directory}/.tmp"):
            if file in files:
                newfile = os.path.join(root, file)
        shutil.move(newfile, f"{output_directory}/.tmp")
        shutil.rmtree(f"{output_directory}/.tmp/{file[:-4]}")
        gui.updateProgressBar()

def extract_szs(output_directory, filenames, subfolder):
    """Extract a list of SZS files to a specified subfolder."""

    for file in filenames:
        os.system(f'wszst extract "{output_directory}/.tmp/{file}" --DEST "{output_directory}/.tmp/{subfolder}/szs/{file[:-4]}"')
        gui.updateProgressBar()

def extract_driver_brres(output_directory, filenames, subfolder):
    """Extract a list of BRRES files to a specified subfolder."""

    for file in filenames:
        os.system(f'wszst extract "{output_directory}/.tmp/{subfolder}/szs/{file[:-4]}/driver_model.brres" --DEST "{output_directory}/.tmp/{subfolder}/brres/{file[:-4]}" --ext')
        gui.updateProgressBar()

def replace_driver_files(output_directory, anim_filenames, source_szs_trunc):
    """Replaces model.mdl, model_lod.mdl, and textures folder of a list of extracted BRRES files."""

    for file in anim_filenames:
            os.remove(f"{output_directory}/.tmp/anim/brres/{file[:-4]}/3DModels(NW4R)/model.mdl")
            shutil.copy(f"{output_directory}/.tmp/source/brres/{source_szs_trunc[:-4]}/3DModels(NW4R)/model.mdl", f"{output_directory}/.tmp/anim/brres/{file[:-4]}/3DModels(NW4R)/model.mdl")
            gui.updateProgressBar()

            os.remove(f"{output_directory}/.tmp/anim/brres/{file[:-4]}/3DModels(NW4R)/model_lod.mdl")
            shutil.copy(f"{output_directory}/.tmp/source/brres/{source_szs_trunc[:-4]}/3DModels(NW4R)/model_lod.mdl", f"{output_directory}/.tmp/anim/brres/{file[:-4]}/3DModels(NW4R)/model_lod.mdl")
            gui.updateProgressBar()

            shutil.rmtree(f"{output_directory}/.tmp/anim/brres/{file[:-4]}/Textures(NW4R)")
            shutil.copytree(f"{output_directory}/.tmp/source/brres/{source_szs_trunc[:-4]}/Textures(NW4R)", f"{output_directory}/.tmp/anim/brres/{file[:-4]}/Textures(NW4R)")
            gui.updateProgressBar()

def create_driver_brres(output_directory, anim_filenames):
   for file in anim_filenames:
        os.remove(f"{output_directory}/.tmp/anim/szs/{file[:-4]}/driver_model.brres")
        os.system(f'wszst create "{output_directory}/.tmp/anim/brres/{file[:-4]}" --DEST "{output_directory}/.tmp/anim/szs/{file[:-4]}/driver_model.brres"')
        gui.updateProgressBar()

def replace_kart_brres(output_directory, kart_filenames, anim_filenames):
    for i in range(12):
        k_file = kart_filenames[i]
        a_file = anim_filenames[i]
        os.remove(f"{output_directory}/.tmp/anim/szs/{a_file[:-4]}/kart_model.brres")
        shutil.copy(f"{output_directory}/.tmp/kart/szs/{k_file[:-4]}/kart_model.brres", f"{output_directory}/.tmp/anim/szs/{a_file[:-4]}/kart_model.brres")
        gui.updateProgressBar()

def modify_szs(output_directory, anim_filenames, kart_filenames, source_szs, final_filenames):
    source_szs_trunc = os.path.basename(source_szs)
    
    shutil.copy(source_szs, f"{output_directory}/.tmp/{source_szs_trunc}")
    gui.updateProgressBar()

    extract_szs(output_directory, [source_szs_trunc], "source")
    extract_driver_brres(output_directory, [source_szs_trunc], "source")
    
    extract_szs(output_directory, anim_filenames, "anim")
    extract_driver_brres(output_directory, anim_filenames, "anim")
    
    extract_szs(output_directory, kart_filenames, "kart")

    replace_driver_files(output_directory, anim_filenames, source_szs_trunc)

    create_driver_brres(output_directory, anim_filenames)

    replace_kart_brres(output_directory, kart_filenames, anim_filenames)

    # Create SZS from folders with WSZST
    for i in range(12):
        a_file = anim_filenames[i]
        f_file = final_filenames[i]
        os.system(f'wszst create "{output_directory}/.tmp/anim/szs/{a_file[:-4]}" --DEST "{output_directory}/updated_szs/{f_file}"')
        gui.updateProgressBar()
    
    #Removes temporary folder
    shutil.rmtree(f"{output_directory}/.tmp")
    gui.updateProgressBar()

def zip_characters():
    names = ["Baby Mario", "Baby Luigi", "Baby Peach", "Baby Daisy", "Toad", "Toadette", "Koopa Troopa", "Dry Bones",
             "Mario", "Luigi", "Peach", "Daisy", "Yoshi", "Birdo", "Diddy Kong", "Bowser Jr.",
             "Wario", "Waluigi", "Donkey Kong", "Bowser", "King Boo", "Rosalina", "Funky Kong", "Dry Bowser"]
    ids = ["bmr", "blg", "bpc", "bds", "ko", "kk", "nk", "ka",
           "mr", "lg", "pc", "ds", "ys", "ca", "dd", "jr",
           "wr", "wl", "dk", "kp", "kt", "rs", "fk", "bk"]
    sizes = ["s", "s", "s", "s", "s", "s", "s", "s",
             "m", "m", "m", "m", "m", "m", "m", "m",
             "l", "l", "l", "l", "l", "l", "l", "l"]

    characters = zip(names, ids, sizes)
    return characters

def main_operation(iso_location, output_directory, slot_name, anim_name, kart_name, source_szs):
    characters = zip_characters()

    if os.path.exists(os.path.join(output_directory, ".tmp")):
        shutil.rmtree(os.path.join(output_directory, ".tmp"))

    for name, id, size in characters:
        if slot_name == name:
            final_filenames = get_filenames(size, id)
        if anim_name == name:
            anim_filenames = get_filenames(size, id)
            extract_from_iso(iso_location, anim_filenames, output_directory)
        if kart_name == name:
            kart_filenames = get_filenames(size, id)
            if kart_name != anim_name:
                extract_from_iso(iso_location, kart_filenames, output_directory)
    
    modify_szs(output_directory, anim_filenames, kart_filenames, source_szs, final_filenames)

class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.iso_location = ''
        self.source_szs = ''
        self.output_directory = ''
        self.slot_name = ''

        self.initUI()

    def initUI(self):
        names = []
        characters = zip_characters()
        for name, id, size in characters:
            names.append(name)
        options = ["Default"] + names

        self.setWindowTitle('Character Killer v1.2.0')
        self.setFixedWidth(455)
        self.setFixedHeight(335)

        layout = QVBoxLayout()
        top_layout = QGridLayout()

        self.setLayout(layout)
        layout.addLayout(top_layout)

        # Slot dropdown menu
        self.dropdown1_label = QLabel('Slot:')
        self.dropdown1_menu = QComboBox()
        self.dropdown1_menu.addItems(names)

        top_layout.addWidget(self.dropdown1_label, 0, 0)
        top_layout.addWidget(self.dropdown1_menu, 1, 0)

        # Animation dropdown menu
        self.dropdown2_label = QLabel('Animations:')
        self.dropdown2_menu = QComboBox()
        self.dropdown2_menu.addItems(options)

        top_layout.addWidget(self.dropdown2_label, 0, 1)
        top_layout.addWidget(self.dropdown2_menu, 1, 1)

        # Vehicle dropdown menu
        self.dropdown3_label = QLabel('Vehicles:')
        self.dropdown3_menu = QComboBox()
        self.dropdown3_menu.addItems(options)

        top_layout.addWidget(self.dropdown3_label, 0, 2)
        top_layout.addWidget(self.dropdown3_menu, 1, 2)

        #Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)

        # Button to select ISO
        self.iso_button = QPushButton('MKWii ISO')
        self.iso_button.clicked.connect(self.selectFile)
        layout.addWidget(self.iso_button)

        # Button to select source SZS
        self.source_button = QPushButton('Source Character')
        self.source_button.clicked.connect(self.selectSourceSZS)
        layout.addWidget(self.source_button)

        # Button to select output folder
        self.folder_button = QPushButton('Output Folder')
        self.folder_button.clicked.connect(self.selectFolder)
        layout.addWidget(self.folder_button)

        # Another separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)

        # Button to patch files
        self.patch_button = QPushButton('Patch Files!')
        self.patch_button.setFixedHeight(50)
        font = QFont("Arial", 9)
        font.setBold(True)
        self.patch_button.setFont(font)
        self.patch_button.clicked.connect(self.patchFiles)
        layout.addWidget(self.patch_button)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 159)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def updateProgressBar(self):
        progress = self.progress_bar.value()
        if progress < 159:
            self.progress_bar.setValue(progress + 1)
        else:
            self.progress_bar.setValue(159)

    def selectFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select MKWii ISO')
        if filename:
            self.iso_location = filename
            print(f"MKWii ISO: {filename}")

    def selectSourceSZS(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select Source SZS')
        if filename:
            self.source_szs = filename
            print(f"Source SZS: {filename}")

    def selectFolder(self):
        foldername = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if foldername:
            self.output_directory = foldername
            print(f"Output directory: {foldername}")

    def patchFiles(self):
        self.progress_bar.setValue(0)
        self.slot_name = self.dropdown1_menu.currentText()
        self.anim_name = self.dropdown2_menu.currentText()
        self.kart_name = self.dropdown3_menu.currentText()

        if self.anim_name == "Default":
            self.anim_name = self.slot_name
        if self.kart_name == "Default":
            self.kart_name = self.slot_name

        characters = zip_characters()
        for name, id, size in characters:
            if self.slot_name == name:
                slot_size = size
            if self.anim_name == name:
                anim_size = size
            if self.kart_name == name:
                kart_size = size
        
        #Gets file extensions for the ISO file and source SZS file
        iso_extension = os.path.splitext(self.iso_location)[1][1:]
        szs_extension = os.path.splitext(self.source_szs)[1][1:]

        error_messages = {
            "iso_empty": "MKWii ISO location is not specified.",
            "iso_ext": "MKWii ISO must end in either .iso or .wbfs.",
            "output_error": "Output directory is not specified.",
            "output_exists": "Output directory is already in use.",
            "source_error": "Source SZS file is not specified.",
            "source_ext": "Source SZS file must end in .szs.",
            "size_mismatch": "Slot, animation, and vehicle sizes must be the same."
        }

        #Returns 1 for each error found
        errors = {
            "iso_empty": int(self.iso_location == ''),
            "iso_ext": int(iso_extension.lower() not in ['iso', 'wbfs']),
            "output_error": int(self.output_directory == ''),
            "output_exists": int(os.path.exists(os.path.join(self.output_directory, "extracted_szs"))),
            "source_error": int(self.source_szs == ''),
            "source_ext": int(szs_extension.lower() != 'szs'),
            "size_mismatch": int(slot_size != anim_size or slot_size != kart_size)
        }

        errors_present = [key for key, value in errors.items() if value]

        if errors_present:
            error_messages_str = "\n".join([error_messages[error] for error in errors_present])
            popup_dialog = PopupError(error_messages_str, self)
            popup_dialog.exec_()
        else:
            main_operation(self.iso_location, self.output_directory, self.slot_name, self.anim_name, self.kart_name, self.source_szs)
            popup_dialog = PopupComplete(self.output_directory, self)
            popup_dialog.exec_()

class PopupError(QDialog):
    def __init__(self, error_messages_str, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Error')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()

        self.error_msg = QLabel('The following errors were found:\n')
        layout.addWidget(self.error_msg)
        
        self.errors = QLabel(error_messages_str)
        layout.addWidget(self.errors)
            
        self.setLayout(layout)

class PopupComplete(QDialog):
    def __init__(self, output_directory, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Complete')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout()

        self.output_directory = output_directory

        self.msg = QLabel("All SZS files successfully patched!\nOpen folder now?")
        layout.addWidget(self.msg)

        self.yes_button = QPushButton('Yes')
        self.yes_button.clicked.connect(self.openFolder)
        layout.addWidget(self.yes_button)

        self.no_button = QPushButton('No')
        self.no_button.clicked.connect(self.closePopup)
        layout.addWidget(self.no_button)
        
        gui.progress_bar.setValue(159)
        self.setLayout(layout)
    
    def openFolder(self):
        os.system(f'explorer "{os.path.realpath(f"{self.output_directory}/updated_szs")}')
        gui.progress_bar.setValue(0)
        self.close()
    def closePopup(self):
        gui.progress_bar.setValue(0)
        self.close()

if __name__ == '__main__':
    check_dependencies(["wit", "wszst"])
    app = QApplication(sys.argv)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())
