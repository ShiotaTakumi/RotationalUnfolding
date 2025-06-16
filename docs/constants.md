# Constants
## module `GeometryUtil`
A header-only utility module providing constants used in geometric calculations throughout the unfolding process.
Constants are defined within the `GeometryUtil` namespace and are used by functions such as circumradius, inradius, and geometric pruning checks.

### Constants in Namespace
| Constant Name | Type | Value | Description |
| --- | --- | --- | --- |
| `PI` | `constexpr double` | `3.141592653589793` | Value of π (pi), used in trigonometric calculations. |
| `buffer` | `const double` | `0.01` | A small buffer added to improve numerical stability in overlap detection, preventing false positives due to floating-point errors. |
