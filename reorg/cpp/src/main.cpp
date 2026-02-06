// ============================================================================
// main.cpp
// ============================================================================
//
// What this file does:
//   CLI entry point for the rotational unfolding algorithm.
//   Parses command-line arguments, loads input data from JSON files,
//   runs the search, and outputs results in JSONL format.
//
// このファイルの役割:
//   回転展開アルゴリズムのCLI入口点。
//   コマンドライン引数を解析し、JSONファイルから入力データを読み込み、
//   探索を実行し、結果をJSONL形式で出力する。
//
// Responsibility in the project:
//   - Parses CLI arguments (--polyhedron, --roots, --symmetric, --out)
//   - Loads polyhedron data from JSON using IOUtil
//   - Invokes RotationalUnfolding for each root pair
//   - Manages output streams (stdout or file)
//   - Reports progress to stderr
//   - Does NOT contain algorithm logic
//
// プロジェクト内での責務:
//   - CLI引数を解析（--polyhedron, --roots, --symmetric, --out）
//   - IOUtil を使用してJSONから多面体データを読み込み
//   - 各 root pair について RotationalUnfolding を呼び出し
//   - 出力ストリームを管理（stdout またはファイル）
//   - 進捗を stderr に報告
//   - アルゴリズムロジックは含まない
//
// Phase 1 における位置づけ:
//   User-facing CLI for Phase 1 with the new JSON input format.
//   This is the executable that external researchers will invoke to generate
//   raw.jsonl output from polyhedron.json and root_pairs.json.
//   Phase 1の新しいJSON入力形式を持つユーザー向けCLI。
//   外部研究者が polyhedron.json と root_pairs.json から raw.jsonl 出力を
//   生成するために呼び出す実行ファイルである。
//
// ============================================================================

#include "RotationalUnfolding.hpp"
#include "IOUtil.hpp"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstring>

// ============================================================================
// CLI Argument Parsing
// ============================================================================

// ----------------------------------------------------------------------------
// CliArgs
// ----------------------------------------------------------------------------
//
// Represents parsed command-line arguments.
// コマンドライン引数の解析結果を表す。
//
// ----------------------------------------------------------------------------
struct CliArgs {
    std::string polyhedron_path; // Path to polyhedron.json
    std::string roots_path;      // Path to root_pairs.json
    std::string symmetric_mode;  // Symmetry mode: "auto", "on", or "off"
    std::string out_path;        // Output file path (empty = stdout)

    bool valid = false;          // Whether parsing succeeded
};

// ----------------------------------------------------------------------------
// printUsage
// ----------------------------------------------------------------------------
//
// Prints usage information to stderr.
// 使用方法を stderr に出力する。
//
// ----------------------------------------------------------------------------
void printUsage(const char* program_name) {
    std::cerr << "Usage: " << program_name << " --polyhedron PATH --roots PATH --symmetric auto|on|off [--out PATH]\n";
    std::cerr << "\n";
    std::cerr << "Options:\n";
    std::cerr << "  --polyhedron PATH   Path to the polyhedron.json file\n";
    std::cerr << "  --roots PATH        Path to the root_pairs.json file\n";
    std::cerr << "  --symmetric MODE    Symmetry mode: auto (from polyhedron name), on, or off\n";
    std::cerr << "  --out PATH          Output file path (optional; stdout if not specified)\n";
    std::cerr << "\n";
    std::cerr << "Output format: JSONL (JSON Lines) - one partial unfolding per line\n";
}

// ----------------------------------------------------------------------------
// parseArgs
// ----------------------------------------------------------------------------
//
// Input:
//   argc : Argument count
//   argv : Argument vector
//
// 入力:
//   argc : 引数の数
//   argv : 引数のベクター
//
// Output:
//   Returns a CliArgs structure with parsed arguments.
//   If parsing fails, CliArgs.valid is false.
//
// 出力:
//   解析された引数を含む CliArgs 構造体を返す。
//   解析が失敗した場合、CliArgs.valid は false。
//
// Guarantee:
//   - Validates required arguments (--polyhedron, --roots, --symmetric)
//   - Validates symmetric_mode is one of: auto, on, off
//   - Writes error messages to stderr on failure
//   - No side effects beyond stderr output
//
// 保証:
//   - 必須引数（--polyhedron, --roots, --symmetric）を検証
//   - symmetric_mode が auto, on, off のいずれかであることを検証
//   - 失敗時に stderr にエラーメッセージを書き込み
//   - stderr 出力以外の副作用はない
//
// ----------------------------------------------------------------------------
CliArgs parseArgs(int argc, char* argv[]) {
    CliArgs args;
    args.symmetric_mode = "auto";  // Default value

    if (argc < 7) {  // Minimum: program --polyhedron PATH --roots PATH --symmetric MODE
        return args;
    }

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "--polyhedron" && i + 1 < argc) {
            args.polyhedron_path = argv[++i];
        }
        else if (arg == "--roots" && i + 1 < argc) {
            args.roots_path = argv[++i];
        }
        else if (arg == "--symmetric" && i + 1 < argc) {
            args.symmetric_mode = argv[++i];
            if (args.symmetric_mode != "auto" &&
                args.symmetric_mode != "on" &&
                args.symmetric_mode != "off") {
                std::cerr << "Error: --symmetric must be auto, on, or off\n";
                return args;
            }
        }
        else if (arg == "--out" && i + 1 < argc) {
            args.out_path = argv[++i];
        }
        else {
            std::cerr << "Error: Unknown argument: " << arg << "\n";
            return args;
        }
    }

    // Check that required arguments are present
    // 必須引数が存在することを確認
    if (args.polyhedron_path.empty() || args.roots_path.empty()) {
        std::cerr << "Error: --polyhedron and --roots are required\n";
        return args;
    }

    args.valid = true;
    return args;
}

