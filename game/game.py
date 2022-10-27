from typing import List
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QPushButton
from game.player import ComputerPlayer, Player
from game.playing_field import Cell, PlayingField


class Game(QObject):
    """
    Class is responsible for game.
    """

    ROWS_AND_COLUMNS: int = 3
    game_over: pyqtSignal = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self._game_in_progress: bool = False
        self._players: List[Player] = []
        self._playing_field: PlayingField = PlayingField(self.ROWS_AND_COLUMNS)
        self._turn: int = 0

    @property
    def game_in_progress(self) -> bool:
        """
        :return: True if game is in progress.
        """

        return self._game_in_progress

    def _end_game(self, cells: List[Cell]) -> None:
        """
        Method ends game.
        :param cells: list of cells that are lined up.
        """

        self._game_in_progress = False
        if cells:
            for cell in cells:
                cell.paint_cell()
        self._playing_field.end_game()

    def _make_move_for_computer(self) -> None:
        if isinstance(self._players[self._turn], ComputerPlayer):
            self._players[self._turn].make_move(self._playing_field)

    @pyqtSlot(Cell)
    def make_move(self, cell: Cell) -> None:
        """
        Slot handles move in game.
        :param cell: cell clicked on.
        """

        if not cell.symbol:
            cell.change_symbol(self._players[self._turn].symbol)
            to_finish, cells = self._playing_field.check()
            if to_finish:
                self._end_game(cells)
                self.game_over.emit(self._turn if cells else -1)
            self._turn = (self._turn + 1) % 2
            self._make_move_for_computer()

    def resize(self) -> None:
        self._playing_field.resize()

    def set_buttons(self, buttons: List[List[QPushButton]]) -> None:
        self._playing_field.set_buttons_to_cells(buttons, self.make_move)

    def start_game(self, player_1: Player, player_2: Player) -> None:
        """
        Method starts new game.
        :param player_1: first player;
        :param player_2: second player.
        """

        self._game_in_progress = True
        self._players = [player_1, player_2]
        self._playing_field.clear()
        self._turn = 0
        self._make_move_for_computer()
