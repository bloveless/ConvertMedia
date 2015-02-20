# ConvertMedia
An automatic python script to convert media and view its progress

The first thing that needs to be done is to update the LOGDIR and COMPLETEDPATH at the top of the python file. The LOGDIR is where all the log files will be created and the COMPLETEDPATH is where the video will be moved to after a converted copy is created.

After you change the LOGDIR you will need to update the paths in the error_tail.sh, messsage_tail.sh, and progress_tail.sh file to be correct. These files are not necessary but make it easy to monitor the progress of the conversions.

Last update the start_conversion.sh script to have the correct path to the convertMedia.py script. This script wraps the convertMedia.py command in a screen call so that you can start the process and leave it running even after you log out of your server or close the terminal window. HINT: press Ctrl-A D to detach from the screen. This will leave it running in the background.

Feel free to contact me with any questions. Or create a pull request to update any parts of the script.

Thanks!
Brennon Loveless