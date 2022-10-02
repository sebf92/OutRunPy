from datetime import datetime, timedelta
from time import sleep
from orbit import ISS
from picamera import PiCamera
from pathlib import Path

def convert(angle):
    """
    Convert a `skyfield` Angle to an EXIF-appropriate
    representation (rationals)
    e.g. 98° 34' 58.7 to "98/1,34/1,587/10"

    Return a tuple containing a boolean and the converted angle,
    with the boolean indicating if the angle is negative.
    """
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle

def capture(camera, imagebase, nbimage, pause):
	"""Use `camera` to capture an `image` file with lat/long EXIF data."""

	# Create a `datetime` variable to store the start time
	start_time = datetime.now()

	for i in range(nbimage):
		point = ISS.coordinates()
		# Convert the latitude and longitude to EXIF-appropriate representations
		south, exif_latitude = convert(point.latitude)
		west, exif_longitude = convert(point.longitude)

		# Set the EXIF tags specifying the current location
		camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
		camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
		camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
		camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

		# Capture the image
		image = imagebase+str(i).zfill(5)
		camera.capture(image)

		# pause X seconds
		sleep(pause)

		# Update the current time
		now_time = datetime.now()

		if(now_time > start_time + timedelta(minutes=179)):
			break # we exit the loop in any case if we are close to 3 hours...


cam = PiCamera()
cam.resolution = (1296,972)
cam.start_preview()

base_folder = Path(__file__).parent.resolve()
capture(cam, f"{base_folder}/gps_", 1000, 10)

