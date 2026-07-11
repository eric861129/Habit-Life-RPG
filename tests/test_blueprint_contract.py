from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_prd_defines_the_complete_book_mvp_and_reward_rules():
    text = read("docs/PRD.md")

    for term in ("註冊", "登入", "習慣 CRUD", "每日打卡", "連續天數", "金幣", "經驗值", "等級"):
        assert term in text
    assert "+40 EXP" in text
    assert "+8 gold" in text
    assert "level × 200" in text


def test_user_stories_have_stable_acceptance_identifiers():
    text = read("docs/user-stories.md")

    for prefix in ("AUTH-", "HABIT-", "CHECKIN-", "DASHBOARD-"):
        assert prefix in text
    assert text.count("Given") >= 8
    assert text.count("When") >= 8
    assert text.count("Then") >= 8


def test_ux_flow_covers_success_and_recovery_paths():
    text = read("docs/ux-flow.md").lower()

    for term in ("register", "login", "duplicate", "401", "empty", "loading", "error"):
        assert term in text
    assert "```mermaid" in text


def test_ui_spec_defines_responsive_and_accessible_states():
    text = read("docs/ui-spec.md").lower()

    for term in ("mobile", "desktop", "loading", "empty", "error", "keyboard", "focus"):
        assert term in text
    assert "390" in text
    assert "1440" in text


def test_blueprint_explicitly_excludes_large_game_systems():
    text = read("docs/PRD.md")

    for term in ("Boss", "商店", "社交", "大型任務"):
        assert term in text
    assert "不在本書 MVP" in text


def test_chapter_guide_points_to_the_cumulative_branch():
    text = read("docs/chapter-guides/ch03-blueprint.md")

    assert "chapter/03-blueprint" in text
    assert "chapter/02-toolbox" in text
    assert "累進" in text
