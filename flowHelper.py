from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.ttk import Notebook
from PIL import Image, ImageTk, ImageDraw
import os
import json

from image_info import ImageInfo


CONFIG_FILE = "config.json"

class PyFlowHelper:
	def __init__(self):
		self.root = Tk()
		self.image_tabs = Notebook(self.root)
		self.opened_images = []

		self.init()

	def init(self):
		self.root.title("FlowHelper")
		pad = 0.87
		self.root.geometry(f"{int(self.root.winfo_screenwidth()*pad)}x{int(self.root.winfo_screenheight()*pad)}")
		# self.root.resizable(False,False)
		# self.root.iconphoto(True,PhotoImage(file="resources/icon.png"))

		self.image_tabs.enable_traversal()

		

		self.root.bind("<Control-s>", self.save_current_image)
		self.root.bind("<Control-f>", self.painting_over_top_and_bottom)
		self.root.bind("<Control-w>", self.close_current_image)
		self.root.bind("<s>", self.start_area_selection)
		self.root.bind("<f>", self.fill_selection_area_of_current_image)

		self.root.protocol("WM_DELETE_WINDOW", self._close)

		if not os.path.exists(CONFIG_FILE):
			with open(CONFIG_FILE, 'w') as f:
				json.dump({"opened_images": []}, f)
		else:
			self.load_images_from_config()

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
		file_menu.add_command(label="Save All", command=self.save_all_changes)
		file_menu.add_separator()
		file_menu.add_command(label="Close image", command=self.close_current_image)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self._close)
		menu_bar.add_cascade(label="File", menu=file_menu)

		edit_menu = Menu(menu_bar, tearoff=0)
		edit_menu.add_command(label="Painting over top and bottom", command=self.painting_over_top_and_bottom)
		edit_menu.add_command(label="Painting over selection", command=self.fill_selection_area_of_current_image)

		select_menu = Menu(edit_menu, tearoff=0)
		select_menu.add_command(label="Start selection", command=self.start_area_selection)
		edit_menu.add_cascade(label="Selection menu", menu=select_menu)

		menu_bar.add_cascade(label="Edit", menu=edit_menu)

		self.root.configure(menu=menu_bar)

	def draw_widgets(self):

		self.button_open_images = Button(self.root, text="Open images", command=self.open_new_images).pack(pady=1, side=TOP)
		self.button_fill_top_bot = Button(self.root, text="Painting over top and bottom", command=self.painting_over_top_and_bottom).pack(pady=1, side=TOP)
		self.button_fill_selection = Button(self.root, text="Fill selection", command=self.fill_selection_area_of_current_image).pack(pady=1, side=TOP)
		self.button_start_selection = Button(self.root, text="Start selection", command=self.start_area_selection).pack(pady=1, side=LEFT)
		
		self.image_tabs.pack(fill="both", expand=1)

	def load_images_from_config(self):
		with open(CONFIG_FILE, "r") as f:
			config = json.load(f)

		paths = config["opened_images"]
		
		for path in paths:
			if not os.path.exists(path):
				continue
			self.add_new_image(path)


	def open_new_images(self):
		image_paths = fd.askopenfilenames(filetypes=(("Images", "*.jpeg;*.jpg;*.png"),))
		for image_path in image_paths:
			self.add_new_image(image_path)

	def add_new_image(self, image_path):
		opened_images = [info.path for info in self.opened_images]
		if image_path in opened_images:
			index = opened_images.index(image_path)
			self.image_tabs.select(index)
			return

		image = Image.open(image_path)
		image_tab = Frame(self.image_tabs)

		image_info = ImageInfo(image, image_path, image_tab)
		self.opened_images.append(image_info)

		image_tk = image_info.image_tk
		

		image_canvas = Canvas(image_tab, width=image.width, height=image.height, bd=0, highlightthickness=0)
		image_canvas.image = image_tk
		image_canvas.create_image(0,0, image=image_tk, anchor="nw")
		image_canvas.pack(expand="yes")

		image_info.canvas = image_canvas

		self.image_tabs.add(image_tab, text=image_info.filename())
		self.image_tabs.select(image_tab)

		self.resize_current_image(75)


	def current_image(self):
		current_tab = self.image_tabs.select()
		if not current_tab:
			return None
		tab_number = self.image_tabs.index(current_tab)
		return self.opened_images[tab_number]

	def save_current_image(self, event=None):
		image = self.current_image()
		if not image:
			return
		if not image.unsaved:
			return

		image.save()
		self.image_tabs.add(image_tab, text=image.filename())


	def save_image_as(self):
		image = self.current_image()

		if not image:
			return
		
		try:
			image.save_as()
			self.update_image_inside_app(image)
		except ValueError as e:
			mb.showerror("Save as error", str(e))

	def save_all_changes(self):
		for image_info in self.opened_images:
			if not image_info.unsaved:
				continue
			image_info.save()
			self.image_tabs.tab(image_info.tab, text=image_info.filename())

	def close_current_image(self, event=None):
		image = self.current_image()
		if not image:
			return

		if image.unsaved:
			if not mb.askyesno("Unsaven changes", "Got unsaved changes. Exit anyway?"):
				return

		image.close()
		self.image_tabs.forget(image.tab)
		self.opened_images.remove(image)

	def update_image_inside_app(self, image_info):
		image_info.update_image_on_canvas()

		self.image_tabs.tab(image_info.tab, text=image_info.filename())
		
	def resize_current_image(self, percents):
		image = self.current_image()
		if not image:
			return

		image.resize(percents)
		image.unsaved = True
		self.update_image_inside_app(image)


	def painting_over_top_and_bottom(self, event=None):
		image = self.current_image()
		if not image:
			return

		image.paint_top_bot()
		image.unsaved = True
		self.update_image_inside_app(image)

	def start_area_selection(self, event=None):
		image = self.current_image()
		if not image:
			return

		image.start_selection()

	def fill_selection_area_of_current_image(self, event=None):
		image = self.current_image()
		if not image:
			return

		try:
			image.fill_selected_area()
			image.unsaved = True
			self.update_image_inside_app(image)
		except ValueError as e:
			mb.showerror("Painting error", str(e))

	def save_images_to_config(self):
		paths = [info.full_path(no_star=True) for info in self.opened_images]
		images = {"opened_images": paths}
		with open(CONFIG_FILE, 'w') as f:
			json.dump(images, f, indent=4)


	def unsaved_images(self):
		for info in self.opened_images:
			if info.unsaved:
				return True
		return False

	def _close(self):
		if self.unsaved_images():
			if not mb.askyesno("Unsaven changes", "Got unsaved changes. Exit anyway?"):
				return
		self.save_images_to_config()
		self.root.quit()


if __name__ == "__main__":
	PyFlowHelper().run()