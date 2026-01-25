import os
import sys
import threading
import subprocess 
import asyncio
import time
import edge_tts
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

MEDIA_FOLDER_PATH = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Titanfall2\\R2Northstar\\mods\\chatts\\mod\\media'

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def make_filepath(input, position):
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

async def convert_to_bik(input, position):
    radvideo = get_radvideo()
    if not radvideo:
        return 
    
    output = make_filepath(False, position)
    # print('TTS OUTPUT FILEPATH: ' + output)

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

    print('FINISH')
    return True

async def generate_tts(text, voice, position):
    communicate = edge_tts.Communicate(text, voice)
    path = make_filepath(True, position)
    print('TTS INPUT FILEPATH: ' + path)

    await communicate.save(path)
    success = await convert_to_bik(path, position)
    delete_file(path)
    return True if success else False

# asyncio.run(generate_tts('h', 'de-DE-ConradNeural', 0))

###########################################################################################################################

class Server(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_POST(self):
        path = urlparse(self.path).path
        print(path)

        match path:
            case '/makeTTS':
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
         
                message = params['message'][0]
                voice = params['voice'][0]
                position = int(params['position'][0])

                print( type(message) )
                print( type(voice) )
                print( type(position) )
                
                success = asyncio.run(generate_tts(message, voice, position))
                
                self.send_response(200 if success else 404)
                self.end_headers()

                return

            case _:
                self.send_response(400)
                self.end_headers()
                print('huh?')
                return

###########################################################################################################################

def parse_args(args):
    parsed = []
    
    for k, v in args.items():
        parsed.append(f'--{k}')
        parsed.append(''.join(v))

    return parsed

###########################################################################################################################

def launch_game():
    if 'Titanfall2.exe' in subprocess.check_output('tasklist').decode('UTF-8'):
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
    HTTPServer(('127.0.0.1', 2222), Server).serve_forever()
    print('Listener closed')

###########################################################################################################################

def main():
    # if launch_game():
        threading.Thread(target=start_listener).start()
    
if __name__ == '__main__':
    main()