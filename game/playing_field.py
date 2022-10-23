import os
from typing import Callable, List, Optional, Tuple
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from gui.utils import DIR_MEDIA


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
        self._symbol: str = ""

    @property
    def button(self) -> QPushButton:
        return self._button

    @property
    def position(self) -> Tuple[int, int]:
        """
        :return: row and column of cell.
        """

        return self._row, self._column

    @property
    def symbol(self) -> str:
        """
        :return: cell symbol.
        """

        return self._symbol

    @property
    def value(self) -> int:
        """
        :return: integer of cell state.
        """

        if self.symbol == "o":
            return 1
        if self.symbol == "x":
            return -1
        return 0

    def change_symbol(self, new_symbol: str):
        """
        Method changes cell symbol.
        :param new_symbol: new symbol of cell.
        """

        self._symbol = new_symbol
        self._button.setIcon(QIcon())
        self._button.setIcon(QIcon(os.path.join(DIR_MEDIA, f"{new_symbol}.png")))
        size = self._button.size()
        self._button.setIconSize(QSize(3 * size.width() // 4, 3 * size.height() // 4))

    def clear(self) -> None:
        """
        Method clears state of cell.
        """

        self._symbol = ""
        self._button.setIcon(QIcon())
        self._button.setEnabled(True)
        self._button.setFlat(False)
        self._button.setStyleSheet(self._default_style_sheet)

    def disable(self) -> None:
        self._button.setEnabled(False)
        self._button.setFlat(True)

    def paint_cell(self) -> None:
        color = "#2481BA" if self.symbol == "o" else "#1CB34B"
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

    @property
    def cells(self) -> List[List[Cell]]:
        return self._cells

    @property
    def rows_and_columns(self) -> int:
        return self._rows_and_columns

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
