# RotationalUnfolding.md

## File Structure
This component is implemented as a collection of C++ header files under `include/rotational_unfolding/`:

- [`RotationalUnfolding.hpp`](../include/rotational_unfolding/RotationalUnfolding.hpp)
  - Defines the `RotationalUnfolding` class, which performs recursive path-shaped edge unfolding and checks for overlaps. Also handles symmetry pruning and search initialization.

- [`Polyhedron.hpp`](../include/rotational_unfolding/Polyhedron.hpp)
  - Defines the `Polyhedron` structure, which stores the adjacency structure of the input polyhedron, including face-edge and face-face relationships.

- [`UnfoldingState.hpp`](../include/rotational_unfolding/UnfoldingState.hpp)
  - Defines the `UnfoldingState` structure, which represents a snapshot of the unfolding process during recursion (position, orientation, remaining radius, symmetry info, etc).

- [`UnfoldedFace.hpp`](../include/rotational_unfolding/UnfoldedFace.hpp)
  - Defines the `UnfoldedFace` structure, which stores the position and rotation of each face after unfolding.

- [`GeometryUtil.hpp`](../include/rotational_unfolding/GeometryUtil.hpp)
  - Provides utility functions and constants (in the `GeometryUtil` namespace) for geometric computation such as distances, angles, and radii.

## Class / Struct Definitions
## class `RotationalUnfolding` [[RotationalUnfolding.hpp](../include/rotational_unfolding/RotationalUnfolding.hpp)]
A class that explores path-shape partial edge unfolding starting from a specified face and edge of a polyhedron, and checks for overlap at both endpoints of each path.

### Public Member Functions
| Function Name | Signature | Description |
| --- | --- | --- |
| `RotationalUnfolding` | `RotationalUnfolding(const Polyhedron& poly, int base_face, int base_edge, bool enable_symmetry, bool y_moved_off_axis)` | Constructor. Prepares the path-shape edge unfolding search from the specified base face and edge. |
| `searchSequence` | `void searchSequence()` | Entry point for launching the recursive search for path-shape edge unfoldings. Internally sets up the first face and delegates to the core search logic. |

### Private Member Variables
| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `polyhedron` | `const Polyhedron&` | Reference to the input polyhedron structure. |  |
| `base_face_id` | `int` | ID of the initial base face used to begin the unfolding. |  |
| `base_edge_id` | `int` | ID of the edge on the base face used as the rotation axis to initiate unfolding. |  |
| `symmetry_enabled` | `bool` | Whether pruning based on symmetry with respect to the y-axis is enabled during the search. |  |
| `y_moved_off_axis` | `bool` | Whether any face has deviated from the y-axis (y ≠ 0) since the base face. | Used only if `symmetry_enabled` is true. |
| `initial_state` | `UnfoldingState` | Initial state of the recursive unfolding process, derived from the face that becomes the new base when rotated around the base edge of the base face. |  |
| `unfolding_sequence` | `std::vector<UnfoldedFace>` | Array storing the current path-shape edge unfolding sequence. |  |

### Private Member Functions
| Function Name | Signature | Description |
| --- | --- | --- |
| `setupInitialState` | `void setupInitialState()` | Computes the initial state after rotating the polyhedron around the base edge used as the unfolding axis. |
| `searchUnfoldingSequence` | `void searchUnfoldingSequence(UnfoldingState state, std::vector<bool>& face_usage, std::ostream& out)` | Recursively searches for path-shape edge unfoldings based on the initial state, checking for overlap along the way and applying symmetry pruning if enabled. |

## struct `Polyhedron` [[Polyhedron.hpp](../include/rotational_unfolding/Polyhedron.hpp)]
A struct representing the structure of a polyhedron.

### Member Variables
| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `num_faces` | `int` | Number of faces in the polyhedron. |  |
| `gon_list` | `std::vector<int>` | Number of edges (gon) for each face. |  |
| `adj_edges` | `std::vector<std::vector<int>>` | List of edge IDs per face. | Stored in counterclockwise order on each face, as viewed from outside the polyhedron. |
| `adj_faces` | `std::vector<std::vector<int>>` | List of adjacent face IDs per face. | Aligned with `adj_edges`. |

