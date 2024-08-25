# LoginSmasher
Developers:

Dy5m: Mastermind and Project Contributor
hmodez: Lead Developer


Description
LoginBuster is a Python-based brute-force login tool designed to test the security of login systems. It efficiently performs brute-force attacks using multi-processing and multi-threading to maximize performance. The tool is highly configurable, allowing users to specify multiple usernames and passwords, and provides detailed logging of its activities.

Features
Multi-threading and Multi-processing: Utilizes threading and multiprocessing to optimize attack speed and performance.
Configurable Parameters: Customize login URL, usernames, password file, chunk size, number of threads, number of processes, and delay between attempts.
Logging: Real-time logging of attempts, successful logins, and errors.
Output: Successful passwords are written to a specified output file.

To install the required libraries, use the command:

bash
Copy code
pip install -r requirements.txt
Configuration
The script is configured using default settings but allows for user input to customize:

LoginUrl: URL of the login page to test.
Username: The username(s) to test (comma-separated for multiple).
PasswordFile: Path to the file containing passwords for the brute-force attack.
ChunkSize: Number of passwords to process per chunk.
NumThreads: Number of threads for parallel processing within each process.
NumProcesses: Number of processes for multiprocessing.
Delay: Delay between login attempts to avoid overwhelming the server.
OutputFile: File to store successful passwords.
Usage
Run the script using the command:

bash
Copy code
python loginbuster.py
Follow the prompts to enter:

Username(s): Enter one or more usernames, separated by commas.
Password File: Provide the path to the file containing passwords.
Example
bash
Copy code
python loginbuster.py

#Notes
Permission: Ensure you have explicit permission to test the login system to avoid legal issues.
Customization: Adjust the success criteria in the attempt_login function based on the specific login page being tested.
