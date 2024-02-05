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
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QFileDialog, QDialog, QFrame
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

    #This works but puts them all in their own little directory tree, which I'd like not to happen.
    #The second for loop moves the SZS files back to the root folder and removes the leftover folders.
    for file in filenames:
        os.system(f'wit extract {iso_location} --files "+{file}" --DEST "{output_directory}/.tmp/{file[:-4]}"')
    for file in filenames:
        shutil.move(f"{output_directory}/.tmp/{file[:-4]}/files/Race/Kart/{file}", f"{output_directory}/.tmp/")
        shutil.rmtree(f"{output_directory}/.tmp/{file[:-4]}")

def modify_szs(output_directory, filenames, source_szs):
    #EXTRACT source SZS file
    os.system(f'wszst extract "{source_szs}" --DEST "{output_directory}/.tmp/source_szs"')
    os.system(f'wszst extract "{output_directory}/.tmp/source_szs/driver_model.brres" --DEST "{output_directory}/.tmp/source_brres" --ext')
    
    #EXTRACT all SZS files with WSZST
    for file in filenames:
        os.system(f'wszst extract "{output_directory}/.tmp/{file}" --DEST "{output_directory}/.tmp/extracted_szs/{file[:-4]}"')
        os.system(f'wszst extract "{output_directory}/.tmp/extracted_szs/{file[:-4]}/driver_model.brres" --DEST "{output_directory}/.tmp/extracted_brres/{file[:-4]}" --ext')
    
    #Replace model.mdl, model_lod.mdl, and textures in all extracted BRRES files
    for file in filenames:
        os.remove(f"{output_directory}/.tmp/extracted_brres/{file[:-4]}/3DModels(NW4R)/model.mdl")
        shutil.copy(f"{output_directory}/.tmp/source_brres/3DModels(NW4R)/model.mdl", f"{output_directory}/.tmp/extracted_brres/{file[:-4]}/3DModels(NW4R)/model.mdl")

        os.remove(f"{output_directory}/.tmp/extracted_brres/{file[:-4]}/3DModels(NW4R)/model_lod.mdl")
        shutil.copy(f"{output_directory}/.tmp/source_brres/3DModels(NW4R)/model_lod.mdl", f"{output_directory}/.tmp/extracted_brres/{file[:-4]}/3DModels(NW4R)/model_lod.mdl")

        shutil.rmtree(f"{output_directory}/.tmp/extracted_brres/{file[:-4]}/Textures(NW4R)")
        shutil.copytree(f"{output_directory}/.tmp/source_brres/Textures(NW4R)", f"{output_directory}/.tmp/extracted_brres/{file[:-4]}/Textures(NW4R)")

    #CREATE BRRES and replace in extracted SZS folders
    for file in filenames:
        os.remove(f"{output_directory}/.tmp/extracted_szs/{file[:-4]}/driver_model.brres")
        os.system(f'wszst create "{output_directory}/.tmp/extracted_brres/{file[:-4]}" --DEST "{output_directory}/.tmp/extracted_szs/{file[:-4]}/driver_model.brres"')

    #CREATE SZS from folders with WSZST
    for file in filenames:
        os.system(f'wszst create "{output_directory}/.tmp/extracted_szs/{file[:-4]}" --DEST "{output_directory}/updated_szs/{file}"')
    
    #Removes temporary folder
    shutil.rmtree(f"{output_directory}/.tmp")

def main_operation(iso_location, output_directory, character_name, source_szs):
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

    for name, id, size in characters:
        if character_name == name:
            filenames = get_filenames(size, id)
            extract_from_iso(iso_location, filenames, output_directory)
            modify_szs(output_directory, filenames, source_szs)

class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.iso_location = ''
        self.source_szs = ''
        self.output_directory = ''
        self.character_name = ''

        self.initUI()

    def initUI(self):
        names = ["Baby Mario", "Baby Luigi", "Baby Peach", "Baby Daisy", "Toad", "Toadette", "Koopa Troopa", "Dry Bones",
                 "Mario", "Luigi", "Peach", "Daisy", "Yoshi", "Birdo", "Diddy Kong", "Bowser Jr.",
                 "Wario", "Waluigi", "Donkey Kong", "Bowser", "King Boo", "Rosalina", "Funky Kong", "Dry Bowser"]

        self.setWindowTitle('Character Killer')
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Character dropdown menu
        self.dropdown_label = QLabel('Select a character:')
        self.dropdown_menu = QComboBox()
        options = names
        self.dropdown_menu.addItems(options)

        layout.addWidget(self.dropdown_label)
        layout.addWidget(self.dropdown_menu)

        #Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Button to select ISO
        self.file_button = QPushButton('MKWii ISO')
        self.file_button.clicked.connect(self.selectFile)
        layout.addWidget(self.file_button)

        # Button to select source SZS
        self.file_button = QPushButton('Source Character')
        self.file_button.clicked.connect(self.selectSourceSZS)
        layout.addWidget(self.file_button)

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

        self.setLayout(layout)

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
        self.character_name = self.dropdown_menu.currentText()
        
        #Gets file extensions for the ISO file and source SZS file
        iso_extension = os.path.splitext(self.iso_location)[1][1:]
        szs_extension = os.path.splitext(self.source_szs)[1][1:]

        error_messages = {
            "iso_empty": "MKWii ISO location is not specified.",
            "iso_ext": "MKWii ISO must end in either .iso or .wbfs.",
            "output_error": "Output directory is not specified.",
            "source_error": "Source SZS file is not specified.",
            "source_ext": "Source SZS file must end in .szs."
        }

        #Returns 1 for each error found
        errors = {
            "iso_empty": int(self.iso_location == ''),
            "iso_ext": int(iso_extension.lower() not in ['iso', 'wbfs']),
            "output_error": int(self.output_directory == ''),
            "source_error": int(self.source_szs == ''),
            "source_ext": int(szs_extension.lower() != 'szs')
        }

        errors_present = [key for key, value in errors.items() if value]

        if errors_present:
            error_messages_str = "\n".join([error_messages[error] for error in errors_present])
            popup_dialog = PopupError(error_messages_str, self)
            popup_dialog.exec_()
        else:
            main_operation(self.iso_location, self.output_directory, self.character_name, self.source_szs)
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
        
        self.setLayout(layout)
    
    def openFolder(self):
        os.system(f'explorer "{os.path.realpath(f"{self.output_directory}/updated_szs")}')
        self.close()
    def closePopup(self):
        self.close()

if __name__ == '__main__':
    check_dependencies(["wit", "wszst"])
    app = QApplication(sys.argv)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())
