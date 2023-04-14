from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.ttk import Notebook
from PIL import Image, ImageTk, ImageDraw
import os
import json


CONFIG_FILE = "config.json"

class PyFlowHelper:
	def __init__(self):
		self.root = Tk()
		self.image_tabs = Notebook(self.root)
		self.opened_images = []

		self.selection_top_x = 0
		self.selection_top_y = 0
		self.selection_bottom_x = 0
		self.selection_bottom_y = 0

		self.canvas_for_selection = None
		self.selection_rect = None

		self.init()

	def init(self):
		self.root.title("FlowHelper")
		pad = 0.87
		self.root.geometry(f"{int(self.root.winfo_screenwidth()*pad)}x{int(self.root.winfo_screenheight()*pad)}")
		# self.root.resizable(False,False)
		# self.root.iconphoto(True,PhotoImage(file="resources/icon.png"))

		self.image_tabs.enable_traversal()

		

		self.root.bind("<Control-s>", self.save_current_image)
		self.root.bind("<p>", self.painting_over_top_and_bottom)
		self.root.bind("<Control-w>", self.close_current_image)

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
		edit_menu.add_command(label="Painting over selection", command=self.painting_current_selection)

		select_menu = Menu(edit_menu, tearoff=0)
		select_menu.add_command(label="Start selection", command=self.start_area_selection)
		select_menu.add_command(label="Stop selection", command=self.stop_area_selection)
		edit_menu.add_cascade(label="Selection menu", menu=select_menu)

		menu_bar.add_cascade(label="Edit", menu=edit_menu)

		self.root.configure(menu=menu_bar)

	def draw_widgets(self):

		self.button_open_images = Button(self.root, text="Open images", command=self.open_new_images).pack(pady=1, side=TOP)
		self.button_fill_top_bot = Button(self.root, text="Painting over top and bottom", command=self.painting_over_top_and_bottom).pack(pady=1, side=TOP)
		self.button_fill_selection = Button(self.root, text="Fill selection", command=self.painting_current_selection).pack(pady=1, side=TOP)
		self.button_start_selection = Button(self.root, text="Start selection", command=self.start_area_selection).pack(pady=1, side=LEFT)
		self.buttin_stop_selection = Button(self.root, text="Stop selection", command=self.stop_area_selection).pack(pady=1, side=RIGHT)
		
		self.image_tabs.pack(fill="both", expand=1)

	def load_images_from_config(self):
		with open(CONFIG_FILE, "r") as f:
			config = json.load(f)

		paths = config["opened_images"]
		for path in paths:
			self.add_new_image(path)


	def open_new_images(self):
		image_paths = fd.askopenfilenames(filetypes=(("Images", "*.jpeg;*.jpg;*.png"),))
		for image_path in image_paths:
			self.add_new_image(image_path)

	def add_new_image(self, image_path):
		image = Image.open(image_path)
		image_tk = ImageTk.PhotoImage(image)
		self.opened_images.append([image_path, image])

		image_tab = Frame(self.image_tabs)

		image_canvas = Canvas(image_tab, width=image_tk.width(), height=image_tk.height(), bd=0, highlightthickness=0)
		image_canvas.image = image_tk
		image_canvas.create_image(0,0, image=image_tk, anchor="nw")
		image_canvas.pack(expand="yes")

		self.image_tabs.add(image_tab, text=os.path.split(image_path)[1])
		self.image_tabs.select(image_tab)

		# self.resize_current_image(75)


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
			self.image_tabs.add(current_tab, text=os.path.split(path)[1])



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

	def save_all_changes(self):
		for index, (path, image) in enumerate(self.opened_images):
			if path[-1] != "*":
				continue
			path = path[:-1]
			self.opened_images[index][0] = path
			image.save(path)
			self.image_tabs.tab(index,text=os.path.split(path)[1])

	def close_current_image(self, event=None):
		current_tab, path, image = self.get_current_working_data()
		if not current_tab:
			return

		if path[-1]=="*":
			if not mb.askyesno("Unsaven changes", "Got unsaved changes. Exit anyway?"):
				return

		index = self.image_tabs.index(current_tab)

		image.close()
		del self.opened_images[index]
		self.image_tabs.forget(current_tab)

	def update_image_inside_app(self, current_tab, image):
		tab_number = self.image_tabs.index(current_tab)
		tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
		canvas = tab_frame.children["!canvas"]

		self.opened_images[tab_number][1] = image

		image_tk = ImageTk.PhotoImage(image)

		canvas.delete('all')
		canvas.image = image_tk
		canvas.configure(width=image_tk.width(), height=image_tk.height())
		canvas.create_image(0,0, image=image_tk, anchor="nw")

		image_path = self.opened_images[tab_number][0]
		if image_path[-1] != "*":
			image_path += "*"
			self.opened_images[tab_number][0] = image_path
			image_name = os.path.split(image_path)[1]
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

	def start_area_selection(self):
		current_tab = self.image_tabs.select()
		if not current_tab:
			return
		tab_frame = self.image_tabs.children[current_tab[current_tab.rfind("!"):]]
		canvas = tab_frame.children["!canvas"]
		
		self.canvas_for_selection = canvas
		self.selection_rect = canvas.create_rectangle(
			self.selection_top_x, self.selection_top_y, 
			self.selection_bottom_x, self.selection_bottom_y, 
			dash=(10, 10), fil="", outline="white", width=2
		)

		canvas.bind("<Button-1>", self.get_selection_start_pos)
		canvas.bind("<B1-Motion>", self.update_selection_end_pos)

	def get_selection_start_pos(self, event):
		self.selection_top_x, self.selection_top_y = event.x, event.y


	def update_selection_end_pos(self, event):
		self.selection_bottom_x, self.selection_bottom_y = event.x, event.y
		if self.canvas_for_selection is not None and self.selection_rect is not None:
			self.canvas_for_selection.coords(
				self.selection_rect,
				self.selection_top_x, self.selection_top_y,
				self.selection_bottom_x, self.selection_bottom_y
			)		


	def stop_area_selection(self):
		self.canvas_for_selection.unbind("<Button-1>")
		self.canvas_for_selection.unbind("<B1-Motion>")

		self.canvas_for_selection.delete(self.selection_rect)

		self.selection_rect = None
		self.canvas_for_selection = None
		self.selection_top_x, self.selection_top_y = 0, 0
		self.selection_bottom_x, self.selection_bottom_y = 0, 0


	def painting_current_selection(self):
		current_tab, path, image = self.get_current_working_data()
		if not current_tab:
			return
		outline = (0,0,0)
		draw = ImageDraw.Draw(image)
		draw.rectangle( (self.selection_top_x, self.selection_top_y, self.selection_bottom_x, self.selection_bottom_y), fill="black", outline=outline )

		self.update_image_inside_app(current_tab, image)

	def save_images_to_config(self):
		paths = [(path[:-1] if path[-1] == "*" else path) for (path, images) in self.opened_images]
		images = {"opened_images": paths}
		with open(CONFIG_FILE, 'w') as f:
			json.dump(images, f, indent=4)


	def unsaved_images(self):
		for path, _ in self.opened_images:
			if path[-1] == "*":
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