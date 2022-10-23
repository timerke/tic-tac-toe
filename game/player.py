

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


class ComputerPlayer(Player):
    """
    Class for computer player.
    """

    def __init__(self, player_id: int) -> None:
        super().__init__(player_id)
