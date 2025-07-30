#ifndef UNFOLDED_FACE_HPP
#define UNFOLDED_FACE_HPP

// 平面に配置された部分展開図の各面の情報を保持する構造体
// A struct that stores information for each face
// in a partial unfolding placed on the plane.
struct UnfoldedFace {
    // 面の番号
    // ID of the face.
    int face_id;

    // 面の辺の数（何角形か）
    // Number of edges (gon) of the face.
    int gon;

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
};

#endif  // UNFOLDED_FACE_HPP
