from backend.app.models import User


CHECKIN_EXP_REWARD = 40
CHECKIN_GOLD_REWARD = 8


def apply_checkin_reward(user: User) -> bool:
    user.exp += CHECKIN_EXP_REWARD
    user.gold += CHECKIN_GOLD_REWARD

    threshold = user.level * 200
    leveled_up = user.exp >= threshold
    if leveled_up:
        user.level += 1

    return leveled_up
