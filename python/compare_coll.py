#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import examine_widget_gui
import check_coll
import table_play_widget

import utils
import shared

import visualize_cats

class CompareColl(QtGui.QFrame):
    row_delete = QtCore.pyqtSignal(str, name="row_delete")
    row_retrain = QtCore.pyqtSignal(str, name="row_retrain")
    row_prev = None
    
    def __init__(self, files):
        QtGui.QFrame.__init__(self)
        # set up GUI
        self.ui = examine_widget_gui.Ui_Frame()
        self.ui.setupUi(self)

        self.files = files
        self.check_coll = check_coll.CheckColl(files)

        self.table = table_play_widget.TablePlayWidget(self)
        self.table.set_column_names(["cat", "judgements", "dyn", "finger"])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 500)
        self.table.setColumnWidth(2, 50)
        self.table.setColumnWidth(3, 50)

        self.ui.verticalLayout.addWidget(self.table)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.table.action_play.connect(self.table_play)
        self.table.action_delete.connect(self.table_row_delete)
        self.table.action_retrain.connect(self.table_row_retrain)
        self.table.action_quit.connect(self.table_quit)
        self.table.itemSelectionChanged.connect(self.selection_changed)
        self.ui.button_play.clicked.connect(self.table_play)

        # add extra buttons
        button = QtGui.QPushButton("re&train")
        self.ui.examine_commands.insertWidget(1, button)
        button.clicked.connect(self.table_row_retrain)
        button = QtGui.QPushButton("&delete")
        self.ui.examine_commands.insertWidget(2, button)
        button.clicked.connect(self.table_row_delete)


    def display(self):
        text = utils.st_to_text(self.st) + " string "
        self.ui.string_label.setText(text)

        #text = utils.dyn_to_text(self.dyn)
        self.ui.dyn_label.setText("")

        self.ui.examine_type_label.setText("collection")

    def get_dynamic_hack(self, filename):
        bv = abs(float(filename.split("_")[5]))
        if bv >= 0.39:
            return "f"
        elif bv > 0.34:
            return "mf - f"
        elif bv > 0.32:
            return "mf"
        elif bv > 0.27:
            return "mp - mf"
        elif bv > 0.25:
            return "mp"
        elif bv > 0.21:
            return "mp - p"
        elif bv >= 0.19:
            return "p"
        else:
            return "eh?"

    def get_finger_hack(self, filename):
        finger = int(round(float(filename.split("_")[2])))
        return str(finger)

    def compare(self, st, coll):
        self.st = st
        self.display()

        self.check_coll.check(coll, self.st)
        self.data = list(self.check_coll.data)

        self.table.clearContents()
        self.table.setRowCount(len(self.data))
        for i, datum in enumerate(self.data):
            table_item = QtGui.QTableWidgetItem(str(datum[1]))
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(i, 0, table_item)
            vc = visualize_cats.VisualizeCats()
            vc.set_data(datum[1], datum[2])
            self.table.setCellWidget(i, 1, vc)

            table_item = QtGui.QTableWidgetItem(
                str(self.get_dynamic_hack(datum[0])))
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            font = table_item.font()
            font.setWeight(75)
            font.setItalic(True)
            table_item.setFont(font)
            self.table.setItem(i, 2, table_item)

            table_item = QtGui.QTableWidgetItem(
                str(self.get_finger_hack(datum[0])))
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(i, 3, table_item)
        self.table_focus()

    def table_focus(self):
        self.table.setFocus()
        self.show()

    def table_play(self):
        row = self.table.currentRow()
        if row >= 0:
            wavfile = self.data[row][0]
            utils.play(wavfile)

    def get_selected_filename(self):
        row = self.table.currentRow()
        col = self.table.currentColumn()

    def get_selected_filename(self):
        row = self.table.currentRow()
        wavfilename = self.data[row][0]
        filename = wavfilename[0:-4] # remove .wav
        return filename

    def selection_changed(self):
        filename = self.get_selected_filename()
        shared.examine_main.load_file(filename, self.files)
        shared.examine_main.load_note("")

        if self.row_prev >= 0:
            self.table.cellWidget(self.row_prev, 1).highlight(False)
        row = self.table.currentRow()
        self.table.cellWidget(row, 1).highlight(True)
        self.row_prev = row

    def table_row_delete(self):
        filename = self.get_selected_filename()
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.data.pop(row)
        self.row_delete.emit(filename)

    def table_row_retrain(self):
        # TODO: update display with new category
        filename = self.get_selected_filename()
        self.row_retrain.emit(filename)

    def table_quit(self):
        shared.examine_main.reset()
        self.close()

