from node import Node  # Assuming your Node class is defined in a file named 'node.py'
from network_utils import IPv4
from typing import List, Dict

class CommandParser:
    def __init__(self):
        self.node = Node()
        self.commands = {
            "-ip": self.handle_ip_command,
            "--ip_addr": self.handle_ip_command,
            "-p": self.handle_port_command,
            "--port": self.handle_port_command,
            "-is": self.handle_input_size_command,
            "--input_size": self.handle_input_size_command,
            "-os": self.handle_output_size_command,
            "--output_size": self.handle_output_size_command,
            "-fc": self.handle_frame_corruption_command,
            "-fic": self.handle_file_corruption_command,
            "--file_corruptness": self.handle_file_corruption_command,
            "-s": self.handle_start_server_command,
            "--start_node": self.handle_start_server_command,
            "-c": self.handle_comm_command,
            "--comm": self.handle_comm_command,
            "-cc": self.handle_close_comm_command,
            "--close_comm": self.handle_close_comm_command,
            "-fcc": self.handle_force_close_comm_command,
            "--force_close_comm": self.handle_force_close_comm_command,
            "-m": self.handle_message_command,
            '--message': self.handle_message_command,
            "-f": self.handle_file_command,
            "--file": self.handle_file_command,
            "-sw": self.handle_swap_command,
            "--swap": self.handle_swap_command,
            "-q": self.handle_quit_server_command,
            "--quit_node": self.handle_quit_server_command,
            "-t": self.handle_terminate_command,
            "--terminate": self.handle_terminate_command,
            "-h": self.handle_help_command,
            "--help": self.handle_help_command
        }

    def handle_ip_command(self, args):
        if len(args) == 1:
            print(self.node.get_ip())
        elif len(args) == 2:
            self.node.set_ip(args[1])
        else:
            print("Invalid command structure. See help for more information.")

    def handle_port_command(self, args):
        if len(args) == 1:
            print(self.node.get_port())
        elif len(args) == 2:
            self.node.set_port(port=int(args[1]))
        else:
            print("Invalid command structure. See help for more information.")

    def handle_input_size_command(self, args):
        if len(args) == 1:
            print(self.node.get_input_size())
        elif len(args) == 2:
            self.node.set_input_size(int(args[1]))
        else:
            print("Invalid command structure. See help for more information.")

    def handle_output_size_command(self, args):
        if len(args) == 1:
            print(self.node.get_output_size())
        else:
            print("Invalid command structure. See help for more information.")

    def handle_frame_corruption_command(self, args):
        if len(args) == 1:
            print(self.node.get_frame_corruption())
        elif len(args) == 2:
            self.node.set_frame_corruption(float(args[1]))
        else:
            print("Invalid command structure. See help for more information.")

    def handle_file_corruption_command(self, args):
        if len(args) == 1:
            print(self.node.get_file_corruption())
        elif len(args) == 2:
            self.node.set_file_corruption(float(args[1]))
        else:
            print("Invalid command structure. See help for more information.")

    def handle_start_server_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.start()

    def handle_comm_command(self, args: List[str]):
        if len(args) > 1:
            args.extend(args[1].split(' '))
            args.remove(args[1])

        if len(args) != 3:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.start_comm(args[1], int(args[2]), requested=True)

    def handle_close_comm_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.finish_comm(requested=True)

    def handle_force_close_comm_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.force_finish_comm()

    def handle_message_command(self, args):
        if len(args) < 2:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.send_message(message=args[1])

    def handle_file_command(self, args):
        if len(args) < 2:
            print("Invalid command structure. See help for more information.")
            return

        args.extend(args[1].split(' '))
        args.remove(args[1])

        if len(args) == 2:
            self.node.send_file(f_path=args[1])
        elif len(args) == 3:
            self.node.send_file(f_path=args[1], name=args[2])

    def handle_swap_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.swap_roles()

    def handle_quit_server_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        else:
            self.node.quit()

    def handle_terminate_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        elif self.node.is_running():
            print("Server still running! Quit it first to terminate the program.")
        else:
            exit()

    def handle_help_command(self, args):
        if len(args) != 1:
            print("Invalid command structure. See help for more information.")
        else:
            print("""Supported Commands List

Node Configuration
                  
    --ip_addr <VALUE>:          If value parameter is not present, the current will be printed, otherwise reset.
    -ip <VALUE>                 Shortcut for --ip_addr.
    --port <VALUE>:             If value parameter is not present, the current will be printed, otherwise reset.
    -p <VALUE>                  Shortcut for --port.
    --input_size:               If value parameter is not present, the current will be printed, otherwise reset.
    -is <VALUE>                 Shortcut for --input_size.
    --output_size:              If value parameter is not present, the current will be printed, otherwise reset.
    -os <VALUE>                 Shortcut for --output_size.
    --frame_corruption:         If value parameter is not present, the current will be printed, otherwise reset.
    -fc                         Shortcut for --frame_corruption.
    --file_corruption:          If value parameter is not present, the current will be printed, otherwise reset.
    -fic                        Shortcut for --file_corruption.

Node Manipulation
                                                
    --start_node:               Starts the node and all subprocesses.
    -s                          Shortcut for --start_node.
    --quit_node:                Quits the node and all subprocesses.
    -q                          Shortcut for --quit_node.

Communication
                                    
    --comm <IP> <PORT>:         Starts a communication with a node with the specified parameters.
    -c <IP> <PORT>              Shortcut for --comm.             
    --close_comm:               Closes the started communication with the other node.
    -cc                         Shortcut for --close_comm.
    --force_close_comm:         Forces the communication to close, can only be executed during serious scenarios.
    --message <VALUE>:          Sends a message to the other node.
    -m <VALUE>                  Shortcut for --message.
    --file <PATH> <NAME>:       Sends a file with the specified path to the other site. User can also provide
                                their custom name for the file at the received end, otherwise the current one will be used.
    -f <PATH> <NAME>            Shortcut for --file.    
    --swap:                     Swap roles between client and server.
    -sw                         Shortcut for --swap.

General
                  
    --terminate:                Terminates the program only if the server is not running.
    -t                          Shortcut for --terminate.
    --help:                     Prints help.
    -h                          Shortcut for --help.""")
            
    def parse_command(self, command):
        args = command.split(' ', 1)
        if args[0] in self.commands:
            self.commands[args[0]](args)
        else:
            print("Unknown command. Use \"--help\" for more information.")


def main():
    command_parser = CommandParser()

    while True:
        print("")
        user_input = input("Enter command: ")
        print("")

        if user_input.lower() == "--terminate":
            break

        command_parser.parse_command(user_input)

    print("Program terminated successfully!")

if __name__ == "__main__":
    main()