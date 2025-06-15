# Class / Struct Definitions
## struct `Polyhedron`
A struct representing the structure of a polyhedron.
| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `num_faces` | `int` | Number of faces in the polyhedron. |  |
| `gon_list` | `std::vector<int>` | Number of edges (gon) for each face. |  |
| `adj_edges` | `std::vector<std::vector<int>>` | List of edge IDs per face. | Stored in counterclockwise order with respect to the outward normal. |
| `adj_faces` | `std::vector<std::vector<int>>` | List of adjacent face IDs per face. | Aligned with `adj_edges`. |

## struct `UnfoldedFace`
A struct that stores information of a face after it has been unfolded in the plane.

| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `face_id` | `int` | ID of the face. |  |
| `gon` | `int` | Number of edges (gon) of the face. |  |
| `edge_id` | `int` | ID of the edge that is connected to the previous unfolded face in the unfolding. | Set to `-1` for the initial face. |
| `x` | `double` | X-coordinate of the face center in the unfolding. | Approximate value. Set to `0.0` for the initial face. |
| `y` | `double` | Y-coordinate of the face center in the unfolding. | Approximate value. Set to `0.0` for the initial face. |
| `angle` | `double` | Orientation angle (in degree) from the center of this face to the center of the previously unfolded face. | Approximate value. Normalized to the range `[-180, 180]`. For the initial face, set to `-180`. |

## struct `UnfoldingState`
A struct representing the current state of the unfolding process at a recursive step.
| Variable Name | Type | Description | Note |
| --- | --- | --- | --- |
| `current_face_id` | `int` | ID of the face currently being placed. | In other words, the base of the current unfolding step. |
| `pivot_edge_id` | `int` | ID of the edge used as the pivot for unfolding from the previous face. | Set to `-1` for the initial face. |
| `x` | `double` | X-coordinate of the center of the current face. | Approximate value. Set to `0.0` for the initial face. |
| `y` | `double` | Y-coordinate of the center of the current face. | Approximate value. Set to `0.0` for the initial face. |
| `angle` | `double` | Orientation angle pointing opposite to the unfolding direction. | Approximate value. Normalized to the range `[-180, 180]`. For the initial face, set to `-180`. |
| `face_usage` | `std::vector<bool>` | A boolean vector indicating whether each face has not yet been unfolded (true if unused). | Size equals the total number of faces. |
| `unfolding_sequence` | `std::vector<UnfoldedFace>` | List of faces that have already been unfolded before the current one. | Does not include the current face. |
| `remaining_distance` | `double` |  Sum of the diameters of the circumscribed circle of all unused faces (including the current face). | Used for pruning. |
| `symmetry_enabled` | `bool` | Whether symmetric pruning is enabled. |  |
| `y_moved_off_axis` | `bool` | Whether the y-coordinate has ever been non-zero since the base face. | Only used if `symmetry_enabled` is true. |
