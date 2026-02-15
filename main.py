import os
import json
import shutil
from datetime import datetime
from PyQt6.QtWidgets import QInputDialog, QApplication, QWidget,  QGridLayout, QListWidget, QPushButton, QLineEdit
from PyQt6.QtGui import QIcon


save_path = os.getenv("APPDATA") + "/garn47/"
valid_saves = []


def remove_backup():
    try:
        os.remove(save_path + "backup" + "/saveData.garnular")
        os.remove(save_path + "backup" + "/saveTrophy.garnular")
        os.rmdir(save_path + "backup")
    except Exception as err:
        print(err)


def create_backup():
    if "backup" not in os.listdir(save_path):
        os.mkdir(save_path + "backup")

    shutil.copy(save_path + "saveData.garnular", save_path + "backup")
    shutil.copy(save_path + "saveTrophy.garnular", save_path + "backup")


def remove_save(name):
    scan_saves()
    valid = False
    for save in valid_saves:
        if save["name"] == name:
            valid = True
    if valid:
        shutil.rmtree(f"./saves/{name}")
    else:
        print(f"Save {name} doesn't exist!")


def create_save(name, date_saved):
    os.mkdir(f"./saves/{name}")
    d = {
        "name": name,
        "date_saved": date_saved
    }
    str = json.dumps(d)
    with open(f"./saves/{name}/save.json", "w") as f:
        f.write(str)
    shutil.copy(save_path + "saveData.garnular", f"./saves/{name}")
    shutil.copy(save_path + "saveTrophy.garnular", f"./saves/{name}")


def load_save(name):
    if "backup" not in os.listdir(save_path):
        print("Error: No backup. Please make a backup before trying to load a save")
        return

    scan_saves()
    valid = False
    for save in valid_saves:
        if save["name"] == name:
            valid = True
            break

    if not valid:
        print(f"Save {name} doesnt exist")
        return

    try:
        os.remove(save_path + "/saveData.garnular")
        os.remove(save_path + "/saveTrophy.garnular")
    except Exception as err:
        print(err)
    shutil.copy(f"./saves/{name}/saveData.garnular",
                save_path + "/saveData.garnular")
    shutil.copy(f"./saves/{name}/saveTrophy.garnular",
                save_path + "saveTrophy.garnular")


def rename_save(name, newname):
    if newname not in os.listdir("./saves"):
        os.mkdir(f"./saves/{newname}")
    shutil.copy(f"./saves/{name}/saveData.garnular", f"./saves/{newname}")
    shutil.copy(f"./saves/{name}/saveTrophy.garnular", f"./saves/{newname}")
    date_saved = None
    with open(f"./saves/{name}/save.json", "r") as f:
        d = json.load(f)
        date_saved = d["date_saved"]

    d = {
        "name": newname,
        "date_saved": date_saved
    }
    str = json.dumps(d)
    with open(f"./saves/{newname}/save.json", "w") as f:
        f.write(str)
    remove_save(name)


def scan_saves():
    global valid_saves
    # search for "valid" saves (just checks if it has the save.json file)
    saves = os.listdir("./saves")
    valid_saves = []
    for save in saves:
        files = os.listdir("./saves/" + save)
        if "save.json" in files:
            with open(f"./saves/{save}/save.json") as f:
                d = json.load(f)
                valid_saves.append(
                    {"path": f"./saves/{save}", "name": d["name"], "date_saved": d["date_saved"]})


if "backup" not in os.listdir(save_path):
    print("No Backup folder in save path, creating new one...")
    create_backup()


# qt functions
def save_button_clicked():
    text, ok = QInputDialog.getText(
        window, "Dialog", "Save name:")
    if ok and text:
        create_save(text, datetime.now().strftime("%m-%d-%y %H:%M:%S"))
        list_widget.addItem(text)


def load_button_clicked():
    row = list_widget.currentRow()
    if row >= 0:
        item = list_widget.item(row)
        load_save(item.text())
        list_widget.addItem(item)


def delete_button_clicked():
    row = list_widget.currentRow()
    if row >= 0:
        item = list_widget.takeItem(row)
        remove_save(item.text())
        del item


def rename_button_clicked():
    text, ok = QInputDialog.getText(
        window, "Dialog", "New name:"
    )
    if ok and text:
        row = list_widget.currentRow()
        if row >= 0:
            item = list_widget.takeItem(row)
            rename_save(item.text(), text)
            del item
            list_widget.addItem(text)


def path_text_box_textChanged():
    global save_path
    save_path = path_text_box.text()
    print(save_path)


if "saves" not in os.listdir("./"):
    os.mkdir("./saves")

scan_saves()
items = []
for save in valid_saves:
    items.append(save["name"])


app = QApplication([])

window = QWidget(windowTitle="GarnSaver")
window.setWindowIcon(QIcon("./assets/icon.png"))


layout = QGridLayout(window)
window.setLayout(layout)


path_text_box = QLineEdit(
    placeholderText=save_path,
    clearButtonEnabled=True
)
path_text_box.textChanged.connect(path_text_box_textChanged)


list_widget = QListWidget(window)
list_widget.addItems(items)
save_button = QPushButton("Save")
save_button.clicked.connect(save_button_clicked)

load_button = QPushButton("Load")
load_button.clicked.connect(load_button_clicked)

delete_button = QPushButton("Delete")
delete_button.clicked.connect(delete_button_clicked)

rename_button = QPushButton("Rename")
rename_button.clicked.connect(rename_button_clicked)

layout.addWidget(path_text_box, 4, 1, 4, 1)
layout.addWidget(list_widget, 0, 0, 4, 1)
layout.addWidget(save_button, 0, 1)
layout.addWidget(load_button, 1, 1)
layout.addWidget(delete_button, 2, 1)
layout.addWidget(rename_button, 3, 1)

window.show()


# start event loop
app.exec()
