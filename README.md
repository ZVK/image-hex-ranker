# image-hex-ranker
Uses Python's asyncio to batch request images from a list of URLs and logs the top colors in hexidecimal

## dependencies
- Python 3.6

- Aiohttp

- PIL

- Numpy

## quick start
<pre>
  cd ./image-hex-ranker/
  python async_image_scraper.py
</pre>

### input
1. urls.txt with an image per row

### output
1. colors.csv with url,color1,color2,color3 on each row

2. error_log.txt will write all exceptions to file
