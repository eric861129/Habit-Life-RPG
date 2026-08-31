from scripts.final_verify import verification_commands


def test_final_verification_covers_every_delivery_surface():
    raw_commands = verification_commands(include_live=True)
    commands = [" ".join(command) for command in raw_commands]

    assert any("ruff check backend tests scripts" in command for command in commands)
    assert any("pytest -q" in command for command in commands)
    assert any("scripts/verify_openapi.py" in command for command in commands)
    assert any(
        command[0] in {"npm", "npm.cmd"}
        and command[1:] == ["--prefix", "frontend", "test", "--", "--run"]
        for command in raw_commands
    )
    assert any(
        command[0] in {"npm", "npm.cmd"}
        and command[1:] == ["--prefix", "frontend", "run", "build"]
        for command in raw_commands
    )
    assert any("scripts/smoke_test.py" in command and "--read-only" in command for command in commands)


def test_offline_verification_omits_only_the_live_probe():
    commands = [" ".join(command) for command in verification_commands(include_live=False)]

    assert not any("scripts/smoke_test.py" in command for command in commands)
    assert len(commands) == 5


def test_windows_verification_uses_the_executable_npm_command_shim():
    commands = verification_commands(include_live=False, platform="win32")

    assert commands[3][0] == "npm.cmd"
    assert commands[4][0] == "npm.cmd"
