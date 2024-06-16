A toolkit for creating animations explaining Temporal.

- [`schema`](schema/) defines a schema describing actor state changes and messages passing between actors.

- [`manim_renderer`](manim_renderer/) uses [manim](https://github.com/ManimCommunity/manim) to render JSONL data conforming to the schema as an animation.

- [`tempyral`](tempyral/) is a simulation of Temporal that outputs the JSONL format.

### Output

https://go.temporal.io/temporal-animations

### Usage

```
python scenes/CallActivity.py | manim render --quality h manim_renderer/temporal_scene.py TemporalScene
```

To create a new animation illustrating a different aspect of Temporal, take a look at the commits implementing [`SignalWithStart`](https://github.com/temporalio/temporal-animations/commit/34f932bf30ff01f123643f569c96127617f5e5a5) and [`StartWorkflowAndExecuteUpdate`](https://github.com/temporalio/temporal-animations/commit/ac4cb605a12cd6acdc7640685262acb7c856a4ca).

### Installation

This project uses typing features requiring Python >= 3.12. Use
[pyenv](https://github.com/pyenv/pyenv) to install the required Python
interpreter version, and use [poetry](https://python-poetry.org/docs/) to manage
the Python virtualenv:

```
# install poetry
brew install pyenv
pyenv install 3.12
pyenv shell 3.12
poetry install
poetry shell
```

To use the command-line utilities in [`bin`](bin/), install [fzf](https://github.com/junegunn/fzf).
