import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scoring_service import ScoringService


def test_base_score_correct():
    score = ScoringService.calculate_score(is_correct=True, streak=0)
    assert score == ScoringService.BASE_POINTS


def test_base_score_incorrect():
    score = ScoringService.calculate_score(is_correct=False, streak=5)
    assert score == 0


def test_streak_bonus_3():
    score = ScoringService.calculate_score(is_correct=True, streak=3)
    expected = ScoringService.BASE_POINTS + ScoringService.STREAK_BONUSES[3]
    assert score == expected


def test_streak_bonus_5():
    score = ScoringService.calculate_score(is_correct=True, streak=5)
    expected = ScoringService.BASE_POINTS + ScoringService.STREAK_BONUSES[3] + ScoringService.STREAK_BONUSES[5]
    assert score == expected


def test_streak_bonus_10():
    score = ScoringService.calculate_score(is_correct=True, streak=10)
    expected = ScoringService.BASE_POINTS + ScoringService.STREAK_BONUSES[3] + ScoringService.STREAK_BONUSES[5] + ScoringService.STREAK_BONUSES[10]
    assert score == expected


def test_streak_bonus_cumulative():
    score_15 = ScoringService.calculate_score(is_correct=True, streak=15)
    score_10 = ScoringService.calculate_score(is_correct=True, streak=10)
    assert score_15 == score_10  # Same bonus for streak >= 10


def test_get_streak_bonus():
    bonus = ScoringService.get_streak_bonus(7)
    expected = ScoringService.STREAK_BONUSES[3] + ScoringService.STREAK_BONUSES[5]
    assert bonus == expected


def test_get_streak_bonus_zero():
    bonus = ScoringService.get_streak_bonus(0)
    assert bonus == 0


def test_get_streak_bonus_below_threshold():
    bonus = ScoringService.get_streak_bonus(2)
    assert bonus == 0
