from dataclasses import dataclass

from backend.app.models import User


CHECKIN_EXP_REWARD = 40
CHECKIN_GOLD_REWARD = 8


@dataclass(frozen=True)
class RewardResult:
    exp_earned: int
    gold_earned: int
    leveled_up: bool


def apply_checkin_reward(user: User) -> RewardResult:
    previous_level = user.level
    user.exp += CHECKIN_EXP_REWARD
    user.gold += CHECKIN_GOLD_REWARD
    while user.exp >= user.level * 200:
        user.level += 1
    return RewardResult(
        exp_earned=CHECKIN_EXP_REWARD,
        gold_earned=CHECKIN_GOLD_REWARD,
        leveled_up=user.level > previous_level,
    )
