import itertools
import unittest

from akkio_take_home.generate import (
    IdenticonGenerator,
    IdenticonImageWriter,
    _get_palette,
)


class TestIdenticonGenerator(unittest.TestCase):
    def test_palette(self):
        base, colors = _get_palette(4, base_color_idx=0, use_gradient=False)
        self.assertEqual(base, (0, 0, 0))
        self.assertEqual(len(colors), 3)

        base, colors = _get_palette(3, base_color_idx=-1, use_gradient=False)
        self.assertNotEqual(base, (0, 0, 0))
        self.assertEqual(len(colors), 2)

        base, colors = _get_palette(5, base_color_idx=0)

    def test_identicon_generator(self):
        names = ["graham", "graham "]

        num_colors = 3
        grid_generator = IdenticonGenerator(num_colors=num_colors)

        grids = [grid_generator(name) for name in names]
        self.assertNotEqual(grids[0], grids[1])

    def test_image_generator(self):
        num_colors = 4
        name = "graham"
        grid_generator = IdenticonGenerator(num_colors=num_colors)

        hash_digest = grid_generator.make_hash(name)

        self.assertEqual(len(hash_digest), 64)

        binary_digest = grid_generator.make_digest(hash_digest)
        # since the hash is 64 bits long (from sha256),
        # will give 64 hexadecimal chars, the binary digest should be 256 characters long
        self.assertEqual(len(binary_digest), 256)
        grid = grid_generator.make_identicon_grid(binary_digest)

        grid = grid_generator.make_identicon_grid(binary_digest)
        cgrid = grid_generator.make_color_grid(grid)

        # check that all the vals in cgrid are in the colors we allow
        flat_cgrid = itertools.chain(*cgrid)
        self.assertListEqual(
            list(filter(lambda v: v not in grid_generator.colors, flat_cgrid)), []
        )

        image_writer = IdenticonImageWriter()

        # test that it works with both binary and colored grids
        cimage = image_writer.generate_image(cgrid)
        oimage = image_writer.generate_image(grid)

        self.assertEqual(cimage.size, oimage.size)
        cimage.save("out/test-color.png")
        oimage.save("out/test-nocolor.png")

        # test grid_generator call
        grid_generator = IdenticonGenerator(num_colors=5)
        bw_grid = grid_generator("Name Grid", return_colored=False)

        self.assertIn(0, list(itertools.chain(*bw_grid)))
        self.assertIn(1, list(itertools.chain(*bw_grid)))

    def test_example(self):
        name = "full example"
        image_writer = IdenticonImageWriter()
        image_writer(name, output_file="out/test-example.png")

        image_writer = IdenticonImageWriter()
        image_writer("Graham Generated", output_file="out/test-example.png")
