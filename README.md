## Subscene grabber

Very rough python script to retrieve subtitle file from subscene.com.
It gets the zip file, extracts it and renames the downloaded subtitle file to the name of the video file for 
instant integration with most players.

It also waits for user input at the end for self verification of what is the actual subtitle that has been downloaded.

You can also find a file *regedit.reg* in /res directory. It does not work *as is*, but you can use it to find the real
paths. Aim of it is to have a Windows contextual choice on .AVI & .MKV files to get subtitles faster.

## How to use

usage: main.py [-h] [-l] file

positional arguments:
  file        
  The path to the video file.

optional arguments:

  -h, --help  show this help message and exit
  
  -l          Use to list all the available subtitles.