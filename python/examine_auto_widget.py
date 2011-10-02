#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import examine_widget_gui

import glob

import utils
import shared

import examine_note_widget
import table_play_widget

import task_attack


class ExamineAutoWidget(QtGui.QFrame):
    select_note = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Window)

        ### setup GUI
        self.ui = examine_widget_gui.Ui_Frame()
        self.ui.setupUi(self)

        self.st = None
        self.dyn = None


    def examine(self, type, st, dyn, task_stable, finger=None):
        self.st = st
        self.dyn = dyn

        text = utils.st_to_text(self.st) + " string "
        if finger:
            text += "      " + str(finger) + "       "
        self.ui.string_label.setText(text)

        text = utils.dyn_to_text(self.dyn)
        self.ui.dyn_label.setText(text)

        if type == "stable":
            self.task_stable = task_stable
            self.setup_stable()
            self.ui.examine_type_label.setText("stable")
        elif type == "attack":
            self.task_attack = task_stable # oh god ick
            self.setup_attack(finger)
            self.ui.examine_type_label.setText("attack")
        elif type == "dampen":
            self.task_dampen = task_stable # oh god ick
            self.setup_dampen()
            self.ui.examine_type_label.setText("dampen")

        self.show()

    def setup_attack(self, finger):
        if not self.task_attack.notes:
            self.task_attack.get_attack_files_info()

        num_rows = self.task_attack.num_rows
        num_cols = self.task_attack.num_cols

        forces_strings = map(str, self.task_attack.forces)
        # setup table and gui
        self.table = table_play_widget.TablePlayWidget(self)
        self.table.set_column_names(forces_strings)

        # clear previous widget if exists
        if self.ui.verticalLayout.count() == 3:
            self.ui.verticalLayout.takeAt(2)

        self.ui.verticalLayout.addWidget(self.table)

        self.table.action_play.connect(self.table_play)
        self.table.select_previous.connect(self.clear_select)
        self.table.select_new.connect(self.select_plot)
        self.table.action_quit.connect(self.table_quit)
        self.ui.button_play.clicked.connect(self.table_play)

        self.table.clearContents()
        self.table.setRowCount(num_rows)

        self.examines = []
        for row in range(num_rows):
            examines_row = []
            for col in range(num_cols):
                examines_row.append(None)
            self.examines.append( examines_row )
                    
        # populate table
        for row in range(num_rows):
            # oh god ick: names of rows vs. cols
            for col in range(num_cols):
                examine = examine_note_widget.ExamineNoteWidget(
                    shared.examine_note_widget.PLOT_ATTACK)

                examine.set_examine_note( self.task_attack.notes[row][col] )
                self.examines[row][col] = examine

                self.table.setCellWidget(row, col,
                    examine.plot_actions)
                self.table.setRowHeight(row, 50.0)
                if col % 1 == 0 and col > 0:
                    self.examines[row][col].plot_actions.set_border([0,0,0,1])
                if col % 1 == 0 and col < num_cols-1:
                    self.examines[row][col].plot_actions.set_border([0,1,0,0])
                if row % num_rows == 0 and row > 0:
                    self.examines[row][col].plot_actions.set_border([1,0,0,0])
                if row % num_rows == (num_rows-1) and row < num_rows:
                    self.examines[row][col].plot_actions.set_border([0,0,1,0])



    def setup_stable(self):
        if not self.task_stable.notes:
            self.task_stable.get_stable_files_info()

        # clear previous widget if exists
        if self.ui.verticalLayout.count() == 3:
            self.ui.verticalLayout.takeAt(2)

        num_rows = self.task_stable.num_rows
        num_cols = self.task_stable.num_cols
        num_counts = self.task_stable.num_counts

        # setup table and gui
        self.table = table_play_widget.TablePlayWidget(self)
        col_names = []
        col_names.extend(map(lambda x: "Low %i" % x, self.task_stable.finger_midis))
        col_names.extend(map(lambda x: "Middle %i" % x, self.task_stable.finger_midis))
        col_names.extend(map(lambda x: "High %i" % x, self.task_stable.finger_midis))
        self.table.set_column_names(col_names)
        self.ui.verticalLayout.addWidget(self.table)

        self.table.action_play.connect(self.table_play)
        self.table.select_previous.connect(self.clear_select)
        self.table.select_new.connect(self.select_plot)
        self.table.action_quit.connect(self.table_quit)
        self.ui.button_play.clicked.connect(self.table_play)


        self.table.clearContents()
        self.table.setRowCount(num_rows)

        for i in range(num_rows):
            item = QtGui.QTableWidgetItem()
            mod = i % num_counts + 1
            item.setText(str("%.2f-%i" % (self.task_stable.extras[0][i/num_counts], mod)))
            self.table.setVerticalHeaderItem(i, item)

        self.examines = []
        for row in range(num_rows):
            examines_row = []
            for col in range(num_cols):
                examines_row.append(None)
            self.examines.append( examines_row )
                    
        fmis = len(self.task_stable.finger_midis)
        # populate table
        for row in range(num_rows):
            for col in range(num_cols):
                examine = examine_note_widget.ExamineNoteWidget(
                    shared.examine_note_widget.PLOT_STABLE)
                examine.set_examine_note( self.task_stable.notes[row][col] )
                self.examines[row][col] = examine

                self.table.setCellWidget(row, col,
                    examine.plot_actions)
                self.table.setRowHeight(row, 50.0)
                if col % fmis == 0 and col > 0:
                    self.examines[row][col].plot_actions.set_border([0,0,0,1])
                if col % fmis == 2 and col < (num_cols-1):
                    self.examines[row][col].plot_actions.set_border([0,1,0,0])
                if row % num_counts == 0 and row > 0:
                    self.examines[row][col].plot_actions.set_border([1,0,0,0])
                if row % num_counts == (num_counts-1) and row < num_rows:
                    self.examines[row][col].plot_actions.set_border([0,0,1,0])

    def setup_dampen(self):
        if not self.task_dampen.notes:
            self.task_dampen.get_dampen_files_info()

        num_rows = len(self.task_dampen.extras)
        num_counts = self.task_dampen.REPS

        forces_strings = map(str, self.task_dampen.extras)
        # setup table and gui
        self.table = table_play_widget.TablePlayWidget(self)
        self.table.set_column_names(forces_strings)

        # clear previous widget if exists
        if self.ui.verticalLayout.count() == 3:
            self.ui.verticalLayout.takeAt(2)

        self.ui.verticalLayout.addWidget(self.table)

        self.table.action_play.connect(self.table_play)
        self.table.select_previous.connect(self.clear_select)
        self.table.select_new.connect(self.select_plot)
        self.table.action_quit.connect(self.table_quit)
        self.ui.button_play.clicked.connect(self.table_play)

        self.table.clearContents()
        self.table.setRowCount(3)

        self.examines = []
        for row in range(num_counts):
            examines_row = []
            for col in range(num_rows):
                examines_row.append(None)
            self.examines.append( examines_row )

        # populate table
        for row in range(num_counts):
            for col in range(num_rows):
                # TODO: define a PLOT_DAMPEN
                examine = examine_note_widget.ExamineNoteWidget(
                    shared.examine_note_widget.PLOT_ATTACK)

                examine.set_examine_note(self.task_dampen.notes[col][row] )
                self.examines[row][col] = examine

                self.table.setCellWidget(row, col,
                    examine.plot_actions)
                self.table.setRowHeight(row, 50.0)

                if col % 1 == 0 and col > 0:
                    self.examines[row][col].plot_actions.set_border([0,0,0,1])
                if col % 1 == 0 and col < 3:
                    self.examines[row][col].plot_actions.set_border([0,1,0,0])
                if row % num_counts == 0 and row > 0:
                    self.examines[row][col].plot_actions.set_border([1,0,0,0])
                if row % num_counts == (num_counts-1) and row < num_rows:
                    self.examines[row][col].plot_actions.set_border([0,0,1,0])



    def table_play(self):
        row = self.table.currentRow()
        col = self.table.currentColumn()
        #print "table_play:", row, col
        if row >= 0 and col >= 0:
            self.examines[row][col].play()

    def table_train(self):
        row = self.table.currentRow()
        col = self.table.currentColumn()
#        print "table train:", row, col
#        if row >= 0:
#            filename = self.examines[row][col].get_zoom_bare()
#            print "train ", filename
            #self.examine.load_file(wavfile)
            #self.string_train.set_note_label(self.ui.note_label)
            #self.string_train.retrain(self.st, self.dyn, wavfile)

    def clear_select(self, row, col):
        self.examines[row][col].plot_actions.clear_selection()
        self.examines[row][col].plot_actions.highlight(False)

    def select_plot(self, row, col):
        self.examines[row][col].plot_actions.highlight(True)
        #print self.examines[row][col].examine_note.basename
        self.select_note.emit()

    def get_selected_filename(self):
        row = self.table.currentRow()
        col = self.table.currentColumn()
        if row >= 0 and col >= 0:
            examine = self.examines[row][col]
            return examine.examine_note.basename, examine.examine_note.note_text
        return None

#    def keyPressEvent(self, event):
#        print "examine note auto, key event:", event
        #QtGui.QFrame.keyPressEvent(self.parent, event)
        #self.parent.keyPressEvent(event)
        #QtCore.QCoreApplication.sendEvent(event)

    def table_quit(self):
        shared.examine_main.reset()
        self.close()

