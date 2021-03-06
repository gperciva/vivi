#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import examine_widget_gui

import glob

import utils
import shared

import examine_note_widget
import table_play_widget

#import task_attack


class ExamineAutoWidget(QtGui.QFrame):
    select_note = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Window)

        ### setup GUI
        self.ui = examine_widget_gui.Ui_Frame()
        self.ui.setupUi(self)

        self.st = None
        self.dyn = None


    def examine(self, mode, st, dyn, task_stable, finger=None):
        self.mode = mode
        self.st = st
        self.dyn = dyn

        text = utils.st_to_text(self.st) + " string "
        if finger:
            text += "      " + str(finger) + "       "
        self.ui.string_label.setText(text)

        text = utils.dyn_to_text(self.dyn)
        self.ui.dyn_label.setText(text)

        if mode == "stable":
            self.task_stable = task_stable
            self.setup_stable()
            self.ui.examine_type_label.setText("stable")
        elif mode == "verify":
            self.task_verify = task_stable # oh god ick
            self.setup_verify(finger)
            self.ui.examine_type_label.setText("verify")
        elif mode == "attack":
            self.task_attack = task_stable # oh god ick
            self.setup_attack(finger, 1)
            self.ui.examine_type_label.setText("attack")
        elif mode == "second-att":
            self.task_attack = task_stable # oh god ick
            self.setup_attack(finger, 2)
            self.ui.examine_type_label.setText("second-att")
        elif mode == "dampen":
            self.task_dampen = task_stable # oh god ick
            self.setup_dampen()
            self.ui.examine_type_label.setText("dampen")

        self.show()

    def setup_attack(self, finger, onetwo):
        #print "setup attack, onetwo:", onetwo
        if not self.task_attack.notes:
            self.task_attack.get_attack_files_info()

        num_rows = self.task_attack.num_rows
        num_cols = self.task_attack.num_cols

        if onetwo == 1:
            forces_strings = map(lambda x: str("%.3f" % x),
                self.task_attack.test_range1)
        elif onetwo == 2:
            forces_strings = map(lambda x: str("%.3f" % x),
                self.task_attack.test_range2)
        # setup table and gui
        self.table = table_play_widget.TablePlayWidget(self)
        self.table.set_column_names(forces_strings)

        if onetwo == 1:
            Ks = map(lambda x: str("%.2f" % x),
                self.task_attack.K_range1)
        elif onetwo == 2:
            Ks = map(lambda x: str("%.2f" % x),
                self.task_attack.K_range2)
        self.table.set_row_names(Ks)

        if onetwo == 1:
            extra_text = "Best: %.3f N, %.2f" % (
                self.task_attack.best_attack1,
                self.task_attack.best_stability1)
        elif onetwo == 2:
            extra_text = "Best: %.3f N, %.2f" %(
                self.task_attack.best_attack2,
                self.task_attack.best_stability2)
        self.ui.extra_label.setText(extra_text)

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

        if onetwo == 1:
            notes = self.task_attack.notes1
        elif onetwo == 2:
            notes = self.task_attack.notes2
 
        # populate table
        for row in range(num_rows):
            # oh god ick: names of rows vs. cols
            for col in range(num_cols):
                examine = examine_note_widget.ExamineNoteWidget(
                    shared.examine_note_widget.PLOT_ATTACK)

                examine.set_examine_note(notes[row][col] )
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

    def setup_verify(self, finger):
        fmi = finger
        if not self.task_verify.notes:
            self.task_verify.get_verify_files_info()

        num_rows = self.task_verify.num_rows
        num_cols = self.task_verify.num_cols

        forces_strings = ['-'] * self.task_verify.num_cols
        #forces_strings = map(lambda x: str("%.3f" % x),
        #    self.task_verify.test_range)
        #print forces_strings
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

                #examine.set_examine_note(self.task_verify.notes[fmi][row][col] )
                try:
                    examine.set_examine_note(self.task_verify.notes[row][col] )
                except:
                    continue
                self.examines[row][col] = examine
                #print row, col, self.task_verify.notes[row][col][0].basename

                row_divs = self.task_verify.REPS
                self.table.setCellWidget(row, col,
                    examine.plot_actions)
                self.table.setRowHeight(row, 50.0)
                if col == 0:
                    self.examines[row][col].plot_actions.set_border([0,1,0,0])
                if col == 8:
                    self.examines[row][col].plot_actions.set_border([0,0,0,1])
                if row % row_divs == 0 and row > 0:
                    self.examines[row][col].plot_actions.set_border([1,0,0,0])
                if row % row_divs == (row_divs-1) and row > 0:
                    self.examines[row][col].plot_actions.set_border([0,0,1,0])
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
        num_cols = self.task_stable.num_cols*3
        num_counts = self.task_stable.num_counts

        # setup table and gui
        self.table = table_play_widget.TablePlayWidget(self)
        #print self.task_stable.forces_initial
        col_names = []
        col_names = [ str("%.2f" % x) for x in self.task_stable.forces_init_used]
        #col_names.extend(map(lambda x: "Low %i" % x, self.task_stable.finger_midis))
        #col_names.extend(map(lambda x: "Middle %i" % x, self.task_stable.finger_midis))
        #col_names.extend(map(lambda x: "High %i" % x, self.task_stable.finger_midis))
        #for i, c in enumerate(col_names):
        #    fmi = i % len(self.task_stable.forces_initial)
        #    fm = self.task_stable.finger_midis[fmi]
        #    j = i / len(self.task_stable.forces_initial)
        #    force = self.task_stable.forces_initial[fm][j]
        #    col_names[i] += ": %.2f" % force
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
        #print num_rows, num_cols
        # populate table
        for row in range(num_rows):
            for col in range(num_cols):
                examine = examine_note_widget.ExamineNoteWidget(
                    shared.examine_note_widget.PLOT_STABLE)

                # FIXME: replace with button?
                fmi = col / 3
                notescol = col % 3
                #print row, col, notescol, fmi
                examine.set_examine_note( self.task_stable.notes[fmi][row][notescol] )
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

        num_rows = self.task_dampen.num_rows
        num_cols = self.task_dampen.num_cols

        forces_strings = map(str, self.task_dampen.extras[0])
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
            for col in range(num_cols):
                # TODO: define a PLOT_DAMPEN
                examine = examine_note_widget.ExamineNoteWidget(
                    shared.examine_note_widget.PLOT_ATTACK)

                examine.set_examine_note(self.task_dampen.notes[row][col] )
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

