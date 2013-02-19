#!/usr/bin/env python
""" Qt widget for getting user judgement about an audio file """

from PyQt4 import QtGui, QtCore
import judge_audio_gui

import utils # to play sound
import collection
import vivi_defines

JUDGEMENT_CANCEL = -1234

#pylint: disable=C0103,R0904
# I can't change the overriden method names, nor the Qt naming scheme.

class JudgeAudioWidget(QtGui.QFrame):
    """ Qt widget for getting user judgement about an audio file """
    judged_cat = QtCore.pyqtSignal(int, name='judged_cat')

    def __init__(self, mainwindow_layout):
        """ constructor """
        QtGui.QFrame.__init__(self)
        self.ui = judge_audio_gui.Ui_Frame()
        self.ui.setupUi(self)

        self.mainwindow_layout = mainwindow_layout
        self.use_layout = self.mainwindow_layout

        self.judge_filename = None

        # attach buttons to self._clicked
        self.buttons = QtGui.QButtonGroup(self)
        for widget in self.ui.groupBox.findChildren(QtGui.QPushButton):
            self.buttons.addButton(widget)
        self.buttons.buttonClicked.connect(self._clicked)

        self.display(show=False)


    ### basic GUI framework
    def display(self, parent=None, position=-1, show=True, main=False):
        """ adds widget to the appropriate parent """
        if main:
            self.use_layout = self.mainwindow_layout
        elif parent:
            self.use_layout = parent
        if show:
            self.use_layout.insertWidget(position, self)
            self.show()
            self.setFocus()
        else:
            self.clearFocus()
            self.hide()
            if self.parent():
                self.parent().layout().removeWidget(self)
                if self.use_layout != self.mainwindow_layout:
                    self.parent().table_focus()
            self.setParent(None)

    def _clicked(self, event):
        """ user clicked on a button inside the widget """
        self._user_key(int(event.objectName()[11]))

    def keyPressEvent(self, event):
        """ override default handler """
        try:
            key = chr(event.key())
        except ValueError:
            QtGui.QFrame.keyPressEvent(self, event)
            return
        key = key.lower()
        if (key >= '0') and (key <= '9'):
            self._user_key(int(key))
        elif (key == 'q'):
            self._user_key(9)
        else:
            QtGui.QFrame.keyPressEvent(self, event)


    ### actual code
    def user_judge(self, judge_filename):
        """ prompt user to judge this audio file """
        self.judge_filename = judge_filename
        self.display()
        utils.play(self.judge_filename+'.wav')

    def _user_key(self, key):
        """ user pressed this key or button """
        if (key > 0) and (key <= vivi_defines.CATEGORIES_NUMBER):
            self.judged_cat.emit(key - vivi_defines.CATEGORIES_CENTER_OFFSET)
        elif key == 8:
            utils.play(self.judge_filename+'.wav')
        elif key == 9:
            self.judged_cat.emit(JUDGEMENT_CANCEL)
        elif key == 0:
            self.judged_cat.emit(vivi_defines.CATEGORY_WEIRD)

