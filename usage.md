# Usage Guide

## Terminal data

## Graphs

There are two options for graphs: absolute and relative. The absolute graph is much faster and it visualizes the change to the total amount of listens of an aspect over time. The relative graph visualizes the change to the proportion of the aspect in regard to the total amount of listens at that point in time.

### Absolute Graphs

```python
d.graph_abs(aspect, name)
```

<details>
<summary>Example</summary>

```python
d.graph_abs("artist", "Sabaton")
```

![Example Absolute Graph featuring Sabaton](img/sabaton-absolute-graph.png "Example Absolute Graph")

</details>

### Relative Graphs

```python
d.graph_rel(aspect, name)
```

<details>
<summary>Example</summary>

```python
d.graph_rel("artist", "Sabaton")
```

![Example Relative Graph featuring Sabaton](img/sabaton-relative-graph.png "Example Relative Graph")

</details>
