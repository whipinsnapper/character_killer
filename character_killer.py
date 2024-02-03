import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QFileDialog, QDialog, QProgressBar
import os, shutil

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

        layout = QVBoxLayout()

        # Dropdown menu
        self.dropdown_label = QLabel('Select a character:')
        self.dropdown_menu = QComboBox()
        options = names
        self.dropdown_menu.addItems(options)

        layout.addWidget(self.dropdown_label)
        layout.addWidget(self.dropdown_menu)

        # Button to select ISO
        self.file_button = QPushButton('MKWii ISO')
        self.file_button.clicked.connect(self.selectFile)
        layout.addWidget(self.file_button)

        # Button to select source SZS
        self.file_button = QPushButton('Source Character')
        self.file_button.clicked.connect(self.selectSourceSZS)
        layout.addWidget(self.file_button)

        # Button to select folder
        self.folder_button = QPushButton('Output Folder')
        self.folder_button.clicked.connect(self.selectFolder)
        layout.addWidget(self.folder_button)

        # Button to call function
        self.call_function_button = QPushButton('Patch Files!')
        self.call_function_button.clicked.connect(self.callFunction)
        layout.addWidget(self.call_function_button)

        self.setLayout(layout)

    def selectFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select MKWii ISO')
        if filename:
            self.iso_location = filename

    def selectSourceSZS(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select Source SZS')
        if filename:
            self.source_szs = filename

    def selectFolder(self):
        foldername = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if foldername:
            self.output_directory = foldername

    def callFunction(self):
        self.character_name = self.dropdown_menu.currentText()

        self.iso_error = 0
        self.output_error = 0
        self.source_error = 0

        if self.iso_location == '':
            self.iso_error = 1
        if self.output_directory == '':
            self.output_error = 1
        if self.source_szs == '':
            self.source_error = 1

        errors = self.iso_error + self.output_error + self.source_error

        if errors > 0:
            popup_dialog = PopupError(self.iso_error, self.output_error, self.source_error, self)
            popup_dialog.exec_()
        
        else:
            main_operation(self.iso_location, self.output_directory, self.character_name, self.source_szs)
            popup_dialog = PopupComplete(self.output_directory, self)
            popup_dialog.exec_()

class PopupError(QDialog):
    def __init__(self, iso_error, output_error, source_error, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Error')

        layout = QVBoxLayout()

        self.error_msg = QLabel('Error! Please do the following things:\n')
        layout.addWidget(self.error_msg)

        if iso_error == 1:
            self.iso_label = QLabel('Select MKWii ISO')
            layout.addWidget(self.iso_label)
        if output_error == 1:
            self.output_label = QLabel('Select output directory')
            layout.addWidget(self.output_label)
        if source_error == 1:
            self.source_label = QLabel('Select source SZS')
            layout.addWidget(self.source_label)

        self.setLayout(layout)

class PopupComplete(QDialog):
    def __init__(self, output_directory, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Complete')
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
    app = QApplication(sys.argv)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())
