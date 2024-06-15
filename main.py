import argparse

from akkio_take_home.identicon import IdenticonGenerator, IdenticonImageWriter


def main():
    parser = argparse.ArgumentParser(description="Generate an identicon image.")
    parser.add_argument(
        "name", type=str, help="The name to generate the identicon for."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="The output file to save the image to. If not provided, the image will not be saved.",
    )
    parser.add_argument(
        "--no-return-colored",
        action="store_true",
        help="Flag indicating whether the image should be black and white. Defaults to False.",
    )
    parser.add_argument(
        "--num-colors",
        type=int,
        default=4,
        help="The number of colors to use in the identicon. Defaults to 4.",
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=256,
        help="The size of the image. Defaults to 256.",
    )
    parser.add_argument(
        "--no-symmetric",
        action="store_true",
        help="Flag indicating whether the image should be symmetric. Defaults to True.",
    )
    parser.add_argument(
        "--no-gradient",
        action="store_true",
        help="Flag indicating whether the image should use a gradient. Defaults to False.",
    )

    parser.add_argument(
        "--base-color-idx",
        type=int,
        default=None,
        help="The index of the base color to use. Defaults to 0.",
    )

    parser.add_argument(
        "--end-color-idx",
        type=int,
        default=None,
        help="The index of the end color to use. Defaults to None.",
    )

    args = parser.parse_args()

    # instantiate the classes
    identicon_generator = IdenticonGenerator(
        num_colors=args.num_colors,
        use_gradient=not args.no_gradient,
        base_color_idx=args.base_color_idx,
        end_color_idx=args.end_color_idx,
    )
    image_writer = IdenticonImageWriter(
        image_size=args.image_size,
        symmetric=not args.no_symmetric,
    )

    # generate
    grid = identicon_generator(args.name, return_colored=not args.no_return_colored)
    image = image_writer.generate_image(grid, output_file=args.output)


if __name__ == "__main__":
    main()
