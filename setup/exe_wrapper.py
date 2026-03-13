import os
import sys
import threading
import subprocess 
import asyncio
import time
import edge_tts
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from better_profanity import profanity
import re

###########################################################################################################################

# Change this path if you have a different installation location
# escaped backslashes are crucial !!
MEDIA_FOLDER_PATH = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Titanfall2\\R2Northstar\\mods\\chatts\\mod\\media'
HAS_LAUNCHED = False
SERVER = None

def delete_file(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)

def make_filepath(input: str, position: int):
    if input:
        return MEDIA_FOLDER_PATH + f'\\bik_input_pos_{position}.mp3'
    else:
        return MEDIA_FOLDER_PATH + f'\\bik_output_pos_{position}.bik'

def get_radvideo():
    # Check if valid executable is present in current directory
    for filename in ['radvideo32.exe', 'radvideo64.exe']:
        filename = MEDIA_FOLDER_PATH + '\\' + filename 
        if os.path.exists(filename):
            return filename
    return None

async def convert_to_bik(input: str, position: int):
    # Get executable filename (if present)
    radvideo = get_radvideo()
    if not radvideo:
        return False
    
    output = make_filepath(False, position)

    # Dont show external window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Run the conversion command in the background
    process = subprocess.Popen(
        [radvideo, 'Bink', '/O', input, output],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    timeout = 4.0
    start_time = time.time()

    # Get latest time of change of the output file
    old_mtime = os.path.getmtime(output) if os.path.exists(output) else 0
    
    while True:
        # If the conversion takes longer than the set timeout (4.0s), kill the process prematurely
        if (time.time() - start_time) > timeout:
            process.kill()
            return False
        
        await asyncio.sleep(0.1)
        
        if os.path.exists(output):
            new_mtime = os.path.getmtime(output)
            new_size = os.path.getsize(output)
            
            # Exit if the file hasnt been changed in 0.1s and has thus finished converting
            if new_mtime > old_mtime and new_size > 0:
                await asyncio.sleep(0.1)
                stable_size = os.path.getsize(output)
                if stable_size == new_size:
                    break
    
    # End the process if it is still running
    if process.poll() is None:
        process.terminate()

    return True

def create_beep(length: int):
    # Return a beep of according length
    # Fuck -> Beep
    # Faggot -> Beeeep
    if length <= 2:
        return 'beep'
    return 'b' + ('e' * (length - 2)) + 'p'

def beep(text: str):
    def replace_word(match):
        word = match.group()
        if profanity.contains_profanity(word):
            return create_beep(len(word))
        return word
    
    # Regex search and replacement
    pattern = r'\b\w+\b'
    result = re.sub(pattern, replace_word, text, flags=re.IGNORECASE)
    return result

async def generate_tts(text: str, voice: str, censor: bool, position: int):
    # Optionally replace profanity with beeps
    if censor:
        text = beep(text)

    # Get TTS
    try:
        communicate = edge_tts.Communicate(text, voice)
    except ValueError:
        print('Not a valid voice')
        return False
    
    path = make_filepath(True, position)

    # Save previously generated TTS to file
    try:
        await communicate.save(path)
    except edge_tts.exceptions.NoAudioReceived:
        print('No audio received!')
        return False

    # Convert saved .mp3 file to .bik file to be useable ingame 
    success = await convert_to_bik(path, position)

    # Delete previously created temporary .mp3 file
    try:
        delete_file(path)
    except FileNotFoundError:
        print('Could not delete temp .mp3 file')

    return True if success else False

###########################################################################################################################

class Server(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_POST(self):
        path = urlparse(self.path).path

        match path:
            case '/makeTTS':
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)

                # Parse query
                try:
                    message = params['message'][0]
                    voice = params['voice'][0]
                    position = int(params['position'][0])
                    should_censor = (params['censor'][0] == 'true')
                except:
                    print('Error while converting query types')
                    self.send_response(400)
                    self.end_headers()
                    return 
                
                # Create TTS file with parsed query as parameters
                success = asyncio.run(generate_tts(message, voice, should_censor, position))

                if success:
                    print('Successfully created TTS')
                    self.send_response(200)
                else:
                    print('Failed to create TTS')
                    self.send_response(400)
                
                self.end_headers()
                return
            
            case _:
                print('Not a valid path: ' + path)
                self.send_response(404)
                self.end_headers()
                return

###########################################################################################################################

def is_game_open():
    try:
        return 'Titanfall2_real.exe' in subprocess.check_output(args='tasklist', creationflags=subprocess.CREATE_NO_WINDOW).decode('UTF-8')
    except subprocess.CalledProcessError:
        print('subprocess.CalledProcessError')
        return True

def launch_game():
    # Dont start again if the game is already loaded up
    global HAS_LAUNCHED
    if HAS_LAUNCHED:
        if is_game_open():
            print('Titanfall is already running!')
            return False

    # Start the game with the steam launch args included
    try:
        args = sys.argv[1:]
        subprocess.Popen(
            [os.path.join(os.getcwd(), 'Titanfall2_real.exe'), *args],
            shell=False
        )
        return True
    except:
        print('Could not launch game!! Is this file in the correct directory? Did you rename the original .exe?')
        return False

def start_listener():
    print('Listening on http://127.0.0.1:2222')

    # Start listener server and keep alive in the background on port 2222
    global SERVER 
    SERVER = HTTPServer(('127.0.0.1', 2222), Server)
    SERVER.serve_forever()

    print('Listener closed')

def close_server_monitor():
    # Close listener server and end script if theres no 'Titanfall2.exe' process to be found in the tasklist
    # Poll every 5 seconds
    while True:
        time.sleep(5)
        if not is_game_open():
            print('Titanfall2.exe is not opened, closing server')
            try:
                global SERVER
                SERVER.shutdown()
            except:
                pass
            break

###########################################################################################################################

def main():
    if launch_game():
        global HAS_LAUNCHED
        HAS_LAUNCHED = True
        
        # Monitor in background
        threading.Thread(target=close_server_monitor).start()

        # Start listener server (blocking)
        start_listener()
        print('Main finished')
    
if __name__ == '__main__':
    main()