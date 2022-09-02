import math

_DEFAULT_MAX_WIDTH = 80

def add_border(string, max_width=None, fit=False, box_chars="│┐└┘┌─", bold=False):
  """Draw a border around a string

  Parameters:
    string (str): the string
    max_width: if set, text will wrap if it exceeds a given width.
      defaults to `80`
    fit: if True, the border will be fit tightly to the text. If False, the border will have width max_width.
      defaults to `False`
    box_chars: the text symbols for horizontal, top-right, bottom-left, bottom-right, top-left, and vertical border parts.
      defaults to `│┐└┘┌─`
    bold: if set, replaces the default box chars `│┐└┘┌─`, with bold glyfs `┃┓┗┛┏━`
      defaults to `False`
  """
  if type(string) == list:
    string_lines = string
  else:
    string_lines = string.split("\n")
  box = box_chars
  if bold:
    assert box_chars == '│┐└┘┌─', "cannot set both box_chars and bold."
    box="┃┓┗┛┏━"
  if max_width is None:
    width=_DEFAULT_MAX_WIDTH
  else:
    width = max_width
  if fit:
    wrap_width = max([len(l) for l in string_lines]) + 1
    if max_width is not None:
      width = min(wrap_width, max_width)
    else:
      width = wrap_width
  lines = []
  for line in string_lines:
    words = line.split(" ")
    cur = ''
    for word in words:
      if len(cur) + len(word) < width:
        cur+= f"{word} "
      else:
        lines.append(cur)
        if len(cur) < width:
          cur = f"{word} "
        else:
          word = word+" "
          for idx in range(0, len(word), width):
            if len(word) > idx + width:
              lines.append(word[idx:idx+width])
            else:
              cur=word[idx:]
    lines.append(cur)
  formatted_lines = [f"{box[4]}{'':{box[5]}<{width+1}}{box[1]}"]
  formatted_lines.extend([f"{box[0]} {line:<{width}}{box[0]}" for line in lines])
  formatted_lines.append(f"{box[2]}{'':{box[5]}<{width+1}}{box[3]}")
  if type(string) == list:
    return formatted_lines
  return '\n'.join(formatted_lines) + "\n"


class SORTER:
  def default(x):
    return 0

  def identity(x):
    return x

  def alphabetical(x):
    return str(x)

  def lookup_list(l):
    def sort_fn(x):
      if x in l:
        return l.index(x)
      else:
        return len(l)+1


