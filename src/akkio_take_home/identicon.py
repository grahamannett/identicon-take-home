import copy
import hashlib
import string
from random import randint, choice

from PIL import Image, ImageDraw

# --- CONSTANTS ---
CHARACTERS_ALLOWED = string.ascii_letters + string.digits + " "
STRING_MAX_LENGTH = 10

GridType = list[list[int]]
ColorType = tuple[int, int, int]
ColorGridType = list[list[ColorType]]


BASE_COLORS = [
    (0, 0, 0),  # Black
    (255, 255, 255),  # White
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]


def _get_palette(
    num_colors: int,
    base_color_idx: int = None,
    end_color_idx: int = None,  # only important for gradient
    use_gradient: bool = True,
):
    """
    Get a palette of colors with an optional gradient between start and end colors.

    Args:
        num_colors (int): The number of colors in the palette.
        base_color_idx (int, optional): Index of the base color. Defaults to None.
        end_color_idx (int, optional): Index of the end color for gradient. Defaults to None.
        use_gradient (bool, optional): Whether to use color gradient. Defaults to True.

    Returns:
        tuple: A tuple containing the base color and the palette of colors.
    """
    colors = copy.deepcopy(BASE_COLORS)

    if base_color_idx is None:
        base_color_idx = randint(0, num_colors - 1)

    if not use_gradient:
        base_color = colors.pop(base_color_idx)
        palette = colors[: num_colors - 1]

    else:
        # Create color gradient
        palette = []

        # remove the base color from the list so it doesn't get picked again
        base_color = colors.pop(base_color_idx)
        end_color = (
            colors[end_color_idx] if end_color_idx is not None else choice(colors)
        )

        for i in range(num_colors):
            ratio = i / (num_colors - 1)
            r = int(base_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(base_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(base_color[2] * (1 - ratio) + end_color[2] * ratio)
            palette.append((r, g, b))

    return base_color, palette


class IdenticonGenerator:
    """
    A class to generate identicons based on a given input string.

    Identicons are visual representations of hash values, typically used to represent users or data in a visually distinct manner.
    """

    def __init__(
        self,
        num_colors: int = 4,
        use_gradient: bool = True,
        base_color_idx: int = None,
        end_color_idx: int = None,
    ):
        """
        Initialize a Generate object.

        Args:
            grid_size (int): The size of the grid. Defaults to 16.
            num_colors (int): The number of colors. Defaults to 4.
        """
        # note: I thought grid_size could be a param but it seems like it has to be 16 so it coincides with the digest size
        self.grid_size = 16
        self._bin_digest_format = "04b"  # maybe better name/format for this?
        self.num_colors = num_colors
        self.use_gradient = use_gradient

        self.base_color, self.palette = _get_palette(
            self.num_colors,
            base_color_idx=base_color_idx,
            end_color_idx=end_color_idx,
            use_gradient=self.use_gradient,
        )

        self._params_check()

    def __call__(self, string: str, return_colored: bool = True):
        """
        Generates an identicon grid based on the given string.

        Args:
            string (str): The input string used to generate the identicon.
            return_colored (bool, optional): Specifies whether to return a colored grid or a binary grid.
                Defaults to True.

        Returns:
            list: The generated identicon grid.

        """
        hash_digest = self.make_hash(string)
        binary_digest = self.make_digest(hash_digest)
        grid = self.make_identicon_grid(binary_digest)

        if return_colored:
            grid = self.make_color_grid(grid)
        return grid

    def _params_check(self):
        """
        Checks the parameters of the generator.

        Raises:
            ValueError: If the grid entropy is less than the string entropy.
        """
        grid_entropy = 2 ** (self.grid_size * self.grid_size)
        string_entropy = len(CHARACTERS_ALLOWED) ** STRING_MAX_LENGTH

        if grid_entropy < string_entropy:
            raise ValueError("Not enough grid entropy")

    @property
    def colors(self):
        return [self.base_color] + self.palette

    def make_digest(self, hash: str) -> str:
        """
        Converts a hexadecimal hash string to a binary digest string.

        Args:
            hash (str): The hexadecimal hash string to convert.

        Returns:
            str: The binary digest string.

        """
        return "".join(format(int(x, 16), self._bin_digest_format) for x in hash)

    def make_hash(self, string: str) -> str:
        """
        Generates a SHA-256 hash for the given string.

        Args:
            string (str): The string to be hashed.

        Returns:
            str: The hexadecimal representation of the hash.
        """
        hash_object = hashlib.sha256(string.encode())
        return hash_object.hexdigest()

    def make_identicon_grid(self, binary_digest: str) -> GridType:
        """
        Generates an identicon grid based on the given binary digest.

        Args:
            binary_digest (str): The binary digest used to generate the identicon grid.

        Returns:
            list[list[int]]: The identicon grid represented as a 2D list of integers.
                Each element in the grid is either 0 or 1, indicating the presence or absence of a pixel.
        """
        # base grid is just empty
        grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        for i in range(self.grid_size * self.grid_size):
            if binary_digest[i] == "1":
                row = i // self.grid_size
                col = i % self.grid_size
                grid[row][col] = 1
        return grid

    def make_color_grid(self, grid: GridType) -> ColorGridType:
        """
        Generates a color grid based on the given grid.

        Args:
            grid (GridType): The input grid.

        Returns:
            ColorGridType: The generated color grid.
        """
        grid_out = copy.deepcopy(grid)

        base_color, palette = self.base_color, self.palette

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 1:
                    grid_out[i][j] = palette[(i + j) % len(palette)]
                else:
                    grid_out[i][j] = base_color

        return grid_out


class IdenticonImageWriter:
    def __init__(self, image_size: int = 256, symmetric: bool = True):
        """
        Initialize the Generate class.

        Args:
            image_size (int): The size of the image. Defaults to 256.
            symmetric (bool): Flag indicating whether the image should be symmetric. Defaults to True.
        """
        self.image_size = image_size
        self.symmetric = symmetric

        # if symmetric we just generate half and then mirror, but need to make the block size half
        self.block_size = self.image_size // 2 if self.symmetric else self.image_size

    def __call__(self, string: str, output_file: str = None, **kwargs) -> Image.Image:
        """
        Generates an identicon image based on the given string and saves it to a file.

        Args:
            string (str): The input string used to generate the identicon.
            output_file (str): The output file to save the image to.

        """
        grid_generator = IdenticonGenerator(**kwargs)
        grid = grid_generator(string)

        image = self.generate_image(grid, output_file=output_file)

        return image

    def generate_image(
        self, grid: ColorGridType | GridType, output_file: str = None
    ) -> Image.Image:
        """
        Generates an image based on the provided grid.

        Args:
            grid (ColorGridType | GridType): The grid representing the image.

        Returns:
            Image.Image: The generated image.

        """
        image = Image.new("RGB", (self.image_size, self.image_size), "white")
        draw = ImageDraw.Draw(image)

        block_width = self.image_size / len(grid[0])
        block_height = self.image_size / len(grid)

        # breakpoint()

        def _get_color(c):
            if isinstance(c, tuple):
                return c
            return ["white", "black"][c]

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                color = _get_color(grid[i][j])
                x1 = j * block_width
                y1 = i * block_height
                x2 = (j + 1) * block_width
                y2 = (i + 1) * block_height
                draw.rectangle((x1, y1, x2, y2), fill=color)

        if self.symmetric:
            left_half = image.crop((0, 0, self.block_size, self.image_size))
            right_half = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            image.paste(right_half, (self.block_size, 0))

        if output_file:
            image.save(output_file)

        return image
