import os
import sys
import threading
import subprocess 
import asyncio
import time
import edge_tts
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

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
    for filename in ['radvideo32.exe', 'radvideo64.exe']:
        filename = MEDIA_FOLDER_PATH + '\\' + filename 
        if os.path.exists(filename):
            return filename
    return None

async def convert_to_bik(input: str, position: int):
    radvideo = get_radvideo()
    if not radvideo:
        return False
    
    output = make_filepath(False, position)

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    process = subprocess.Popen(
        [radvideo, 'Bink', '/O', input, output],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    timeout = 4.0
    start_time = time.time()

    old_mtime = os.path.getmtime(output) if os.path.exists(output) else 0
    
    while True:
        if (time.time() - start_time) > timeout:
            process.kill()
            return False
        
        await asyncio.sleep(0.1)
        
        if os.path.exists(output):
            new_mtime = os.path.getmtime(output)
            new_size = os.path.getsize(output)
            
            if new_mtime > old_mtime and new_size > 0:
                await asyncio.sleep(0.1)
                stable_size = os.path.getsize(output)
                if stable_size == new_size:
                    break
    
    if process.poll() is None:
        process.terminate()

    return True

async def generate_tts(text: str, voice: str, position: int):
    try:
        communicate = edge_tts.Communicate(text, voice)
    except ValueError:
        print('Not a valid voice')
        return False
    
    path = make_filepath(True, position)

    try:
        await communicate.save(path)
    except edge_tts.exceptions.NoAudioReceived:
        print('No audio received!')
        return False

    success = await convert_to_bik(path, position)

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

                # print(params)
                # print(type(params['message'][0]))
                # print(type(params['voice'][0]))
                # print(type(int(params['position'][0])))

                try:
                    message = params['message'][0]
                    voice = params['voice'][0]
                    position = int(params['position'][0])
                except:
                    print('Error while converting query types')
                    self.send_response(400)
                    self.end_headers()
                    return 
                
                success = asyncio.run(generate_tts(message, voice, position))

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
        return 'Titanfall2.exe' in subprocess.check_output('tasklist').decode('UTF-8')
    except subprocess.CalledProcessError:
        print('subprocess.CalledProcessError')
        return True

def launch_game():
    global HAS_LAUNCHED
    if HAS_LAUNCHED:
        if is_game_open():
            print('Titanfall is already running!')
            return False

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

# http://127.0.0.1:2222
def start_listener():
    print('Listening on http://127.0.0.1:2222')

    global SERVER 
    SERVER = HTTPServer(('127.0.0.1', 2222), Server)
    SERVER.serve_forever()

    print('Listener closed')

def close_server_monitor():
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

        threading.Thread(target=close_server_monitor).start()
        start_listener()
        print('Script finished')
    
if __name__ == '__main__':
    main()
    input()