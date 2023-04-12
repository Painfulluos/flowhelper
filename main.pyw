from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import filedialog


def addRectangle():
	filenames = filedialog.askopenfilenames()

	outline= (0,0,0)
	for filename in filenames:
		with Image.open(filename) as img:
			width = img.size[0]
			height = img.size[1]

			rect1 = (0, 0, width, 35)
			rect2 = (width-300, 35, width, 70)
			rect3 = (0, height-50, width-150, height)

			draw = ImageDraw.Draw(img)
			img.load()
			draw.rectangle( rect1, fill="black", outline=outline )
			draw.rectangle( rect2, fill="black", outline=outline )
			draw.rectangle( rect3, fill="black", outline=outline )
			# img.show()
			img.save(filename, "jpeg")
			print(f"image resolution: {img.size[0]}x{img.size[1]}")

root = tk.Tk()

root.geometry("400x400")

choose_btn = tk.Button(root, text="Выбрать изображения", command=lambda:addRectangle())
choose_btn.pack()

root.mainloop()