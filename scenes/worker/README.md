A scene contains some `Entity`s.

Every `Entity` has a `render(self) -> Mobject` method.
This will often involve calling `render()` on child entities.

When an `Entity` is created, it does `self.mobj = self.render()`.

Thereafter, `self.mobj` is typically never replaced.
Instead, the entity's visual representation is updated via `render_to_scene()`:
```python
def render_to_scene(self):
    self.mobj.become(self.render().move_to(self.mobj))
```

To start an animation, create some entities (`scene.entities`) and add their `Mobjects` to the scene.

Then, we enter an update loop.