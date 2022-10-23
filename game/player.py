from game.playing_field import PlayingField


class Player:
    """
    Base class for player.
    """

    def __init__(self, player_id: int) -> None:
        self._player_id: int = player_id
        self._symbol: str = "o" if player_id == 0 else "x"

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def value(self) -> int:
        if self._symbol == "o":
            return 1
        if self._symbol == "x":
            return -1
        return 0


class ComputerPlayer(Player):
    """
    Class for computer player.
    """

    def __init__(self, player_id: int) -> None:
        super().__init__(player_id)

    def make_move(self, playing_field: PlayingField) -> None:
        """
        Method makes move for computer.
        :param playing_field: playing field.
        """

        any_empty_cell = None
        for row in range(playing_field.rows_and_columns):
            column_sum = 0
            empty_cell = None
            for column in range(playing_field.rows_and_columns):
                cell = playing_field.cells[row][column]
                column_sum += cell.value
                if cell.value == 0:
                    empty_cell = cell
                    if any_empty_cell is None:
                        any_empty_cell = cell
            if column_sum == 2 * self.value and empty_cell:
                empty_cell.button.click()
                return

        for column in range(playing_field.rows_and_columns):
            row_sum = 0
            empty_cell = None
            for row in range(playing_field.rows_and_columns):
                cell = playing_field.cells[row][column]
                row_sum += cell.value
                if cell.value == 0:
                    empty_cell = cell
                    if any_empty_cell is None:
                        any_empty_cell = cell
            if row_sum == 2 * self.value and empty_cell:
                empty_cell.button.click()
                return

        if any_empty_cell:
            any_empty_cell.button.click()
