from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.ttk import Notebook
from PIL import Image, ImageTk, ImageDraw
import os


class PyFlowHelper:
	def __init__(self):
		self.root = Tk()
		self.image_tabs = Notebook(self.root)
		self.opened_images = []
		self.init()

	def init(self):
		self.root.title("FlowHelper")
		self.root.geometry("400x400")
		# self.root.iconphoto(True,PhotoImage(file="resources/icon.png"))

		self.image_tabs.enable_traversal()

		self.root.bind("<Control-s>", self.save_current_image)
		self.root.bind("<p>", self.painting_over_top_and_bottom)

	def run(self):
		self.draw_menu()
		self.draw_widgets()

		self.root.mainloop()

	def draw_menu(self):
		menu_bar = Menu(self.root)

		file_menu = Menu(menu_bar, tearoff=0)
		file_menu.add_command(label="Open", command=self.open_new_images)
		file_menu.add_command(label="Save", command=self.save_current_image)
		file_menu.add_command(label="Save As", command=self.save_image_as)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self._close)
		menu_bar.add_cascade(label="File", menu=file_menu)

		edit_menu = Menu(menu_bar, tearoff=0)

		resize_menu = Menu(edit_menu, tearoff=0)
		resize_menu.add_command(label="75% of original size", command=lambda:self.resize_current_image(75))

		edit_menu.add_cascade(label="Resize", menu=resize_menu)

		edit_menu.add_command(label="Painting over top and bottom", command=self.painting_over_top_and_bottom)


		menu_bar.add_cascade(label="Edit", menu=edit_menu)

		self.root.configure(menu=menu_bar)

	def draw_widgets(self):

		self.button_open_images = Button(self.root, text="Open images", command=self.open_new_images).pack(pady=1)
		self.button_fill_top_bot = Button(self.root, text="Painting over top and bottom", command=self.painting_over_top_and_bottom).pack(pady=1)

		self.image_tabs.pack(fill="both", expand=1)

	def open_new_images(self):
		image_paths = fd.askopenfilenames(filetypes=(("Images", "*.jpeg;*.jpg;*.png"),))
		for image_path in image_paths:
			self.add_new_image(image_path)

	def add_new_image(self, image_path):
		image = Image.open(image_path)
		image_tk = ImageTk.PhotoImage(image)
		
		self.opened_images.append([image_path, image])

		image_tab = Frame(self.image_tabs)

		image_label = Label(image_tab, image=image_tk, anchor="nw")
		image_label.image = image_tk
		image_label.pack(side="bottom", fill="both", expand="yes")

		self.image_tabs.add(image_tab, text=image_path.split('/')[-1])
		self.image_tabs.select(image_tab)

	def get_current_working_data(self):
		current_tab = self.image_tabs.select()
		if not current_tab:
			return None, None, None
		tab_number = self.image_tabs.index(current_tab)
		path, image = self.opened_images[tab_number]
		return current_tab, path, image

	def save_current_image(self, event=None):
		current_tab, path, image = self.get_current_working_data()
		if not current_tab:
			return
		tab_number = self.image_tabs.index(current_tab)

		if path[-1] == "*":
			path = path[:-1]
			self.opened_images[tab_number][0] = path
			image.save(path)
			self.image_tabs.add(current_tab, text=path.split('/')[-1])



	def save_image_as(self):
		current_tab, path, image = self.get_current_working_data()

		if not current_tab:
			return
		tab_number = self.image_tabs.index(current_tab)

		old_path, old_ext = os.path.splitext(path)
		if old_ext[-1] == "*":
			old_ext = old_ext[:-1]

		new_path = fd.asksaveasfilename(initialdir=old_path, filetypes=(("Images", "*.jpeg;*.jpg;*.png"),))
		if not new_path:
			return

		new_path, new_ext = os.path.splitext(new_path)
		if not new_ext:
			new_ext = old_ext
		elif old_ext != new_ext:
			mb.showerror("Incorrect extension", f"Got incorrect extension: {new_ext}. Old was: {old_ext}")
			return

		image.save(new_path+new_ext)
		image.close()

		del self.opened_images[tab_number]
		self.image_tabs.forget(current_tab)

		self.add_new_image(new_path + new_ext)

	def update_image_inside_app(self, current_tab, image):
		tab_number = self.image_tabs.index(current_tab)
		tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
		label = tab_frame.children["!label"]

		self.opened_images[tab_number][1] = image

		image_tk = ImageTk.PhotoImage(image)
		label.configure(image=image_tk)
		label.image = image_tk

		image_path = self.opened_images[tab_number][0]
		if image_path[-1] != "*":
			image_path += "*"
			self.opened_images[tab_number][0] = image_path
			image_name = image_path.split('/')[-1]
			self.image_tabs.tab(current_tab, text=image_name)
		
	def resize_current_image(self, percents):
		current_tab, path, image = self.get_current_working_data()
		if not current_tab:
			return

		width, height = image.size
		width = (width*percents) // 100
		height = (height*percents) // 100

		image = image.resize( (width, height), Image.LANCZOS )

		self.update_image_inside_app(current_tab, image)


	def painting_over_top_and_bottom(self, event=None):
		current_tab, path, image = self.get_current_working_data()
		if not current_tab:
			return

		outline = (0,0,0)
		width, height = image.size

		coord_y = height / 100 * 4
		coord_y1 = height / 100 * 94.5
		coord_x = width / 100 * 78
		coord_x1 = width / 100 * 89

		rect1 = (0, 0, width, coord_y)
		rect2 = (coord_x, coord_y, width, coord_y*2)
		rect3 = (0, coord_y1, coord_x1, height)

		draw = ImageDraw.Draw(image)
		draw.rectangle( rect1, fill="black", outline=outline )
		draw.rectangle( rect2, fill="black", outline=outline )
		draw.rectangle( rect3, fill="black", outline=outline )

		self.update_image_inside_app(current_tab, image)

	def _close(self):
		self.root.quit()


if __name__ == "__main__":
	PyFlowHelper().run()