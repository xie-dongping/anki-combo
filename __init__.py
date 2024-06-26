from aqt import mw

from aqt.utils import showInfo, qconnect
from aqt.qt import *
from aqt import gui_hooks
from PyQt6.QtCore import Qt

class StatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QWidget { background: transparent; }")

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setAlignment(Qt.AlignCenter)

        self.timeout = 20
        self.interval_ms = 50
        self.decrement_opacity = 1.0 / (self.timeout * 1000.0 / self.interval_ms)
        self.font_size = 65

    def show_number(self, number):
        self.label.setText("Longest streak of combo: {number}".format(number=number))

        self.label.setStyleSheet("""
            QLabel {
                font-size: %dpx;
                color: rgba(255, 0, 0, 0.8);
            }
        """ % self.font_size)
        self.opacity = 1.0

        # Set up the QTimer for the animation
        if not hasattr(self, "timer"):
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_stylesheet)
            self.timer.start(self.interval_ms)
        else:
            self.timer.stop()
            self.timer.start(self.interval_ms)

    def update_stylesheet(self):
        new_opacity = max(0.0, self.opacity - self.decrement_opacity)
        self.opacity = new_opacity
        self.font_size = new_pt_size

        if new_opacity > 0.3:
            self.label.setstylesheet("""
                qlabel {
                    font-size: %dpx;
                    color: rgba(245, 13, 9, %f);
                }
            """ % (self.font_size, 0.8))
        else:
            self.label.setStyleSheet("""
                QLabel {
                    font-size: %dpx;
                    color: rgba(245, 13, 9, %f);
                }
            """ % (self.font_size, self.opacity))

        if new_opacity <= 0.0:
            self.timer.stop()

class NumberStarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QWidget { background: transparent; }")

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # Create a layout for the combined widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        # layout.addWidget(self.star_label)
        layout.setAlignment(Qt.AlignCenter)

        self.timeout = 12
        self.interval_ms = 50
        self.decrement_opacity = 1.0 / (self.timeout * 1000.0 / self.interval_ms)
        self.decrement_font_size = 35.0 / (self.timeout * 1000.0 / self.interval_ms)

        self.number = 0
        self.skip = 0
        self.interval_skip_reset_ms = self.timeout * 1000
        self._max_combo = [0]

    def get_combo(self):
        return self._max_combo[-1]

    def clear_combo(self):
        self._max_combo = [0]

    def _update_combo(self, new_value):
        if self._max_combo[-1] < new_value:
            self._max_combo.append(new_value)
        else:
            self._max_combo.append(self._max_combo[-1])
        if len(self._max_combo) > 500:
            self._max_combo = self._max_combo[-500:]

    def _undo_combo(self):
        if len(self._max_combo) > 1:
            self._max_combo = self._max_combo[:-1]

    def increment(self):
        if self.skip > 0:
            self.skip = max(0, self.skip - 1)
            return

        self._set_number(self.number + 1)
        self._update_combo(self.number + 1)

    def clear_skip(self):
        self.skip = 0

    def undo(self):
        self._undo_combo()
        self.skip = self.skip + 1
        if not hasattr(self, "timer_skip_reset"):
            self.timer_skip_reset = QTimer(self)
            self.timer_skip_reset.timeout.connect(self.clear_skip)
            self.timer_skip_reset.start(self.interval_skip_reset_ms)
        else:
            self.timer_skip_reset.stop()
            self.timer_skip_reset.start(self.interval_skip_reset_ms)

    def _set_number(self, number):
        self.number = number

        if number == 1:
            self.label.setText("Nice!")
        elif number <= 5:
            self.label.setText("Nice{exclamation}\nCombo: {number}!".format(
                number=number,
                exclamation="!"*number
            ))
        elif number > 5 and number <= 10:
            self.label.setText("Great{exclamation}\nCombo: {number}!".format(
                number=number,
                exclamation="!"*(number-4)
            ))
        elif number > 10 and number <= 15:
            self.label.setText("Excellent{exclamation}\nCombo: {number}!".format(
                number=number,
                exclamation="!"*(number-10)
            ))
        elif number > 15:
            self.label.setText("Wonderful{exclamation}\nCombo: {number}!".format(
                number=number,
                exclamation="!"*max(6, (number-15))
            ))
        else:
            self.label.setText("Super!\nCombo: {}!".format(number))

        self.font_size = max(75, 40 + number)
        self.label.setStyleSheet("""
            QLabel {
                font-size: %dpx;
                color: rgba(255, 0, 0, 0.8);
            }
        """ % self.font_size)
        self.opacity = 1.0

        # Set up the QTimer for the animation
        if not hasattr(self, "timer"):
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_stylesheet)
            self.timer.start(self.interval_ms)
        else:
            self.timer.stop()
            self.timer.start(self.interval_ms)

    def update_stylesheet(self):
        new_opacity = max(0.0, self.opacity - self.decrement_opacity)
        new_pt_size = max(10.0, self.font_size - self.decrement_font_size)
        self.opacity = new_opacity
        self.font_size = new_pt_size

        # Adjust the color property with red and the new opacity
        self.label.setStyleSheet("""
            QLabel {
                font-size: %dpx;
                color: rgba(245, 13, 9, %f);
            }
        """ % (new_pt_size, new_opacity*0.8))

        # self.timer.start(100)  # Update every 100 milliseconds
        if new_opacity <= 0.0:
            self.timer.stop()
            self.number = 0

