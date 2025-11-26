from cfg.constant import CLI_TYP_PIPE
from cli.cliMain import NoneCLI
from cli.cliNODE import NodeCLI
from cli.cliSYSOP import UserCLI
from cli.cliMCAST import MCastCLI
from cli.cliBOX import BoxCLI

CLI_OPT = {
    UserCLI.cli_name: UserCLI,
    NodeCLI.cli_name: NodeCLI,
    NoneCLI.cli_name: NoneCLI,
    CLI_TYP_PIPE: NoneCLI,
    MCastCLI.cli_name: MCastCLI,
    BoxCLI.cli_name: BoxCLI,
}
