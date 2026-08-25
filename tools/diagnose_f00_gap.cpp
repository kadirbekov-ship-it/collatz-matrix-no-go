#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <tuple>
#include <vector>

// Finite diagnostic only.  This program searches for the first structural
// separation inside a coefficient box; none of its counts is used as a proof
// of an unbounded statement.  In particular, coordinate comparisons printed
// below may be artifacts of the common ceiling.

using Matrix = std::array<int, 4>;

Matrix multiply(const Matrix& a, const Matrix& b) {
    return {a[0] * b[0] + a[1] * b[2],
            a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2],
            a[2] * b[1] + a[3] * b[3]};
}

bool dominates(const Matrix& a, const Matrix& b) {
    for (int index = 0; index < 4; ++index)
        if (a[index] < b[index]) return false;
    return true;
}

std::array<int, 2> row_multiply(const std::array<int, 2>& row,
                                const Matrix& matrix) {
    return {row[0] * matrix[0] + row[1] * matrix[2],
            row[0] * matrix[1] + row[1] * matrix[3]};
}

bool row_dominates(const std::array<int, 2>& left,
                   const std::array<int, 2>& right) {
    return left[0] >= right[0] && left[1] >= right[1];
}

int main(int argc, char** argv) {
    const int bound = argc >= 2 ? std::stoi(argv[1]) : 2;
    const std::string fixed_mode = argc >= 3 ? argv[2] : "";
    const bool fixed_lower = fixed_mode == "--fixed-lower";
    const bool fixed_full = fixed_mode == "--fixed-full";
    const bool fixed_projection = fixed_mode == "--fixed-projection";
    const bool fixed_idempotent_upper = fixed_mode == "--fixed-idempotent-upper";
    const bool fixed_idempotent_lower = fixed_mode == "--fixed-idempotent-lower";
    std::vector<Matrix> matrices;
    for (int m00 = 1; m00 <= bound; ++m00)
        for (int m01 = 0; m01 <= bound; ++m01)
            for (int m10 = 0; m10 <= bound; ++m10)
                for (int m11 = 0; m11 <= bound; ++m11)
                    matrices.push_back({m00, m01, m10, m11});

    std::uint64_t carry_cores = 0;
    std::uint64_t f00_gap_cores = 0;
    std::uint64_t left_extendible = 0;
    std::uint64_t right_extendible = 0;
    std::uint64_t both_extendible = 0;
    std::map<std::tuple<int, int, int>, std::uint64_t> separation;
    std::map<int, std::uint64_t> left_row_masks;
    std::map<int, std::uint64_t> left_one_coordinate_masks;
    std::map<int, std::uint64_t> first_column_comparisons;
    std::map<int, std::uint64_t> lower_triangular_cone_masks;
    std::map<int, std::uint64_t> lower_triangular_spectral_masks;
    std::map<int, std::uint64_t> lower_triangular_tf_trace_signs;
    std::map<int, std::uint64_t> lower_triangular_zd_signs;
    std::map<Matrix, std::uint64_t> fixed_t_patterns;

    for (const Matrix& f : matrices) {
        if (f[3] != 0) continue;
        if (!fixed_projection && !fixed_idempotent_upper
            && !fixed_idempotent_lower && f[0] < 2) continue;
        if (fixed_lower && f != Matrix{2, 0, 1, 0}) continue;
        if (fixed_full && f != Matrix{2, 1, 1, 0}) continue;
        if (fixed_projection && f != Matrix{1, 0, 0, 0}) continue;
        if (fixed_idempotent_upper && f != Matrix{1, 1, 0, 0}) continue;
        if (fixed_idempotent_lower && f != Matrix{1, 0, 1, 0}) continue;
        for (const Matrix& t : matrices) {
            for (const Matrix& zero : matrices) {
                if (!dominates(multiply(f, zero), multiply(zero, f))) continue;
                for (const Matrix& one : matrices) {
                    if (!dominates(multiply(f, one), multiply(zero, t))) continue;
                    if (!dominates(multiply(t, zero), multiply(one, t))) continue;
                    for (const Matrix& two : matrices) {
                        if (!dominates(multiply(f, two), multiply(one, f))) continue;
                        if (!dominates(multiply(t, one), multiply(two, f))) continue;
                        if (!dominates(multiply(t, two), multiply(two, t))) continue;
                        ++carry_cores;
                        ++f00_gap_cores;
                        if (fixed_lower || fixed_full) ++fixed_t_patterns[t];
                        if (fixed_full && bound <= 3) {
                            auto print_matrix = [](const Matrix& matrix) {
                                std::cout << matrix[0] << ',' << matrix[1] << ','
                                          << matrix[2] << ',' << matrix[3];
                            };
                            std::cout << "core F=";
                            print_matrix(f);
                            std::cout << " T=";
                            print_matrix(t);
                            std::cout << " Z=";
                            print_matrix(zero);
                            std::cout << " O=";
                            print_matrix(one);
                            std::cout << " D=";
                            print_matrix(two);
                            std::cout << "\n";
                        }
                        int first_column_mask = 0;
                        if (one[0] <= f[0]) first_column_mask |= 1;
                        if (one[2] <= f[2]) first_column_mask |= 2;
                        if (one[0] <= f[0] * f[0] + f[1] * f[2])
                            first_column_mask |= 4;
                        if (one[2] <= f[2] * f[0]) first_column_mask |= 8;
                        ++first_column_comparisons[first_column_mask];
                        if (f[1] == 0 && f[2] > 0) {
                            int cone_mask = 0;
                            if (t[2] <= f[2] * t[0]) cone_mask |= 1;
                            if (t[2] + f[2] * t[3]
                                <= f[2] * (t[0] + f[2] * t[1]))
                                cone_mask |= 2;
                            ++lower_triangular_cone_masks[cone_mask];
                            const int u = f[0];
                            int spectral_mask = 0;
                            if (t[0] <= u && t[3] <= u)
                                spectral_mask |= 1;
                            if (t[0] <= u && t[3] <= u
                                && (u - t[0]) * (u - t[3]) >= t[1] * t[2])
                                spectral_mask |= 2;
                            if (u * t[0] + f[2] * t[1] <= u * u)
                                spectral_mask |= 4;
                            ++lower_triangular_spectral_masks[spectral_mask];
                            const int tf_trace = u * t[0] + f[2] * t[1];
                            ++lower_triangular_tf_trace_signs[
                                (tf_trace > u * u) - (tf_trace < u * u)];
                            ++lower_triangular_zd_signs[
                                (zero[0] > two[0]) - (zero[0] < two[0])];
                        }

                        bool has_left = false;
                        bool has_right = false;
                        int aggregate_left_mask = 0;
                        const Matrix f_squared = multiply(f, f);
                        const Matrix f_times_t = multiply(f, t);
                        for (int a = 1; a <= bound; ++a) {
                            for (int b = 1; b <= bound; ++b) {
                                if (a * f[1] >= b) continue;
                                const std::array<int, 2> ell{a, b};
                                int mask = 0;
                                if (row_dominates(row_multiply(ell, zero),
                                                  row_multiply(ell, t)))
                                    mask |= 1;
                                if (row_dominates(row_multiply(ell, one),
                                                  row_multiply(ell, f_squared)))
                                    mask |= 2;
                                const auto left_one = row_multiply(ell, one);
                                const auto left_f_squared = row_multiply(ell, f_squared);
                                int left_one_mask = 0;
                                if (left_one[0] >= left_f_squared[0]) left_one_mask |= 1;
                                if (left_one[1] >= left_f_squared[1]) left_one_mask |= 2;
                                ++left_one_coordinate_masks[left_one_mask];
                                if (row_dominates(row_multiply(ell, two),
                                                  row_multiply(ell, f_times_t)))
                                    mask |= 4;
                                aggregate_left_mask |= mask;
                                if (mask == 7) has_left = true;
                            }
                        }
                        ++left_row_masks[aggregate_left_mask];
                        for (const Matrix& left : matrices) {
                            const std::array<int, 2> ell{left[0], left[1]};
                            if (left[1] == 0 || left[0] * f[1] >= left[1]) continue;
                            if (!dominates(multiply(left, zero), multiply(left, t))) continue;
                            if (!dominates(multiply(left, one), multiply(multiply(left, f), f))) continue;
                            if (!dominates(multiply(left, two), multiply(multiply(left, f), t))) continue;
                            // Defensive first-row check: this is the exact region R.
                            if (row_dominates(row_multiply(ell, f), ell)) continue;
                            has_left = true;
                            break;
                        }
                        for (const Matrix& right : matrices) {
                            if (!dominates(multiply(f, right), right)) continue;
                            if (!dominates(multiply(t, right), multiply(two, right))) continue;
                            has_right = true;
                            break;
                        }
                        if (has_left) ++left_extendible;
                        if (has_right) ++right_extendible;
                        if (has_left && has_right) ++both_extendible;
                        ++separation[{f[1] > 0, f[2] > 0,
                                      (has_left ? 1 : 0) + (has_right ? 2 : 0)}];
                    }
                }
            }
        }
    }

    std::cout << "bound=" << bound << " matrices=" << matrices.size()
              << " carry_cores=" << carry_cores
              << " f00_gap_cores=" << f00_gap_cores
              << " left_extendible=" << left_extendible
              << " right_extendible=" << right_extendible
              << " both_extendible=" << both_extendible << "\n";
    for (const auto& [key, count] : separation) {
        const auto [p_positive, r_positive, extension_mask] = key;
        std::cout << "p=" << p_positive << " r=" << r_positive
                  << " mask=" << extension_mask << " count=" << count << "\n";
    }
    for (const auto& [mask, count] : left_row_masks)
        std::cout << "aggregate-left-row-mask=" << mask
                  << " count=" << count << "\n";
    for (const auto& [mask, count] : left_one_coordinate_masks)
        std::cout << "left-one-coordinate-mask=" << mask
                  << " count=" << count << "\n";
    for (const auto& [mask, count] : first_column_comparisons)
        std::cout << "first-column-mask=" << mask
                  << " count=" << count << "\n";
    for (const auto& [mask, count] : lower_triangular_cone_masks)
        std::cout << "lower-triangular-cone-mask=" << mask
                  << " count=" << count << "\n";
    for (const auto& [mask, count] : lower_triangular_spectral_masks)
        std::cout << "lower-triangular-spectral-mask=" << mask
                  << " count=" << count << "\n";
    for (const auto& [sign, count] : lower_triangular_tf_trace_signs)
        std::cout << "lower-triangular-tf-trace-sign=" << sign
                  << " count=" << count << "\n";
    for (const auto& [sign, count] : lower_triangular_zd_signs)
        std::cout << "lower-triangular-zd-sign=" << sign
                  << " count=" << count << "\n";
    if (fixed_lower || fixed_full)
        for (const auto& [t, count] : fixed_t_patterns)
            std::cout << "T=" << t[0] << ',' << t[1] << ','
                      << t[2] << ',' << t[3] << " count=" << count << "\n";
    return both_extendible == 0 ? 0 : 1;
}