def bar_graph(label_value_pairs, filler_char='■', sorter=SORTER.alphabetical,
  max_width=40, horizontal=True,
  size_labels=True, border=False, title=''):
  """Draws a bar graph

  Parameters:
    label_value_pairs: a list of pairs or a dict mapping labels to values
    filler_char: the character to use as a filler
      default ■
    sorters: a function that sorts the labels along the axis.
      default `SORTERS.identity`
    horizontal: sets the orientation of the graph. Currently only horizontal bars are available
      default: True
    size_labels: if true, includes the value as text at the top of each bar
      default: True

  example:
  ```
  bar_graph({1:17, "2":3, "3 & OTHER": 1, 5: 16})

              1: ■■■■■■■■■■■■■■■■■■■■■■ 17
              2: ■■■■ 3
              3: ■■■■■■■■■■■■■ 10
      3 & OTHER: ■ 1
              5: ■■■■■■■■■■■■■■■■■■■■■ 16
  ```
  """
  if not horizontal:
    raise NotImplemented("vertial graphs not implimented in this version")

  if type(label_value_pairs) == dict:
    label_value_pairs = list(label_value_pairs.items())

  to_ret = []
  max_label_width = max(len(str(label)) for label, _ in label_value_pairs)
  max_val = max(value for _, value in label_value_pairs)
  _sorter = lambda label, *_: sorter(label)
  for label, value in sorted(label_value_pairs, key=_sorter):
    value_str = f" {value}" if size_labels else ""
    bar = filler_char * round((max_width/len(filler_char)*value)//max_val)
    to_ret.append(f"{label:>{max_label_width}}: {bar}{value_str}")
  if title:
    to_ret = [f"{title:^{max(map(len,to_ret))}}", ''] + to_ret
  if border:
    to_ret = add_border(to_ret, fit=True)
  return '\n'.join(to_ret)


class SCALE_FN:
  def linear(min_, max_, steps, n):
      # spread = max_ - min_
      # min_ -= spread/steps
      # max_ += spread/steps
      return min_ + n*((max_-min_) / steps)

  def log(min_, max_, steps, n):
      if min_<1:
          rescale = 1-min_
      exp = SCALE_FN.linear(math.log10(min_+rescale), math.log10(max_+rescale), steps, n)
      return (10**exp) - rescale


class FORMATTER:
  def num(x):
    return f"{x:.1f}"

  def int(x):
    return f"{round(x)}"

def _xy_pairs_to_2d_count_array(xy, rows, cols, row_val, col_val):
  counts = []
  # graph as 2d array
  for r in range(rows+1):
    r_val = row_val(r)
    cur_count_row = []
    for c in range(cols):
      count = 0
      c_val = col_val(c)
      for x_, y_ in xy:
        if c_val <= x_ < col_val(c+1):
          if r_val <= y_ < row_val(r+1):
            count += 1
      cur_count_row.append(count)
    counts.append(cur_count_row)
  return counts

def _compute_glyph_thresholds(glyphs, count_array):
  counts = sorted(set(filter(int, sum(count_array, []))))
  assert counts, "no points to render"
  step_size = len(counts) / len(glyphs)
  thresholds = tuple(counts[min(int(i*step_size), len(counts)-1)] for i in range(len(glyphs)))
  print(counts, len(counts), step_size, thresholds)
  return thresholds

def _render_scatter(counts, glyph_lookup, glyph_thresholds):
  to_ret = []
  for row in counts:
    cur_row = ""
    for count in row:
      cur_row += glyph_lookup[sum(count >= threshold for threshold in glyph_thresholds)]
    to_ret.append(''.join(cur_row))
  return to_ret

def _render_key(counts, glyph_lookup, glyph_thresholds):
  glyph_dict = {glyph: [] for glyph in glyph_lookup[1:-1]}
  for row in counts:
    cur_row = ""
    for count in row:
      glyph = glyph_lookup[sum(count >= threshold for threshold in glyph_thresholds)]
      if glyph in glyph_dict:
        glyph_dict[glyph].append(count)
  glyph_vals = sorted((min(g_counts), max(g_counts), glyph) for glyph, g_counts in glyph_dict.items() if g_counts)
  to_ret = []
  cur=None
  for min_, max_, glyph in glyph_vals:
    if cur==min_:
      continue
    cur = min_
    if min_ != max_:
      to_ret.append(f'"{glyph}": {min_} - {max_} points')
    else:
      to_ret.append(f'"{glyph}": {max_} point{"" if max_==1 else "s"}')
  return to_ret

def _combine_str_arrays(a, b, justify=">", margin=0):
  assert len(a) == len(b), f"arrays must be of equal length. a:{len(a)} b:{len(b)}"
  max_len = max(len(aa) for aa in a) + margin
  return [f"{aa:{justify}{max_len}}{bb}" for aa, bb in zip(a, b)]

def _add_axis(scatter, x_ticks, y_ticks, row_val, col_val, x_formatter, y_formmatter, unit_block):
  to_ret = []
  y_labels = []
  rows = len(scatter)
  for r, row_str in enumerate(scatter):
    r_val = row_val(r)
    if r == len(scatter)-1 or (r!=0 and r in range(rows-1, 0, -len(scatter)//y_ticks)):
      y_labels.append(r_val)
    else:
      y_labels.append(None)
  y_axis = [y_formmatter(row_val(0))] + [y_formmatter(y_label) if y_label is not None else '' for y_label in y_labels]
  y_bar = ["┨" if y_label is not None else '┃' for y_label in y_labels]

  scatter_with_ybar = _combine_str_arrays(y_bar, scatter)

  x_labels = []
  cols = len(scatter_with_ybar[0])
  for c in range(cols):
    c_val = col_val(c)
    if c in range(cols+1, 0, -cols//x_ticks):
      x_labels.append(c_val)
    else:
      x_labels.append(None)
  x_labels.append(col_val(cols))
  x_labels = [col_val(0)] + x_labels
  x_bar = "╄" + ''.join("━┯"[x_label is not None] for x_label in x_labels[1:])
  x_axis = [' ' * len(x_labels), ' ' * len(x_labels), ' ' * len(x_labels)]
  for i, x_label in enumerate(x_labels):
    if x_label is not None:
      x_str = x_formatter(x_label)
      for col in range(3):
        cur = x_axis[col]
        if any(ch != ' ' for ch in cur[i:len(x_str)]):
          continue
        x_axis[col] = f"{cur[:i]}{x_str}{cur[i+len(x_str):]}"
        break
  x_axis = [line for line in x_axis if any(ch != ' ' for ch in line)]

  scatter_xy = x_axis + [x_bar] + scatter_with_ybar
  y_axis = ['' for _ in x_axis] + y_axis
  return _combine_str_arrays(y_axis, scatter_xy)


def _expand_range(l):
  min_ = min(l)
  max_ = max(l)
  spread = max_ - min_
  min_-=spread/10
  max_+=spread/10
  min_ = min(min_, 0)
  return min_, max_

def scatterplot(
  xy, x_range=None, y_range=None, height=15, width=40,
  y_scale_fn=SCALE_FN.linear, x_scale_fn=SCALE_FN.linear,
  x_label="", y_label="", glyphs=".x*", unit_block=' ',
  x_ticks=5, y_ticks=5, x_formatter=FORMATTER.num, y_formmatter=FORMATTER.num,
  show_key=True, title=None, border=False):
  """ Draw a scatterplot
  Parameters:
    xy: a set of xy pairs
    x_range: an optional pair setting the maximum and minimum values for the x axis
    y_range: an optional pair setting the maximum and minimum values for the y axis
    height: an optional value setting the height of the y axis
    width: an optional value setting the width of the x axis
    x_scale_fn: an optional scale function, which takes (min_, max_, steps, current_step) as inputs and
      returns the scalar value of the begginning of that step. SCALE_FN.log is available.
      Defaults to SCALE_FN.linear
    y_scale_fn: an optional scale function, which takes (min_, max_, steps, current_step) as inputs and
      returns the scalar value of the begginning of that step. SCALE_FN.log is available.
      Defaults to SCALE_FN.linear
    x_label: the label for the x axis
    y_label: the label for the y axis
    glyphs: a set of symbols to use to represent overlapping points.
      defaults to ".x*"
      on some monitors, `・•●` may improve clarity, but can run into variable width issues.
    unit_block: sets the "background" for the chart. Used as the unit for combuting width.
    x_ticks: the number of "ticks" along the x axis
    y_ticks: the number of "ticks" along the y axis
    show_key: self explanatory.

  Example:
    random_tuples = [(random.normalvariate(50, 5)*random.randint(1,3), random.normalvariate(3, 1)) for _ in range(400)]
    scatterplot(
        random_tuples,
        title='test title', x_label='number of X values', y_label='number of\nunits of Y value', border=True)

    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                         test title                                          │
    │                                                                                             │
    │                    6.7┨                                              ┌────────────────────┐ │
    │                       ┃                                              │ ".": 1 - 3 points  │ │
    │                       ┃         .       .                            │ "x": 4 - 6 points  │ │
    │                       ┃          .        .      . .                 │ "*": 7 - 10 points │ │
    │                    4.7┨         .x        . .       ... .            └────────────────────┘ │
    │                       ┃        .x.. .    .x. .. ... .. ..                                   │
    │     number of         ┃        .xx.     ....xx... ..........                                │
    │  units of Y value     ┃        .**.  . ....xx......x..x...                                  │
    │                    2.8┨        .**x  .. x.**x......xxx..   .                                │
    │                       ┃         **x    . ..*..   x.. x xx...                                │
    │                       ┃        ...x     ..*...    ....... . .                               │
    │                       ┃        ....     .  . . ..  ....... ..                               │
    │                    0.8┨         .         .  .    .    .                                    │
    │                       ┃        . .       .  .                                               │
    │                       ┃         .        ..          .                                      │
    │                       ┃                                                                     │
    │                   -0.7╄━━━━━━┯━━━━━━━━┯━━━━━━━━┯━━━━━━━━┯━━━━━━━┯                           │
    │                       0.0    30.0     75.1     120.1    165.1   205.2                       │
    │                                                                                             │
    │                              number of X values                                             │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘

  """

  # Setup
  x = [x for x, _ in xy]
  y = [y for _, y in xy]
  if x_range == None:
    x_range = _expand_range(x)
  if y_range == None:
    y_range = _expand_range(y)
  assert x_range[1] > x_range[0], "x_range must increase"
  assert y_range[1] > y_range[0], "y_range must increase"

  def row_val(r_idx):
    return y_scale_fn(y_range[0], y_range[1], height, r_idx)
  def col_val(c_idx):
    return x_scale_fn(x_range[0], x_range[1], width, c_idx)

  plot_rows = []

  counts = _xy_pairs_to_2d_count_array(xy, height, width, row_val, col_val)
  glyph_thresholds = _compute_glyph_thresholds(glyphs, counts)

  glyph_lookup = [unit_block] + list(glyphs) + [unit_block]
  scatter = _render_scatter(counts, glyph_lookup, glyph_thresholds)

  axis_graph = _add_axis(scatter, x_ticks, y_ticks, row_val, col_val, x_formatter, y_formmatter, unit_block)
  axis_graph = list(reversed(axis_graph))

  base_label=[''] + [f"{s:^{width}}" for s in x_label.split("\n")]

  axis_graph = axis_graph + base_label

  side_label_text = y_label.split("\n")
  side_label_spacer_height = (height-len(side_label_text))//2
  side_label = ['' for _ in range(len(axis_graph))]
  side_label[side_label_spacer_height:side_label_spacer_height+len(side_label_text)] = side_label_text
  axis_graph = _combine_str_arrays(side_label, axis_graph, justify='^', margin=2)

  to_render = axis_graph
  if show_key:
    key = add_border(_render_key(counts, glyph_lookup, glyph_thresholds), fit=True)
    to_render = _combine_str_arrays(to_render, key+['' for _ in range(len(to_render)-len(key))], justify="<")
  if title:
    to_render = [f"{title:^{len(to_render[0])}}", ''] + to_render
  if border:
    to_render = add_border(to_render, fit=True)
  to_ret ="\n".join(map(lambda s: s.rstrip(), to_render))
  return to_ret