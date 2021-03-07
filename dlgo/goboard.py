import copy


class GoString:
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)  # 돌과 활로는 불변의 frozenset 인스턴스

    def without_liberty(self, point):  # without_liberty() 매서드는 기존의 remove_liberty() 매서드 대체
        new_liberties = self.liberties - set([point])
        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):  # with_liberty()매서드는 add_liberty() 매서드를 대체
        new_liberties = self.liberties | set([point])
        return GoString(self.color, self.stones, new_liberties)


from dlgo import zobrist


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)  # <1>

        for same_color_string in adjacent_same_color:  # <2>
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        self._hash ^= zobrist.HASH_CODE[point, player]  # <3>

        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.without_liberty(point)  # <4>
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                self._remove_string(other_color_string)  # <5>

    # <1> Until this line `place_stone` remains the same.
    # <2> You merge any adjacent strings of the same color.
    # <3> Next, you apply the hash code for this point and player
    # <4> Then you reduce liberties of any adjacent strings of the opposite color.
    # <5> If any opposite color strings now have zero liberties, remove them.
    # end::apply_zobrist[]

    def _replace_string(self, new_string):
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None

            self._hash ^= zobrist.HASH_CODE[point, string.color]

    def zobrist_hash(self):
        return self._hash


class GameState:
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())})
        self.last_move = move

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states


def find_winning_move(game_state, next_player):
    for candidate_move in game_state.legal_moves(next_player):  # 모든 가능한 수에 대해 반복
        next_state = game_state.apply_move(candidate_move)  # 이 수를 선택한 경우 어떤 일이 일어날지 계산
        if next_state.is_over() and next_state.winner == next_player:
            return candidate_move  # 이수를 두면 이긴다!
    return None


def eliminate_losing_moves(game_state, next_player):
    opponent = next_player.other()
    possible_moves = []  # 고려 대상인 모든 수가 들어갈 리스트
    for candidate_move in game_state.legal_moves(next_player):  # 모든 가능한 수에 대해 반복
        next_state = game_state.apply_move(candidate_move)  # 이 수를 둘 경우 어떤 일이 일어날지 계산
        opponent_winning_move = find_winning_move(next_state, opponent)  # 이를 두면 상대가 필승점에 두게 될까? 아니라면 이 수는 괜찮다.
        if opponent_winning_move is None:
            possible_moves.append(candidate_move)
    return possible_moves


def find_two_step_win(game_state, next_player):
    opponent = next_player.other()
    for candidate_move in game_state.legal_moves(next_player):  # 모든 가능한 수에 대해 반복한다.
        next_state = game_state.apply_move(candidate_move)  # 이 수를 두었을때 전체 게임이 어떻게 될자 계산
        good_responses = eliminate_losing_moves(next_state, opponent)  # 상대방이 방어를 잘했는가? 아니라면 이 수를 두자.
        if not good_responses:
            return candidate_move
    return None
