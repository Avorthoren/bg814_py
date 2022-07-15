import itertools
import math
import random
import time
import tkinter
from typing import Union


class Vector(list):
	def _ensure_compatibility(self, other: "Vector"):
		if not isinstance(other, Vector):
			return NotImplemented

		if len(self) != len(other):
			raise TypeError("Can not add vectors of different length")

	@property
	def size(self) -> int:
		return len(self)

	def __add__(self, other: "Vector") -> "Vector":
		self._ensure_compatibility(other)
		return Vector(x1 + x2 for x1, x2 in zip(self, other))

	def __iadd__(self, other: "Vector") -> "Vector":
		self._ensure_compatibility(other)
		for i in range(self.size):
			self[i] += other[i]
		return self

	def __sub__(self, other: "Vector") -> "Vector":
		self._ensure_compatibility(other)
		return Vector(x1 - x2 for x1, x2 in zip(self, other))

	def __isub__(self, other: "Vector") -> "Vector":
		self._ensure_compatibility(other)
		for i in range(self.size):
			self[i] -= other[i]
		return self

	def scalar_prod(self, other: "Vector") -> float:
		self._ensure_compatibility(other)
		return sum(x1 * x2 for x1, x2 in zip(self, other))

	def pretty_str(self):
		return "\n".join(str(el) for el in self)


class Matrix(list):
	@property
	def cols(self) -> int:
		return len(self)

	@property
	def rows(self) -> int:
		return len(self[0])

	def _ensure_same_size(self, other: "Matrix"):
		if self.cols != other.cols or self.rows != other.rows:
			raise TypeError("Matrix of different sizes are not supported in this context")

	def _ensure_addable(self, other):
		if not isinstance(other, Matrix):
			raise TypeError("other must be Matrix")
		self._ensure_same_size(other)

	def _ensure_multiplicable(self, other):
		if isinstance(other, Matrix):
			size = other.rows
		elif isinstance(other, Vector):
			size = other.size
		else:
			raise TypeError("other must be Matrix of Vector")

		if self.cols != size:
			raise TypeError(
				"Number of columns in left operand of multiplication"
				" must be equal to number of rows in right operand"
			)

	def __add__(self, other: "Matrix") -> "Matrix":
		self._ensure_addable(other)
		return Matrix(v1 + v2 for v1, v2 in zip(self, other))

	def __iadd__(self, other: "Matrix") -> "Matrix":
		self._ensure_addable(other)
		for i in range(self.cols):
			self[i] += other[i]
		return self

	def __sub__(self, other: "Matrix") -> "Matrix":
		self._ensure_addable(other)
		return Matrix(v1 - v2 for v1, v2 in zip(self, other))

	def __isub__(self, other: "Matrix") -> "Matrix":
		self._ensure_addable(other)
		for i in range(self.cols):
			self[i] -= other[i]
		return self

	def __mul__(self, other: Union["Matrix", Vector]) -> Union["Matrix", Vector]:
		self._ensure_multiplicable(other)
		if isinstance(other, Vector):
			return Vector(
				Vector(
					self[j][i]
					for j in range(self.cols)
				).scalar_prod(other)
				for i in range(self.rows)
			)

		m = Matrix(
			Vector(
				Vector(
					self[j][i]
					for j in range(self.cols)
				).scalar_prod(other[k])
				for i in range(self.rows)
			)
			for k in range(other.cols)
		)
		if m.cols == 1:
			return m[0]
		else:
			return m

	def __rmul__(self, other: Vector) -> "Matrix":
		# TODO: return Vector for length 1?
		if not isinstance(other, Vector):
			raise TypeError("other must be Matrix of Vector")

		other = Matrix(other for _ in range(1))
		return other * self

	@classmethod
	def identity(cls, size: int) -> "Matrix":
		return Matrix(
			Vector(
				1 if j == i else 0
				for j in range(size)
			)
			for i in range(size)
		)

	def pretty_str(self):
		return "\n".join(str(list(self[i][j] for i in range(self.cols))) for j in range(self.rows))


def create_rotation_matrix(angle: float) -> Matrix:
	return Matrix((
		Vector((math.cos(angle), math.sin(angle))),
		Vector((-math.sin(angle), math.cos(angle)))
	))


