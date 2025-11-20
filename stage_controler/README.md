# Contents of the stage controler software library

- \_\_init\_\_.py turns the directory into a library
- Serial_handler.py a class to send and recieve JSON packages over the serial bus
- Stage_controler.py a class to generate JSON command packages which are then handed off to a serial handler for execution
- Contains tests for the functionality of the serial handler and stage controler
