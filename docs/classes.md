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
| `x` | `double` | X-coordinate of the face center in the unfolding (approximate value). | Set to `0.0` for the initial face. |
| `y` | `double` | Y-coordinate of the face center in the unfolding (approximate value). | Set to `0.0` for the initial face. |
| `angle` | `double` | Orientation angle from the center of this face to the center of the previously unfolded face, normalized to the range `[-180, 180]`. | For the initial face, set to `-180`. |

