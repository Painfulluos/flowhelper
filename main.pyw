from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import filedialog


def addRectangle():
	filenames = filedialog.askopenfilenames()
	for filename in filenames:
		with Image.open(filename) as img:
			draw = ImageDraw.Draw(img)
			img.load()
			draw.rectangle( (0, 0, 1400, 35), fill="black", outline=(0,0,0) )
			draw.rectangle( (1100, 35, 1400, 70), fill="black", outline=(0,0,0) )
			draw.rectangle( (0, 730,1245, 767), fill="black", outline=(0,0,0) )
			# img.show()
			img.save(filename, "jpeg")

root = tk.Tk()
root.geometry("400x400")

choose_btn = tk.Button(root, text="Выбрать изображения", command=lambda:addRectangle())
choose_btn.pack()

root.mainloop()