### Member Functions
| Function Name | Signature | Description |
| --- | --- | --- |
| `getEdgeIndex` | `int getEdgeIndex(int face_id, int edge_id) const` | Returns the index of `edge_id` in `adj_edges[face_id]`. Returns `-1` if not found.

## struct `UnfoldingState` [[UnfoldingState.hpp](../include/rotational_unfolding/UnfoldingState.hpp)]
A struct representing the current state of the unfolding process at a recursive step.

### Member Variables
| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `face_id` | `int` | ID of the face currently being placed. | In other words, the base of the current unfolding step. |
| `edge_id` | `int` | ID of the edge used as the pivot for unfolding from the previous face. | Set to `-1` for the initial face. |
| `x` | `double` | X-coordinate of the center of the current face. | Approximate value. Set to `0.0` for the initial face. |
| `y` | `double` | Y-coordinate of the center of the current face. | Approximate value. Set to `0.0` for the initial face. |
| `angle` | `double` | Orientation angle pointing opposite to the unfolding direction. | Approximate value. Normalized to the range `[-180, 180]`. For the initial face, set to `-180`. |
| `remaining_distance` | `double` |  Sum of the diameters of the circumscribed circle of all unused faces (including the current face). | Used for pruning. |
| `symmetry_enabled` | `bool` | Whether symmetric pruning is enabled. |  |
| `y_moved_off_axis` | `bool` | Whether the y-coordinate has ever been non-zero since the base face. | Only used if `symmetry_enabled` is true. |

## struct `UnfoldedFace` [[UnfoldedFace.hpp](../include/rotational_unfolding/UnfoldedFace.hpp)]
A struct that stores information of a face after it has been unfolded in the plane.

### Member Variables
| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `face_id` | `int` | ID of the face. |  |
| `gon` | `int` | Number of edges (gon) of the face. |  |
| `edge_id` | `int` | ID of the edge that is connected to the previous unfolded face in the unfolding. | Set to `-1` for the initial face. |
| `x` | `double` | X-coordinate of the face center in the unfolding. | Approximate value. Set to `0.0` for the initial face. |
| `y` | `double` | Y-coordinate of the face center in the unfolding. | Approximate value. Set to `0.0` for the initial face. |
| `angle` | `double` | Orientation angle (in degree) from the center of this face to the center of the previously unfolded face. | Approximate value. Normalized to the range `[-180, 180]`. For the initial face, set to `-180`. |

## Function Definitions
## `GeometryUtil` namespace [[GeometryUtil.hpp](../include/rotational_unfolding/GeometryUtil.hpp)]
A header-only utility module providing fundamental geometric functions used throughout the unfolding process.
Functions are defined within the `GeometryUtil` namespace and do not rely on external state.

### Functions in Namespace
| Function Name | Signature | Description |
| --- | --- | --- |
| `getDistanceFromOrigin` | `double getDistanceFromOrigin(double x, double y)` | Returns the Euclidean distance from the origin to the point `(x, y)`. |
| `normalizeAngle` | `void normalizeAngle(double& degree)` | Normalizes the angle to the range `[-180, 180]` degrees. |
| `circumradius` | `double circumradius(int gon)` | Computes the circumradius of a regular polygon with `gon` sides. |
| `inradius` | `double inradius(int gon)` | Computes the inradius of a regular polygon with `gon` sides. |

## Constants
## `GeometryUtil` namespace [[GeometryUtil.hpp](../include/rotational_unfolding/GeometryUtil.hpp)]
A header-only utility module providing constants used in geometric calculations throughout the unfolding process.
Constants are defined within the `GeometryUtil` namespace and are used by functions such as circumradius, inradius, and geometric pruning checks.

### Constants in Namespace
| Constant Name | Type | Value | Description |
| --- | --- | --- | --- |
| `PI` | `constexpr double` | `3.141592653589793` | Value of π (pi), used in trigonometric calculations. |
| `buffer` | `const double` | `0.01` | A small buffer added to improve numerical stability in overlap detection, preventing false positives due to floating-point errors. |
