from ..Interfaces.bookmarks import *
import pytest

@pytest.mark.parametrize('expected_result',
                         [3])
def test_update_players(expected_result):
    assert update_players() == expected_result

@pytest.mark.parametrize('players_idx, expected_result',
                         [([1], (True, 3)),
                          ([5], (False, 5)),
                          ([2], (True, 3)),
                          ([-1], (False, -1)),
                          (['1'], (False, '1')),
                          ([1, 2, 3], (True, 1)),
                          ([1, 5, 3], (False, 5)),
                          (['a', 1], (False, 'a'))])
def test_delete_from_bookmarks(players_idx, expected_result):
    assert delete_from_bookmarks(players_idx) == expected_result
    
@pytest.mark.parametrize('player_idx, expected_result',
                         [(1, (True, None)),
                          (5, (False, 5)),
                          (-1, (False, -1)),
                          ('1', (False, '1')),
                          (2, (True, 'link to phone and email'))])
def test_request_info(player_idx, expected_result):
    assert request_info(player_idx) == expected_result