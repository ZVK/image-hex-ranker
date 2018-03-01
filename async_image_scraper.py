from collections import Counter
from PIL import Image
import numpy as np
import urllib.request
import time
import aiohttp
import asyncio
import async_timeout
import io

HEADERS = {'User-Agent': 'custom-header'}
VERBOSE = True

async def write_log(file, message):
    try:
        with open(file, "a") as log:
            log.write("{}\n".format(message))
            if (VERBOSE):
                print(message)
    except:
        print('WARNING: write_log() last line was not logged')

async def color_ranker(response):
    def rgb2hex(red, green, blue):
        return '#{:02x}{:02x}{:02x}'.format(red, green, blue)
    try:
        image = Image.open(io.BytesIO(response), "r")
    except:
        await write_log("error_log.txt", 'ERROR_IMAGE_OPEN'.format(url))
        raise
    try:
        pixels = list(image.getdata())
        #print(image.size, image.size[0]*image.size[1])
        pixels = list(image.convert('RGBA').getdata())
        pixels_hex = []
        for red, green, blue, _alpha in pixels:
           pixels_hex.append(rgb2hex(red, green, blue))
        counts = Counter(pixels_hex).most_common(3)
        return [counts[0][0], counts[1][0], counts[2][0]]
    except Exception:
        await write_log("error_log.txt","{}, ERROR_COLOR_RANKER".format(url))
        raise

async def fetch(url, session):
    try:
        async with session.get(url, headers=HEADERS, timeout=60*6) as response:
            if response.status == 200:
                try:
                    img = await response.read()
                except Exception:
                    print('ERROR response.read()')
                    raise
                colors = await color_ranker(img)
                await write_log("colors.csv","{}, {}, {}, {}".format(url, colors[0], colors[1], colors[2]))
                return colors
            else:
                await write_log("error_log.txt", "{}, ERROR_RESPONSE_STATUS_{}".format(url, response.status))
    except Exception:
        await write_log("error_log.txt", "{}, ERROR_FETCH_TIMEOUT".format(url))
        raise
    

async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(limit):
    def file_reader():
        with open("urls.txt","r") as file_in:
            for line in file_in:
                yield line
    tasks = []
    sem = asyncio.Semaphore(limit)
    line_index = 0
    async with aiohttp.ClientSession() as session:
        for url in file_reader():
                line_index = (line_index+1)%limit 
                # pass Semaphore and session to every GET request
                print('GET', url.strip('\n'))
                task = asyncio.ensure_future(bound_fetch(sem, url.strip('\n'), session))
                tasks.append(task)
                if (line_index+1 == limit):
                    try:
                        responses = asyncio.gather(*tasks)
                        print(responses)
                        await responses
                        tasks = []
                    except:
                        print("")#exceptions - batch complete
        if len(tasks) > 0:
            responses = asyncio.gather(*tasks)
            await responses
            
    await write_log("error_log.txt", "\n")


start = time.time()
batch_size = 3
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(batch_size))
try:
    loop.run_until_complete(future)
except:
    print('exiting')
loop.close()
print(time.time()-start)
