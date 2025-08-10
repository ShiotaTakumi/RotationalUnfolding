#ifndef ROTATIONAL_UNFOLDING_FACE_STATE_HPP
#define ROTATIONAL_UNFOLDING_FACE_STATE_HPP

// 現在注目している面の情報を保持する構造体
// A struct that stores information for
// the currently focused face.
struct FaceState {
    // 面の番号
    // ID of the face.
    int face_id;

    // 一つ前に展開された面と接続している辺の番号
    // ID of the edge connected to the previously unfolded face.
    int edge_id;

    // 面の中心の x 座標
    // X-coordinate of the face center.
    double x;

    // 面の中心の y 座標
    // Y-coordinate of the face center.
    double y;

    // 面の中心から、一つ前に展開された面の
    // 中心への角度（度数法）
    // Angle (in degrees) from the center of this face
    // to the center of the previously unfolded face.
    double angle;

    // 現在、部分展開図として使用されていない面
    // （現在注目している面 face_id は含まない）の外接円の合計
    // Sum of the diameters of the circumscribed circles of
    // all faces that are not yet used in the partial unfolding,
    // excluding the current face (face_id).
    double remaining_distance;

    // y 軸対称性に基づく枝刈りを有効にするかどうかのフラグ
    // Flag indicating whether pruning based on
    // y-axis symmetry is enabled.
    bool symmetry_enabled;

    // 新たに展開した面の中心座標が y 軸上以外に
    // なったことがあるかを管理するフラグ
    // symmetry_enabled が true の時にのみ使用
    // Flag indicating whether the center of any newly
    // unfolded face has deviated from the y-axis.
    // Used only when symmetry_enabled is true.
    bool y_moved_off_axis;
};

#endif  // ROTATIONAL_UNFOLDING_FACE_STATE_HPP
