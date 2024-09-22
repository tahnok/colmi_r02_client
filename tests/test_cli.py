from unittest.mock import patch, Mock

from asyncclick.testing import CliRunner

from colmi_r02_client.cli import cli_client


async def test_no_address_and_no_name():
    runner = CliRunner()
    result = await runner.invoke(cli_client, ["info"])
    assert result.exit_code == 2
    assert "Error: You must pass either the address option(preferred) or the name option, but not both" in result.output


async def test_address_and_name():
    runner = CliRunner()
    result = await runner.invoke(
        cli_client,
        [
            "--name=foo",
            "--address=bar",
            "info",
        ],
    )
    assert result.exit_code == 2
    assert "Error: You must pass either the address option(preferred) or the name option, but not both" in result.output


@patch("colmi_r02_client.cli.Client", autospec=True)
async def test_just_address(_client_mock):
    runner = CliRunner()
    result = await runner.invoke(
        cli_client,
        [
            "--address=bar",
            "info",
        ],
    )
    assert result.exit_code == 0


@patch("colmi_r02_client.cli.Client", autospec=True)
@patch("colmi_r02_client.cli.BleakScanner.discover", autospec=True)
async def test_just_name(discover_mock, _client_mock):
    found = Mock()
    found.name = "bar"
    found.address = "foo"
    discover_mock.return_value = [found]

    runner = CliRunner()
    result = await runner.invoke(
        cli_client,
        [
            "--name=bar",
            "info",
        ],
    )
    assert result.exit_code == 0


@patch("colmi_r02_client.cli.Client", autospec=True)
@patch("colmi_r02_client.cli.BleakScanner.discover", autospec=True)
async def test_just_name_not_found(discover_mock, _client_mock):
    found = Mock()
    found.name = "nonono"
    found.address = "foo"
    discover_mock.return_value = [found]

    runner = CliRunner()
    result = await runner.invoke(
        cli_client,
        [
            "--name=bar",
            "info",
        ],
    )
    assert result.exit_code == 2
    assert "Error: No device found with given name" in result.output
