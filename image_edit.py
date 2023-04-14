from PIL import Image, ImageTk, ImageDraw


class ImageEdit:
	def __init__(self, image):
		self.original_image = image
		self.image = image.copy()

		self.canvas = None

		self.sel_start_x = 0
		self.sel_start_y = 0
		self.sel_stop_x = 0
		self.sel_stop_y = 0
		self.sel_rect = None

	@property
	def image_tk(self):
		return ImageTk.PhotoImage(self.image)

	def update_image_on_canvas(self):
		if self.canvas is None:
			raise RuntimeError("Canvas of image not given")
	
		image_tk = self.image_tk

		self.canvas.delete("all")
		self.canvas.configure(width=self.image.width, height=self.image.height)
		self.canvas.create_image(0,0, image=image_tk, anchor="nw")
		self.canvas.image = image_tk

	def resize(self, percents):
		width, height = self.image.size
		width = (width*percents) // 100
		height = (height*percents) // 100

		self.image = self.image.resize( (width, height), Image.LANCZOS )

	def paint_top_bot(self, event=None):
		outline = (0,0,0)
		width, height = self.image.size

		coord_y = height / 100 * 4
		coord_y1 = height / 100 * 94.5
		coord_x = width / 100 * 78
		coord_x1 = width / 100 * 89

		rect1 = (0, 0, width, coord_y)
		rect2 = (coord_x, coord_y, width, coord_y*2)
		rect3 = (0, coord_y1, coord_x1, height)

		draw = ImageDraw.Draw(self.image)
		draw.rectangle(rect1, fill="black", outline=outline)
		draw.rectangle(rect2, fill="black", outline=outline)
		draw.rectangle(rect3, fill="black", outline=outline)

	def start_selection(self):
		self.sel_rect = self.canvas.create_rectangle(
			self.sel_start_x, self.sel_start_y,
			self.sel_stop_x, self.sel_stop_y,
			dash=(10, 10), fill="cyan", width=1,
			stipple="gray25", outline="black"
		)

		self.canvas.bind("<Button-1>", self._get_selection_start)
		self.canvas.bind("<B1-Motion>", self._update_selection_stop)

	def _get_selection_start(self, event):
		self.sel_start_x, self.sel_start_y = event.x, event.y

	def _update_selection_stop(self, event):
		self.sel_stop_x, self.sel_stop_y = event.x, event.y
		self.canvas.coords(self.sel_rect, self.sel_start_x, self.sel_start_y, self.sel_stop_x, self.sel_stop_y)

	def	fill_selected_area(self):
		if self.sel_rect is None:
			raise ValueError("Got no selection area for painting operation")

		self.canvas.unbind("<Button-1>")
		self.canvas.unbind("<B1-Motion>")
		self.canvas.delete(self.sel_rect)

		if self.sel_start_x > self.sel_stop_x:
			self.sel_start_x, self.sel_stop_x = self.sel_stop_x, self.sel_start_x
		if self.sel_start_y > self.sel_stop_y:
			self.sel_start_y, self.sel_stop_y = self.sel_stop_y, self.sel_start_y

		outline = (0,0,0)
		draw = ImageDraw.Draw(self.image)
		draw.rectangle( 
			(
			self.sel_start_x, self.sel_start_y,
			self.sel_stop_x, self.sel_stop_y
			),
			fill="black", outline=outline
		)

		self.sel_rect = None
		self.sel_start_x, self.sel_start_y = 0, 0
		self.sel_stop_x, self.sel_stop_y = 0, 0




	def close(self):
		self.image.close()
		self.original_image.close()