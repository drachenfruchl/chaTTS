import asyncio
import edge_tts
import os   
import subprocess
import time

# voices = [
#     'de-AT-IngridNeural',
#     'de-AT-JonasNeural',
#     'de-CH-JanNeural',
#     'de-CH-LeniNeural',
#     'de-DE-AmalaNeural',
#     'de-DE-ConradNeural',
#     'de-DE-FlorianMultilingualNeural',
#     'de-DE-KatjaNeural',
#     'de-DE-KillianNeural',
#     'de-DE-SeraphinaMultilingualNeural'       
# ]

# async def generate_speech(text, voice):
#     communicate = edge_tts.Communicate(text, voice)
#     path = make_filepath(voice)
#     await communicate.save(path)

# def make_filepath(voice):
#     parts = voice.split('-')
#     lang = parts[0]
#     sublang = parts[1]
#     voice_short = parts[2]

#     path = './{}/{}'.format(lang, sublang)
#     make_lang_directory(path)

#     path += '/{}.mp3'.format(voice_short.replace('Neural',''))
#     return path

# def make_lang_directory(path):
#     if not os.path.exists(path):
#         os.makedirs(path)

# async def main(text):
#     await asyncio.gather(*[
#         asyncio.create_task(
#             generate_speech(text, voice)
#         ) for voice in voices
#     ])



# if __name__ == '__main__':
#     text = input('TTS Input: ')
#     asyncio.run(main(text))
#     print('Speech generated successfully')






# chat message received
# send request with position in queue to create tts message and file
# delay display of chat message until tts file has been created

# uniform, friends, team, ally, opp, self, party

# 'R2Northstar/mods/chaTTS/mod/media'

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

# def has_finished

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
    await convert_to_bik(path, position)
    delete_file(path)

def main():
    # asyncio.run(generate_tts('digga was ist denn falsch bei dir? warum machst du diese nachricht so geisteskrank lange? willst du denn etwa das programm was aktuell nur wegen diesem verkackten radvideo reinkackt testen?', 'de-DE-ConradNeural', 0))
    asyncio.run(generate_tts('h', 'de-DE-ConradNeural', 0))


main()