"""Command Line Interface for yabp"""
import sys
import click


@click.group(
    invoke_without_command=True, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.pass_context
@click.version_option()
def main(ctx):
    """CLI for yabp"""
    click.echo("yabp")

@cli.command()
def sub_command_one():
    """Example Sub Command"""
    click.echo("yabp sub_command_one")

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