// ============================================================================
// Main Entry Point
// ============================================================================

// ----------------------------------------------------------------------------
// main
// ----------------------------------------------------------------------------
//
// Input:
//   argc : Argument count
//   argv : Argument vector
//
// 入力:
//   argc : 引数の数
//   argv : 引数のベクター
//
// Output:
//   Returns 0 on success, 1 on failure.
//   Writes JSONL records to stdout or the specified output file.
//   Writes progress and error messages to stderr.
//
// 出力:
//   成功時は 0、失敗時は 1 を返す。
//   JSONLレコードを stdout または指定された出力ファイルに書き込む。
//   進捗とエラーメッセージを stderr に書き込む。
//
// Guarantee:
//   - Parses CLI arguments
//   - Loads polyhedron data from polyhedron.json and root_pairs.json
//   - Executes rotational unfolding for all root pairs
//   - Outputs JSONL records for all candidate partial unfoldings
//   - Flushes output after each root pair for safety
//
// 保証:
//   - CLI引数を解析
//   - polyhedron.json および root_pairs.json から多面体データを読み込み
//   - すべての root pair について回転展開を実行
//   - すべての候補部分展開図についてJSONLレコードを出力
//   - 安全のために各 root pair 後に出力をフラッシュ
//
// ----------------------------------------------------------------------------
int main(int argc, char* argv[]) {
    // ------------------------------------------------------------------------
    // Parse command-line arguments
    // コマンドライン引数を解析
    // ------------------------------------------------------------------------
    CliArgs args = parseArgs(argc, argv);
    if (!args.valid) {
        printUsage(argv[0]);
        return 1;
    }

    // ------------------------------------------------------------------------
    // Load polyhedron data from JSON
    // JSON から多面体データを読み込み
    // ------------------------------------------------------------------------
    Polyhedron poly;
    if (!IOUtil::loadPolyhedronFromJson(args.polyhedron_path, poly)) {
        return 1;
    }

    // ------------------------------------------------------------------------
    // Load root pairs from JSON
    // JSON から root pairs を読み込み
    // ------------------------------------------------------------------------
    std::vector<std::pair<int, int>> root_pairs;
    if (!IOUtil::loadRootPairsFromJson(args.roots_path, root_pairs)) {
        return 1;
    }

    // ------------------------------------------------------------------------
    // Determine symmetry setting
    // 対称性設定を決定
    // ------------------------------------------------------------------------
    bool symmetric = false;
    if (args.symmetric_mode == "auto") {
        // Extract polyhedron name from JSON and determine symmetry
        // JSON から多面体名を抽出して対称性を判定
        std::string poly_name = IOUtil::extractPolyNameFromJson(args.polyhedron_path);
        if (!poly_name.empty()) {
            symmetric = IOUtil::isSymmetricFromPolyName(poly_name);
            std::cerr << "Info: Polyhedron name: " << poly_name << "\n";
            std::cerr << "Info: Symmetric mode (auto): " << (symmetric ? "on" : "off") << "\n";
        } else {
            std::cerr << "Warning: Could not extract polyhedron name; defaulting to symmetric=off\n";
            symmetric = false;
        }
    }
    else if (args.symmetric_mode == "on") {
        symmetric = true;
        std::cerr << "Info: Symmetric mode: on\n";
    }
    else {
        symmetric = false;
        std::cerr << "Info: Symmetric mode: off\n";
    }

    // ------------------------------------------------------------------------
    // Determine output destination
    // 出力先を決定
    // ------------------------------------------------------------------------
    std::ofstream out_file;
    std::ostream* output = &std::cout;

    if (!args.out_path.empty()) {
        out_file.open(args.out_path);
        if (!out_file) {
            std::cerr << "Error: Cannot open output file: " << args.out_path << "\n";
            return 1;
        }
        output = &out_file;
        std::cerr << "Info: Writing output to: " << args.out_path << "\n";
    }
    else {
        std::cerr << "Info: Writing output to stdout\n";
    }

    // ------------------------------------------------------------------------
    // Execute rotational unfolding for all root pairs
    // すべての root pairs について回転展開を実行
    // ------------------------------------------------------------------------
    const int total = root_pairs.size();
    std::cerr << "Info: Processing " << total << " root pairs...\n";

    for (int current = 0; current < total; ++current) {
        const auto& [face, edge] = root_pairs[current];

        // Report progress every 10 pairs, and always report first and last
        // 10ペアごとに進捗を報告し、最初と最後は必ず報告
        if ((current + 1) % 10 == 0 || current == 0 || current == total - 1) {
            std::cerr << "Info: Processing " << (current + 1) << "/" << total << "\n";
        }

        RotationalUnfolding rot_ufd(poly, face, edge, symmetric, symmetric);
        rot_ufd.runRotationalUnfolding(*output);

        // Flush output after each root pair for safety
        // 安全のために各 root pair 後に出力をフラッシュ
        output->flush();
    }

    std::cerr << "Info: Done. Processed " << total << " root pairs.\n";

    return 0;
}
