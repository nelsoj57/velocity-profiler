def main():
    """
    Entry point for controller process.
    - Initializes AO and wavemeter interfaces
    - Starts a network server to receive commands
    - Handles incoming voltage step commands by:
        → Ramping to voltage
        → Reading and averaging frequency
        → Sending back results
    """

    """
    with ControllerServer(...) as server:
        while True:
            try:
                cmd = server.receive_command()
                result = handle_step(cmd)
                server.send_response(result)
            except Exception as e:
                log_error(e)
                server.send_response({"valid": False, "error": str(e)})
    """
    pass
    # 1. Initialize TCP server
    # 1a. Start Listening for connections (Do I need a seperate thread for this?)
    # 1b. If command is recieved before AO and WLM are initialized, ACK and queue it?
    # 1c. Or just no one sends a command until client says they are ready, server ACKs it, Server tells client it is ready, client ACKs it and only THEN client sends commands
    # 2. Initialize AO interface
    # 3. Initialize wavemeter interface

    # ^ 1,2,& 3 can happen in any order, or even in parallel
    # 4. Initialize a queue for commands?
    # 5. Initialize the data structure to hold the results
    # 6. Make sure Client is Connected (if that wasn't already required in step 1)
    # 7. Send Server Ready message to client
    # 8. Wait for ACK from client
    # 9. Start listening for commands (possibly in a loop?)
    # - The first command should be metadata about what kind of interaction/sweep the client wants, and maybe what type of formatting I should expect (if there are multiple options)
    # 10. Handle commands in a loop:
    # - When given a command:
    #  - Check that its valid
    # - If valid, ACK it
    # - If command is to move to a certain voltage/index: move to that voltage/index
    # - Then give the client a message saying that the command was successful and to start recording at a certain time in the future if applicable
    # - If don't recieve an ACK before that time, resent the ready message? or just wait for the next command?
    # - in your ACK? send back the time to start recording at (Maybe this should be done after the ACK?)
    # Last. Upon receiving a done command, send a final message to the client
    # Lastest. If the client requests a shutdown, gracefully shutdown the server and close all connections
    # - If the client loses the connection, gracefully shutdown the server and close all connections
