# akkio-take-home Project

Graham Annett
6/14/24

Note: throughout this readme, I use matrix and grid interchangeably.

# Setup
The project was initialized with pdm so it is more files than necessary but I find that its better to just always use something like pdm to start a project rather than attempting to migrate as it can be a pain.

To setup, you can use `pip install -r requirements && pip install -e .` or `pdm install && pdm sync` should also work. I believe the only external dependencies is `PIL`.

To make the zip file I used `zip -r graham_annett.zip src/ tests/ .gitignore main.py .pdm-python pdm.lock pyproject.toml README.md requirements.txt ` so hopefully it has everything and not included the `.venv` or `.git` folders. If there is any issue, please let me know and I will fix it.

# Usage

The code has 2 main classes both in `identicon.py`.  The `IdenticonGenerator` and the `IdenticonImageWriter` class.
It is possible to do everything just by instantiating and calling the `IdenticonImageWriter` with something like the following:

```python
image_writer = IdenticonImageWriter()
image_writer("Graham Generated", output_file="out/test-example.png")

# more in depth calls you can specify colors or just use a matrix with binary colors
grid_generator = IdenticonGenerator(num_colors=5)
grid = grid_generator("Name Grid", return_colored=False)
# and then generate image
black_white_image = image_writer.generate_image(grid)
```

or have included a `main.py` file that can be run with `python main.py` with the following:

```bash
NAME_HERE="Akkio NAME"
OUTFILE="out/akkio.png"
python main.py $NAME_HERE --output=$OUTFILE --image-size=255 --num-colors=8 --base-color-idx=2 --end-color-idx=6
```

# Implementation

The classes are structured such that the actual grid and generation of the uniqueness is all done with `IdenticonGenerator`, as I had hoped I could dictate more about the grid size/dimensions at first (I mention this later in the readme).  Mostly that class is responsible for going from the string->hash->grid.
I wanted to use a matrix/grid as originally starting on this it seemed easy enough and I would have extra time so planned to have it serve the array via webpage and then draw the image in canvas like the info mentioned which would allow no dependencies and result in me learning how to draw via canvas which seems useful. Probably could do that in another 30-60 minutes but wanted to finish this so just did the image generation with PIL. For the code I am submitting, the image could be created in PIL directly without needing this extra grid/matrix I do, but I think this way is more extendable so I just kept this how it is.

The `IdenticonImageWriter` class handles the png generation, there is not much to it besides using the `image_size` specified and then calculating the size of the blocks for the drawing.  This calculation is not really relevant since the grid is fixed size, but if I were to make the grid size variable then I believe this will work as is.


# Testing
There are a few simple tests in the `test_identicon.py` file.
It is not very robust and I do not check inputs or various params, just basic tests to get things working.  It is also a single TestClass, perhaps it would make more sense to split into a class per class implementation but the tests are simple enough that it is not really necessary.
It is possible to run the tests with `python -m unittest` from the root directory.


# Other Info

## Legibility

In terms of legibility, making it large enough is an easy way to make it legible, I do this by just dictating the image size as larger than the grid (which theoretically would allow for 16x16 identicon). I am not sure if there is a way to make the patterns more *cool* while still being unique/legible, I am guessing if I spent more time on it I could think of a way the blocks/colors repeat in a way that still maintains uniqueness. It does seem possible as quick search shows stuff like [this](https://github.com/laurentpayot/minidenticons) but I have not looked at what they do to make the images have more structure while still being unique.
Overall I just allowed it to be symmetric which seems to help with legibility while ensuring the grid has enough entropy that it will allow characters from uppercase/lowercase/digits to be used (as well as spaces, and probably it has enough entropy to allow for punctuation and other non ascii characters).

## Uniqueness
Uniqueness from similar strings seems important.  For example "John" vs "Jon" vs "John " should be different, the idea of having them similar is problematic from an identity perspective.
I believe there was a recent story about a specific crypto attack where the attacker had generated similar addresses to whale accounts, when one whale did a trial transfer to transfer a large sum of money, the attacker sent money with their own similar address and then the victim copied the wrong address when they tried to transfer just after that? This will not solve that issue at all, but having similar images/grids seems like there are many more issues that could arise for no benefit.
Im also curious if it is possible even to make them similar while still maintaining uniqueness, if you are hashing the names, isn't the point of a hash that it is one way and unique?

## Appearance

Generating images that look bad seems subjective but I allowed a few options to be passed in that can alter the appearance such that they can be compared at least to see if one looks better than the other.
Allowing multiple colors is the main way to alter the appearance, and these colors can be a random number of colors or can use a gradient between 2 colors.  If you do not want colors, the image can be generated via just a matrix with binary values as well and would be black and white.  The gradient version does seem the best looking to me but if the colors are too close to one another, I supposed that could be problematic (e.g. black + blue or yellow + white), perhaps the colors should be complimentary or similar but I did not have the time to look into that too deeply.
Along with the coloring, I allowed the image to be symmetric by default but can be turned off if desired.
Seems like the appearance would be nicer if it was less "chaotic" and more "structured" but not sure if I can think of a way off hand to do that (similar to the github repo linked above) while still maintaining uniqueness.

# Original Plan

I first thought I could generate a matrix using N colors from the binary digest/hash, but as I started implementing, I realized that might not be straightforward as the matrix needs to correspond to the binary digest length. So the number of elements for the matrix needs to be 256 for the sha256 hash, which means if I had created a matrix with the width as 2 * height, it might not work out without considering more details.  Instead I changed things a bit to use a standardized size (16x16) which corresponds to the hash length and then just make the actual layout altered during the image creation (e.g. symmetric or not).  I am guessing there is a way to do the matrix size as variable while considering the number of colors such that the matrix maintains uniqueness for all hashes but I can think of a few edge cases that add complexity to that and just wanted to get this done today.


# original info

```markdown
Users often work collaboratively in digital environments where a profile picture is not available. Some platforms have attempted to solve this problem with the creation of randomly generated, unique icons for each user ([github](https://github.blog/2013-08-14-identicons/), [slack](https://slack.zendesk.com/hc/article_attachments/360048182573/Screen_Shot_2019-10-01_at_5.08.29_PM.png), [ethereum wallets](https://github.com/ethereum/blockies)) sometimes called *Identicons*. Given an arbitrary string, create an image that can serve as a unique identifier for a user of a B2B productivity app like slack, notion, etc.

**Requirements**

- Define a set of objectives to accomplish with your *identicon.* There's no right or wrong answer here. Here are some hypothetical objectives:
    - Legibility at some scale or set of scales - what sizes should the icon be shown at?
    - Uniqueness vs similarity - should similar strings look similar "John" vs "Jon" or should they be different?
    - Appearance - how do we avoid generating images that look bad?
- Given an arbitrary string, generate an image (as a jpg, gif, png, or in a web page using canvas, webgl, or whatever other display strategy you prefer)
- Images should be reasonably unique, for instance the strings "John", "Jane", and "931D387731bBbC988B31220" should generate three distinct images
- Any languages may be used, any libraries may be used, recommend javascript or python
- Don’t use an existing library! Treat this exercise as if you looked at existing solutions and thought you could do better, and decided to write your own
```
