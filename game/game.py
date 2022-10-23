import os
from typing import Callable, List, Optional, Tuple
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from game.player import Player


DIR_MEDIA: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")


class Cell:
    """
    Class for cell on playing field.
    """

    def __init__(self, row: int, column: int) -> None:
        """
        :param row: row of cell;
        :param column: column of cell.
        """

        self._button: QPushButton = None
        self._column: int = column
        self._default_style_sheet: str = None
        self._row: int = row
        self._state: str = ""

    @property
    def position(self) -> Tuple[int, int]:
        """
        :return: row and column of cell.
        """

        return self._row, self._column

    @property
    def state(self) -> str:
        """
        :return: cell state.
        """

        return self._state

    @property
    def value(self) -> int:
        """
        :return: integer of cell state.
        """

        if self.state == "o":
            return 1
        if self.state == "x":
            return -1
        return 0

    def change_state(self, new_state: str):
        """
        Method changes cell state.
        :param new_state: new state of cell.
        """

        self._state = new_state
        self._button.setIcon(QIcon())
        self._button.setIcon(QIcon(os.path.join(DIR_MEDIA, f"{new_state}.png")))
        size = self._button.size()
        self._button.setIconSize(QSize(3 * size.width() // 4, 3 * size.height() // 4))

    def clear(self) -> None:
        """
        Method clears state of cell.
        """

        self._state = ""
        self._button.setIcon(QIcon())
        self._button.setEnabled(True)
        self._button.setFlat(False)
        self._button.setStyleSheet(self._default_style_sheet)

    def disable(self) -> None:
        self._button.setEnabled(False)
        self._button.setFlat(True)

    def paint_cell(self) -> None:
        color = "#2481BA" if self.state == "o" else "#1CB34B"
        self._button.setStyleSheet(f"background-color: {color};")

    def set_button(self, button: QPushButton, callback_func: Callable) -> None:
        """
        Method sets button to cell.
        :param button: button;
        :param callback_func:
        """

        self._button = button
        self._button.clicked.connect(lambda: callback_func(self))
        self._default_style_sheet = self._button.styleSheet()


class PlayingField:
    """
    Class for playing field.
    """

    def __init__(self, rows_and_columns: int) -> None:
        """
        :param rows_and_columns: number of rows and columns on playing field.
        """

        self._rows_and_columns: int = rows_and_columns
        self._cells: List[List[Cell]] = [[Cell(row, column) for column in range(self._rows_and_columns)]
                                         for row in range(self._rows_and_columns)]

    def check(self) -> Tuple[bool, Optional[List[Cell]]]:
        """
        Method checks playing field for finish.
        :return: True if game should be finished and list of correct cells.
        """

        empty_cells = False

        for row in range(self._rows_and_columns):
            row_sum = 0
            cells = []
            for column in range(self._rows_and_columns):
                row_sum += self._cells[row][column].value
                cells.append(self._cells[row][column])
                if self._cells[row][column].value == 0:
                    empty_cells = True
            if abs(row_sum) == 3:
                return True, cells

        for column in range(self._rows_and_columns):
            column_sum = 0
            cells = []
            for row in range(self._rows_and_columns):
                column_sum += self._cells[row][column].value
                cells.append(self._cells[row][column])
                if self._cells[row][column].value == 0:
                    empty_cells = True
            if abs(column_sum) == 3:
                return True, cells

        for diagonal in (0, 1):
            diagonal_sum = 0
            cells = []
            for index in range(self._rows_and_columns):
                column = index if diagonal == 0 else self._rows_and_columns - index - 1
                diagonal_sum += self._cells[index][column].value
                cells.append(self._cells[index][column])
                if self._cells[row][column].value == 0:
                    empty_cells = True
            if abs(diagonal_sum) == 3:
                return True, cells

        return not empty_cells, None

    def clear(self) -> None:
        """
        Method clears field.
        """

        for cells_in_column in self._cells:
            for cell in cells_in_column:
                cell.clear()

    def end_game(self) -> None:
        for row in range(self._rows_and_columns):
            for column in range(self._rows_and_columns):
                if self._cells[row][column].value == 0:
                    self._cells[row][column].disable()

    def set_buttons_to_cells(self, buttons: List[List[QPushButton]], callback_func: Callable) -> None:
        """
        Method sets buttons to cells of playing field.
        :param buttons: list of buttons;
        :param callback_func:
        """

        for row in range(self._rows_and_columns):
            for column in range(self._rows_and_columns):
                self._cells[row][column].set_button(buttons[row][column], callback_func)


class Game(QObject):
    """
    Class is responsible for game.
    """

    ROWS_AND_COLUMNS: int = 3
    game_over: pyqtSignal = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self._players: List[Player] = []
        self._playing_field: PlayingField = PlayingField(self.ROWS_AND_COLUMNS)
        self._turn: int = 0

    def _end_game(self, cells: List[Cell]) -> None:
        """
        Method ends game.
        :param cells: list of cells that are lined up.
        """

        if cells:
            for cell in cells:
                cell.paint_cell()
        self._playing_field.end_game()

    @pyqtSlot(Cell)
    def make_move(self, cell: Cell) -> None:
        """
        Slot handles move in game.
        :param cell: cell clicked on.
        """

        if not cell.state:
            cell.change_state(self._players[self._turn].symbol)
            to_finish, cells = self._playing_field.check()
            if to_finish:
                self._end_game(cells)
                self.game_over.emit(self._turn if cells else -1)
            self._turn = (self._turn + 1) % 2

    def set_buttons(self, buttons: List[List[QPushButton]]) -> None:
        self._playing_field.set_buttons_to_cells(buttons, self.make_move)

    def start_game(self, player_1: Player, player_2: Player) -> None:
        """
        Method starts new game.
        :param player_1: first player;
        :param player_2: second player.
        """

        self._players = [player_1, player_2]
        self._playing_field.clear()
        self._turn = 0
