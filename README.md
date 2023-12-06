# Project Chariot - Parser

## Overview
Project Chariot is a collection of tools designed to enhance API interaction. The Parser module is specifically designed to retrieve information from multiple APIs by processing a list of IP addresses.

## Features
- Connects to APIs using IP addresses from a text file.
- Sends a "summary" command to each API.
- Handles connection errors and continues processing other IPs.

## Getting Started
### Prerequisites

.. code-block::

    $  pip install -r requirements.txt
    
##Usage
Clone the repository:
.. code-block::

    $   git clone https://github.com/your-username/Project-Chariot-Parser.git
    $   cd Project-Chariot-Parser

Run the script with a text file containing a list of IP addresses:
.. code-block::

    $  python parser.py filename.txt


##Configuration
Edit the filename.txt file to include the list of IP addresses you want to process.

##Contributing
Feel free to contribute by opening issues, suggesting enhancements, or submitting pull requests.

##License
This project is licensed under the MIT License.
