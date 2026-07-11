from scripts.final_verify import verification_commands


def test_final_verification_covers_every_delivery_surface():
    commands = [" ".join(command) for command in verification_commands(include_live=True)]

    assert any("ruff check backend tests scripts" in command for command in commands)
    assert any("pytest -q" in command for command in commands)
    assert any("scripts/verify_openapi.py" in command for command in commands)
    assert any("npm --prefix frontend test -- --run" in command for command in commands)
    assert any("npm --prefix frontend run build" in command for command in commands)
    assert any("scripts/smoke_test.py" in command and "--read-only" in command for command in commands)


def test_offline_verification_omits_only_the_live_probe():
    commands = [" ".join(command) for command in verification_commands(include_live=False)]

    assert not any("scripts/smoke_test.py" in command for command in commands)
    assert len(commands) == 5