def increment() -> None:
    if not hasattr(mw, "comboLabel"):
        # Create a QGraphicsScene
        scene = QGraphicsScene()
        combo = NumberStarWidget()
        combo.increment()
        mw.comboLabel = combo

        proxy_widget = QGraphicsProxyWidget()
        proxy_widget.setWidget(combo)
        scene.addItem(proxy_widget)

        graphics_view = QGraphicsView(scene, mw)
        graphics_view.setRenderHint(QPainter.Antialiasing, True)
        graphics_view.setInteractive(False)  # Disable interaction with the overlay
        graphics_view.setStyleSheet("background: transparent; border: none;")
        graphics_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Set the position of the graphics view directly
        mw.comboGraphicsView = graphics_view

        # Show the graphics view
        graphics_view.show()

    else:
        mw.comboLabel.increment()

    mw.comboGraphicsView.setGeometry(0, 0, mw.width(), mw.height())

def undo() -> None:
    if not hasattr(mw, "comboLabel"):
        return
    mw.comboLabel.undo()
    mw.comboGraphicsView.setGeometry(0, 0, mw.width(), mw.height())

def show_stats():
    if not hasattr(mw, "comboLabel"):
        return
    if not hasattr(mw, "comboStatsLabel"):
        # Create a QGraphicsScene
        scene = QGraphicsScene()
        combo_stats = StatsWidget()
        mw.comboStatsLabel = combo_stats

        proxy_widget = QGraphicsProxyWidget()
        proxy_widget.setWidget(combo_stats)
        scene.addItem(proxy_widget)

        graphics_view = QGraphicsView(scene, mw)
        graphics_view.setRenderHint(QPainter.Antialiasing, True)
        graphics_view.setInteractive(False)  # Disable interaction with the overlay
        graphics_view.setStyleSheet("background: transparent; border: none;")
        graphics_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        mw.comboStatsGraphicsView = graphics_view

        graphics_view.show()

    mw.comboStatsGraphicsView.setGeometry(0, 0, mw.width(), mw.height())
    mw.comboStatsLabel.show_number(mw.comboLabel.get_combo())
    mw.comboLabel.clearCombo()

def combo_increment_hook(reviewer, card, ease) -> None:
    if ease != 1:
        increment()

def combo_undo_hook(_) -> None:
    undo()

def show_stats_hook() -> None:
    show_stats()

gui_hooks.reviewer_did_answer_card.append(combo_increment_hook)
gui_hooks.state_did_undo.append(combo_undo_hook)

action_increment = QAction("test increment", mw)
qconnect(action_increment.triggered, increment)
mw.form.menuTools.addAction(action_increment)

action_undo = QAction("test undo", mw)
qconnect(action_undo.triggered, undo)
mw.form.menuTools.addAction(action_undo)

action_show_stats = QAction("Show Max Combo Streak", mw)
qconnect(action_show_stats.triggered, show_stats)
mw.form.menuTools.addAction(action_show_stats)
