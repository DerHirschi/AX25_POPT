from cfg.constant import CLI_TYP_PIPE
from cli.cli_frontends.cliNONE import NoneCLI
from cli.cli_frontends.cliNODE import NodeCLI
from cli.cli_frontends.cliSYSOP import UserCLI
from cli.cli_frontends.cliMCAST import MCastCLI
from cli.cli_frontends.cliBOX import BoxCLI

CLI_OPT = {
    UserCLI.cli_name: UserCLI,
    NodeCLI.cli_name: NodeCLI,
    NoneCLI.cli_name: NoneCLI,
    CLI_TYP_PIPE: NoneCLI,
    MCastCLI.cli_name: MCastCLI,
    BoxCLI.cli_name: BoxCLI,
}
