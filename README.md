A toolkit for creating animations explaining Temporal.

- [`schema/`](schema/) defines a schema describing actor state changes and messages passing between actors.

- [`manim_renderer/`](manim_renderer/) uses [manim](https://github.com/ManimCommunity/manim) to render JSONL data conforming to the schema as an animation.

- [`tempyral/`](tempyral/) is a simulation of Temporal that outputs the JSONL format.

### Example output

https://go.temporal.io/temporal-animations/

### Example usage

```
python scenes/CallActivity.py | manim render --quality h manim_renderer/scene.py TemporalScene
```

To create a new animation illustrating a different aspect of Temporal, take a look at the commits implementing [`SignalWithStart`](https://github.com/temporalio/temporal-animations/commit/5d1b852383c7f1a2a30b25b2a5e607c9cdddeaeb) and [`StartWorkflowAndExecuteUpdate`](https://github.com/temporalio/temporal-animations/commit/b064eeba637aeb577c2850a64b5704aa9d3fd452).

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

To use the command-line utilities in [`bin/`](bin/), install [fzf](https://github.com/junegunn/fzf).
