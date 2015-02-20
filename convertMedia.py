#! /usr/bin/env python

from os import walk, path
import subprocess, re, os

# The directory where all the log files will be written to
LOGDIR = "/var/downloads/scripts/ConvertMedia/logs/"
# Any log messages will be written to this file
QUEUELOG = LOGDIR+"convertMedia.queue.log"
# STDERR from HandBrakeCLI will be written here. There is quite a bit of diagnostic information in here
ERRORLOG = LOGDIR+"convertMedia.error.log"
# STDOUT from HandBrakeCLI will be written here. This is simply the progress of the currently running conversion.
PROGRESSLOG = LOGDIR+"convertMedia.progress.log"
# After the conversion is completed the files will be moved to this directory. Nothing gets deleted.
COMPLETEDPATH = "/var/nas/PreConverted/"

def log(message):
	print message
	with open(QUEUELOG, "a") as queue_log:
		queue_log.write(message+"\r\n")

def convert_video(file_path, requested_file_size):
	file_info = subprocess.check_output(['file', file_path])
	is_mp4 = "MPEG v4" in file_info
	# Get filesize in mb
	file_size = path.getsize(file_path) / (1024 * 1024.0)
	# File is too large if it is 100mb larger than the requested file size. KPBS calculations are not exact. This allows for some leeway
	file_is_too_large = file_size > (requested_file_size + 100)
	if not is_mp4 or file_is_too_large:
		log("Converting video: "+file_path)
		# Use the media info command to get the duration of the movie
		media_info = subprocess.check_output(['mediainfo', file_path])
		# Sometimes the length of the movie is 55mn 34s so use a regex to parse out those numbers
		matches = re.search('Duration.+?:.+?(\d+)mn (\d+)s', media_info)
		video_length = 0
		if matches is not None and matches is not None:
			video_length += (int(matches.group(1)) * 60)
			video_length += (int(matches.group(2)))
		else:
			# If we couldn't find a file with 55mn 34s then we will try for 1h 5mn to calculate the kbps
			matches = re.search('Duration.+?:.+?(\d+)h (\d+)mn', media_info)
			if matches is not None and matches is not None:
				video_length += (int(matches.group(1)) * 3600)
				video_length += (int(matches.group(2)))
			else:
				# If neither of those formats worked then we will give up
				log("Could not determine length file will be skipped")

		# We can only convert the file if we know the length of the video in seconds
		if video_length is not 0:
			kbps = ((( requested_file_size * 1000 ) / video_length ) * 8 )
			log("Using kbps: "+str(kbps))
			with open(PROGRESSLOG, 'a') as progress_log, open(ERRORLOG, 'a') as error_log:
				conversion = subprocess.Popen(['HandBrakeCLI', '--preset', 'Normal', '--two-pass', '-b', str(kbps), '-i', file_path, '-o', file_path+'.mp4'], stdout=progress_log, stderr=error_log)
				stdout, stderr = conversion.communicate()
				# If the conversion returns a 0 then move the file to the PreConverted folder
				log("Return code: "+str(conversion.returncode))
				if conversion.returncode is 0:
					log('mv "%s" "%s"' % (file_path, COMPLETEDPATH))
					os.system('mv "%s" "%s"' % (file_path, COMPLETEDPATH))
	else:
		print "No conversion needed"

# Get all the tv shows and movies and run them through the convert_movie function

tv_shows = []
for (dirpath, dirnames, filenames) in walk('/var/nas/Television'):
	for tv_show in filenames:
		tv_shows.append(dirpath+'/'+tv_show)
		# Begin the conversion for the current video. The second parameter is the requested file size in mb
		convert_video(dirpath+'/'+tv_show, 250)

movies = []
for (dirpath, dirnames, filenames) in walk('/var/nas/Movies'):
	for movie in filenames:
		movies.append(dirpath+'/'+movie)
		# Begin the conversion for the current video. The second parameter is the requested file size in mb
		convert_video(dirpath+'/'+movie, 1024)

# To add any more directories just copy and edit the above loops
