# Function Definitions
## module `GeometryUtil`
A header-only utility module providing fundamental geometric functions used throughout the unfolding process.
Functions are defined within the `GeometryUtil` namespace and do not rely on external state.

→ For constants used in these functions (e.g., `PI`, `buffer`), see [constants.md](constants.md).

### Member Functions
| Function Name | Signature | Description |
| --- | --- | --- |
| `getDistanceFromOrigin` | `double getDistanceFromOrigin(double x, double y)` | Returns the Euclidean distance from the origin to the point `(x, y)`. |
| `normalizeAngle` | `void normalizeAngle(double& degree)` | Normalizes the angle to the range `[-180, 180]` degrees. |
| `circumradius` | `double circumradius(int gon)` | Computes the circumradius of a regular polygon with `gon` sides. |
| `inradius` | `double inradius(int gon)` | Computes the inradius of a regular polygon with `gon` sides. |
