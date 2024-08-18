from colmi_r02_client.main import CliConfig

def test_cli_config_all_defaults():
    """click.Context.ensure_object will instantiate this class with 0 arguments"""
    assert CliConfig()