def convert(v: Vector, m: Matrix, dv: Vector) -> Vector:
	return m * v + dv


MAX_H, MAX_W = 500, 500
DH, DW = 5, 5
COLORS = "red", "green", "blue", "orange", "magenta", "cyan", "brown", "olive", "yellow"
BG_COLOR = "white"


def to_graphic_coords(pos: Vector) -> tuple[float, float]:
	return pos[0] + (MAX_W >> 1), -pos[1] + (MAX_H >> 1)


def draw_axis(canvas: tkinter.Canvas):
	origin = Vector((0, 0))
	ox, oy = to_graphic_coords(origin)
	canvas.create_line(ox, 0, ox, MAX_H, fill="black")
	canvas.create_line(0, oy, MAX_W, oy, fill="black")


def construct_figure(xsize: int, ysize: int) -> list[Vector]:
	xs, ys = xsize >> 1, ysize >> 1
	return [
		Vector((xs, ys)),
		Vector((-xs, ys)),
		Vector((-xs, -ys)),
		Vector((xs, -ys))
	]


def convert_figure_for_draw(figure: list[Vector]):
	for pos in figure:
		x, y = to_graphic_coords(pos)
		yield x
		yield y


def draw_figure(figure: list[Vector], color: str, canvas: tkinter.Canvas):
	coords = tuple(convert_figure_for_draw(figure))
	canvas.create_polygon(
		coords,
		outline=color,
		fill=BG_COLOR
	)


def make_random_dots(n: int, xsize: int, ysize: int) -> list[Vector]:
	xs, ys = xsize >> 1, ysize >> 1
	return [
		Vector((random.randint(-xs, xs), random.randint(-ys, ys)))
		for _ in range(n)
	]


def draw_dots(dots: list[Vector], canvas: tkinter.Canvas) -> None:
	coords = tuple(convert_figure_for_draw(dots))

	THICKNESS = 1

	canvas.create_oval(
		coords[0] - THICKNESS,
		coords[1] - THICKNESS,
		coords[0] + THICKNESS,
		coords[1] + THICKNESS,
		outline=COLORS[0],
		fill=COLORS[0]
	)

	for i in range(2, len(coords), 2):
		color_i = (i >> 1) % len(COLORS)
		canvas.create_line(
			coords[i-2] - THICKNESS,
			coords[i-1] - THICKNESS,
			coords[i] + THICKNESS,
			coords[i+1] + THICKNESS,
			fill=COLORS[color_i - 1]
		)
		canvas.create_oval(
			coords[i] - THICKNESS,
			coords[i+1] - THICKNESS,
			coords[i] + THICKNESS,
			coords[i+1] + THICKNESS,
			outline=COLORS[color_i],
			fill=COLORS[color_i]
		)


def main():
	INIT_SIZE = 490
	m_enlarge = Matrix((Vector((0.5, 0)), Vector((0, 0.8))))
	print("m_enlarge")
	print(m_enlarge.pretty_str())
	m_rotate = create_rotation_matrix(9 * math.pi / 16)
	print("m_rotate")
	print(m_rotate.pretty_str())
	m = m_enlarge * m_rotate
	print("m")
	print(m.pretty_str())

	dv = Vector((INIT_SIZE / 5, 0))

	print()

	main_window = tkinter.Tk()
	canvas = tkinter.Canvas(main_window, bg=BG_COLOR, height=MAX_H, width=MAX_W)

	TOTAL_STEPS = 8
	figure = construct_figure(INIT_SIZE, INIT_SIZE)
	# dots are for demonstration.
	fixed_point = Vector((68.51347837188396, 46.50021529631321))
	dots = [fixed_point]
	dots.extend(make_random_dots(TOTAL_STEPS-1, INIT_SIZE, INIT_SIZE))

	draw_figure(figure, COLORS[0], canvas)
	print(figure)
	for step in range(1, TOTAL_STEPS):
		for i in range(len(figure)):
			figure[i] = convert(figure[i], m, dv)
		for i in range(step, TOTAL_STEPS):
			dots[i] = convert(dots[i], m, dv)

		draw_figure(figure, COLORS[step % len(COLORS)], canvas)
		print(figure)

	# draw_axis(canvas)
	draw_dots(dots, canvas)
	canvas.pack()
	main_window.mainloop()


if __name__ == "__main__":
	main()
