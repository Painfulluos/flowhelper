from zipencrypt import ZipFile
from datetime import datetime
import os

import secrets
import string


def get_dir_name(info_images):
	img_dir_path = ''
	for info_image in info_images:
		if img_dir_path == '':
			img_dir_path = info_image.file_directory(no_star=True)
		elif img_dir_path != info_image.file_directory(no_star=True) and len(info_images) > 1:
			return
	img_dir_name = os.path.basename(img_dir_path)+".zip"
	# print(f"Получен путь:{img_dir_path}")
	# print(f"Получено имя:{img_dir_name}")
	return (img_dir_path, img_dir_name)

def create_password():
    password = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(12))
    return password

def arch(info_images):
	archive = get_dir_name(info_images)
	image_paths = [info.filename(no_star=True) for info in info_images]
	password = create_password()
	arr = bytes(password, 'utf-8')
	with ZipFile(archive[1], 'w') as zip_file:
		
		for image in image_paths:
			directory = os.path.dirname(os.path.abspath(__file__))
			# zip_file.write(image, pwd=arr)
			zip_file.write(os.path.join(directory, archive[0], image), image, pwd=arr)

	print(password)
	with open('password_log.txt', 'a') as f:
		f.writelines(f"{archive[1]}" + " - " + password + "\n")