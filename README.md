# textchart

Dead-simple tools for generating pure-text bargraphs and scatterplots

## Usage

```
>>> from textchart import textchart
>>> data1 = {"bees": 5, "fish": 30, "highway": 6}
>>> textchart.print_graph(data1)
┌──────────────────────────────────────────────────────┐
│    bees: ■■■■■■ 5                                    │
│    fish: ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 30 │
│ highway: ■■■■■■■■ 6                                  │
└──────────────────────────────────────────────────────┘
>>> data2 = [(1,3), (4,6), (4,6), (10, 5)]
>>> textchart.print_graph(data2)
┌──────────────────────────────────────────────────────────────────────┐
│   6.3┨                                             ┌───────────────┐ │
│      ┃              *                              │ "x": 1 point  │ │
│      ┃                                             │ "*": 2 points │ │
│      ┃                                             └───────────────┘ │
│   4.6┨                                    x                          │
│      ┃                                                               │
│      ┃                                                               │
│      ┃                                                               │
│   2.9┨   x                                                           │
│      ┃                                                               │
│      ┃                                                               │
│      ┃                                                               │
│   1.3┨                                                               │
│      ┃                                                               │
│      ┃                                                               │
│      ┃                                                               │
│   0.0╄━━━━━━┯━━━━━━━━┯━━━━━━━━┯━━━━━━━━┯━━━━━━━┯                     │
│      0.0    1.6      4.1      6.5      9.0     11.2                  │
│                                                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Utility Objects

FORMATTERS
  - `FORMATTER.num`: round to the nearest .1
  - `FORMATTER.round`: round to the nearest integer

SCALE FUNCTIONS
  - `SCALE_FN.linear`: linear scale axis
  - `SCALE_FN.log`: log scale axis

SORTING FUNCTIONS
  - `SORTER.default`: keeps order from iterating through label_value_pairs
  - `SORTER.identity`: default python sorting
  - `SORTER.alphabetical`: sort alphabetically
  - `SORTER.lookup_list(l)`: creates a sort function that preserves the order in list `l`


## API

### Functions
#### __add_border__
    (
    string,
    max_width=None,
    fit=False,
    box_chars='│┐└┘┌─',
    bold=False
    )

__Parameters:__
  - `string`: the string
  - `max_width`: if set, text will wrap if it exceeds a given width.
    - defaults to `80`
  - `fit`: if True, the border will be fit tightly to the text. If False, the border will have width max_width.
    - defaults to `False`
  - `box_chars`: the text symbols for horizontal, top-right, bottom-left, bottom-right, top-left, and vertical border parts.
    - defaults to `│┐└┘┌─`
  - `bold`: if set, replaces the default box chars `│┐└┘┌─`, with bold glyfs `┃┓┗┛┏━`
    - defaults to `False`

__example:__

    >> add_border("this is a very long test string", max_width=10)

        ┌───────────┐
        │ this is a │
        │ very long │
        │ test      │
        │ string    │
        └───────────┘

#### __bar_graph__
    (
    label_value_pairs,
    filler_char='■',
    sorter=SORTERS.identity,
    max_width=40,
    horizontal=True,
    size_labels=True,
    border=False,
    title=''
    )

__Parameters:__
  - `label_value_pairs`: a list of pairs or a dict mapping labels to values
  - `filler_char`: the character to use as a filler
    - default ■
  - `sorters`: a function that sorts the labels along the axis.
    - default `SORTERS.identity`
  - `horizontal`: sets the orientation of the graph. Currently only horizontal bars are available
    - default True
  - `size_labels`: if true, includes the value as text at the top of each bar
    - default True

__example:__
```
    >> bar_graph({1:17, "2":3, "3 & OTHER": 1, 5: 16})

                1: ■■■■■■■■■■■■■■■■■■■■■■ 17
                2: ■■■■ 3
                3: ■■■■■■■■■■■■■ 10
        3 & OTHER: ■ 1
                5: ■■■■■■■■■■■■■■■■■■■■■ 16
```

#### __scatterplot__
    (
    xy,
    border=False
    glyphs='.x*',
    height=15,
    show_key=True,
    title=None,
    unit_block=' ',
    width=40,
    x_formatter=FORMATTER.num,
    x_label='',
    x_range=None,
    x_scale_fn=SCALE_FN.linear,
    x_ticks=5,
    y_formmatter=FORMATTER.num,
    y_label='',
    y_range=None,
    y_scale_fn=SCALE_FN.linear,
    y_ticks=5,
    )

__Parameters:__
  - `xy`: a set of xy pairs
  - `x_range`: an optional pair setting the maximum and minimum values for the x axis
  - `y_range`: an optional pair setting the maximum and minimum values for the y axis
  - `height`: an optional value setting the height of the y axis
  - `width`: an optional value setting the width of the x axis
  - `x_scale_fn`: an optional scale function, which takes (min_, max_, steps, current_step) as inputs and returns the scalar value of the begginning of that step. SCALE_FN.log is available.
    - Defaults to SCALE_FN.linear
  - `y_scale_fn`: an optional scale function, which takes (min_, max_, steps, current_step) as inputs and returns the scalar value of the begginning of that step. SCALE_FN.log is available.
    - Defaults to SCALE_FN.linear
  - `x_label`: the label for the x axis
  - `y_label`: the label for the y axis
  - `glyphs`: a set of symbols to use to represent overlapping points.
    - defaults to ".x*"
    - NOTE: on some monitors, `・•●` may improve clarity, but can also cause rendering errors due to variable width characters.
  - `unit_block`: sets the "background" for the chart. Used as the unit for combuting width.
  - `x_ticks`: the number of "ticks" along the x axis
  - `y_ticks`: the number of "ticks" along the y axis
  - `show_key`: self explanatory.

__Example:__
```
    >> # generating some random data
    >> data = [
      (random.normalvariate(50, 5)*random.randint(1,3), random.normalvariate(3, 1))
      for _ in range(400)
      ]
    >> # Plot command:
    >> scatterplot(
          data,
          title='test title',
          x_label='number of X values',
          y_label='number of\nunits of\nY value',
          border=True)

        ┌─────────────────────────────────────────────────────────────────────────────────────┐
        │                                 test title                                          │
        │                                                                                     │
        │            6.7┨                                              ┌────────────────────┐ │
        │               ┃                                              │ ".": 1 - 3 points  │ │
        │               ┃         .       .                            │ "x": 4 - 6 points  │ │
        │               ┃          .        .      . .                 │ "*": 7 - 10 points │ │
        │            4.7┨         .x        . .       ... .            └────────────────────┘ │
        │               ┃        .x.. .    .x. .. ... .. ..                                   │
        │ number of     ┃        .xx.     ....xx... ..........                                │
        │ units of      ┃        .**.  . ....xx......x..x...                                  │
        │  Y value   2.8┨        .**x  .. x.**x......xxx..   .                                │
        │               ┃         **x    . ..*..   x.. x xx...                                │
        │               ┃        ...x     ..*...    ....... . .                               │
        │               ┃        ....     .  . . ..  ....... ..                               │
        │            0.8┨         .         .  .    .    .                                    │
        │               ┃        . .       .  .                                               │
        │               ┃         .        ..          .                                      │
        │               ┃                                                                     │
        │           -0.7╄━━━━━━┯━━━━━━━━┯━━━━━━━━┯━━━━━━━━┯━━━━━━━┯                           │
        │               0.0    30.0     75.1     120.1    165.1   205.2                       │
        │                                                                                     │
        │                      number of X values                                             │
        └─────────────────────────────────────────────────────────────────────────────────────┘
```


