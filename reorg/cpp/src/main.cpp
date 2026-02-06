// ============================================================================
// main.cpp
// ============================================================================
//
// What this file does:
//   CLI entry point for the rotational unfolding algorithm.
//   Parses command-line arguments, loads input data, runs the search,
//   and outputs results in JSONL format.
//
// このファイルの役割:
//   回転展開アルゴリズムのCLI入口点。
//   コマンドライン引数を解析し、入力データを読み込み、探索を実行し、
//   結果をJSONL形式で出力する。
//
// Responsibility in the project:
//   - Parses CLI arguments (--adj, --base, --symmetric, --out)
//   - Loads polyhedron data using IOUtil
//   - Invokes RotationalUnfolding for each base pair
//   - Manages output streams (stdout or file)
//   - Reports progress to stderr
//   - Does NOT contain algorithm logic
//
// プロジェクト内での責務:
//   - CLI引数を解析（--adj, --base, --symmetric, --out）
//   - IOUtil を使用して多面体データを読み込み
//   - 各 base pair について RotationalUnfolding を呼び出し
//   - 出力ストリームを管理（stdout またはファイル）
//   - 進捗を stderr に報告
//   - アルゴリズムロジックは含まない
//
// Phase 1 における位置づけ:
//   User-facing CLI for Phase 1. This is the executable that external
//   researchers will invoke to generate raw.jsonl output.
//   Phase 1のユーザー向けCLI。外部研究者が raw.jsonl 出力を生成するために
//   呼び出す実行ファイルである。
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
    std::string adj_path;       // Path to the .adj file
    std::string base_path;      // Path to the .base file
    std::string symmetric_mode; // Symmetry mode: "auto", "on", or "off"
    std::string out_path;       // Output file path (empty = stdout)

    bool valid = false;         // Whether parsing succeeded
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
    std::cerr << "Usage: " << program_name << " --adj PATH --base PATH --symmetric auto|on|off [--out PATH]\n";
    std::cerr << "\n";
    std::cerr << "Options:\n";
    std::cerr << "  --adj PATH          Path to the .adj file (polyhedron adjacency data)\n";
    std::cerr << "  --base PATH         Path to the .base file (base face-edge pairs)\n";
    std::cerr << "  --symmetric MODE    Symmetry mode: auto (from filename), on, or off\n";
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
//   - Validates required arguments (--adj, --base, --symmetric)
//   - Validates symmetric_mode is one of: auto, on, off
//   - Writes error messages to stderr on failure
//   - No side effects beyond stderr output
//
// 保証:
//   - 必須引数（--adj, --base, --symmetric）を検証
//   - symmetric_mode が auto, on, off のいずれかであることを検証
//   - 失敗時に stderr にエラーメッセージを書き込み
//   - stderr 出力以外の副作用はない
//
// ----------------------------------------------------------------------------
CliArgs parseArgs(int argc, char* argv[]) {
    CliArgs args;
    args.symmetric_mode = "auto";  // Default value

    if (argc < 7) {  // Minimum: program --adj PATH --base PATH --symmetric MODE
        return args;
    }

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "--adj" && i + 1 < argc) {
            args.adj_path = argv[++i];
        }
        else if (arg == "--base" && i + 1 < argc) {
            args.base_path = argv[++i];
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
    if (args.adj_path.empty() || args.base_path.empty()) {
        std::cerr << "Error: --adj and --base are required\n";
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
//   - Loads polyhedron data from .adj and .base files
//   - Executes rotational unfolding for all base pairs
//   - Outputs JSONL records for all candidate partial unfoldings
//   - Flushes output after each base pair for safety
//
// 保証:
//   - CLI引数を解析
//   - .adj および .base ファイルから多面体データを読み込み
//   - すべての base pair について回転展開を実行
//   - すべての候補部分展開図についてJSONLレコードを出力
//   - 安全のために各 base pair 後に出力をフラッシュ
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
    // Load polyhedron data
    // 多面体データを読み込み
    // ------------------------------------------------------------------------
    Polyhedron poly;
    if (!IOUtil::loadPolyhedronFromFile(args.adj_path, poly)) {
        return 1;
    }

    // ------------------------------------------------------------------------
    // Load base pairs
    // base pairs を読み込み
    // ------------------------------------------------------------------------
    std::vector<std::pair<int, int>> base_pairs;
    if (!IOUtil::loadBasePairsFromFile(args.base_path, base_pairs)) {
        return 1;
    }

    // ------------------------------------------------------------------------
    // Determine symmetry setting
    // 対称性設定を決定
    // ------------------------------------------------------------------------
    bool symmetric = false;
    if (args.symmetric_mode == "auto") {
        symmetric = IOUtil::isSymmetricFromFilename(args.adj_path);
        std::cerr << "Info: Symmetric mode (auto): " << (symmetric ? "on" : "off") << "\n";
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
    // Execute rotational unfolding for all base pairs
    // すべての base pairs について回転展開を実行
    // ------------------------------------------------------------------------
    const int total = base_pairs.size();
    std::cerr << "Info: Processing " << total << " base pairs...\n";

    for (int current = 0; current < total; ++current) {
        const auto& [face, edge] = base_pairs[current];

        // Report progress every 10 pairs, and always report first and last
        // 10ペアごとに進捗を報告し、最初と最後は必ず報告
        if ((current + 1) % 10 == 0 || current == 0 || current == total - 1) {
            std::cerr << "Info: Processing " << (current + 1) << "/" << total << "\n";
        }

        RotationalUnfolding rot_ufd(poly, face, edge, symmetric, symmetric);
        rot_ufd.runRotationalUnfolding(*output);

        // Flush output after each base pair for safety
        // 安全のために各 base pair 後に出力をフラッシュ
        output->flush();
    }

    std::cerr << "Info: Done. Processed " << total << " base pairs.\n";

    return 0;
}
