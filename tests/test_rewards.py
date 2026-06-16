from backend.app.models import User
from backend.app.services.rewards import (
    CHECKIN_EXP_REWARD,
    CHECKIN_GOLD_REWARD,
    apply_checkin_reward,
)


def test_checkin_reward_adds_fixed_exp_and_gold() -> None:
    user = make_user(level=2, exp=120, gold=35)

    leveled_up = apply_checkin_reward(user)

    assert leveled_up is False
    assert user.exp == 120 + CHECKIN_EXP_REWARD
    assert user.gold == 35 + CHECKIN_GOLD_REWARD
    assert user.level == 2


def test_checkin_reward_levels_up_at_level_threshold() -> None:
    user = make_user(level=1, exp=160, gold=10)

    leveled_up = apply_checkin_reward(user)

    assert leveled_up is True
    assert user.level == 2
    assert user.exp == 200
    assert user.gold == 18


def test_checkin_reward_keeps_exp_cumulative_after_level_gain() -> None:
    user = make_user(level=2, exp=380, gold=0)

    leveled_up = apply_checkin_reward(user)

    assert leveled_up is True
    assert user.level == 3
    assert user.exp == 420
    assert user.exp != 0


def make_user(*, level: int, exp: int, gold: int) -> User:
    return User(
        id=1,
        username="arthur",
        password_hash="test-password-hash",
        level=level,
        exp=exp,
        gold=gold,
        hp=86,
    )
