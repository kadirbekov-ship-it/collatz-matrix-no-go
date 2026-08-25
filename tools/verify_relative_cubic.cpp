#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <tuple>
#include <vector>

using Matrix = std::array<int, 4>;
using Word = std::vector<int>;
using Row = std::array<int, 14>;
using Rows = std::array<Row, 22>;
using Term = std::tuple<int, int, int>;
using Template = std::vector<Term>;

struct Rule { Word lhs; Word rhs; };

// Symbols: f,t,0,1,2,<,>.  Rules: dynamic-even, dynamic-odd,
// carry-f0..carry-f2, carry-t0..carry-t2, left-0..left-2.
const std::vector<Rule> RULES = {
    {{0,6},{6}}, {{1,6},{4,6}}, {{0,2},{2,0}}, {{0,3},{2,1}},
    {{0,4},{3,0}}, {{1,2},{3,1}}, {{1,3},{4,0}}, {{1,4},{4,1}},
    {{5,2},{5,1}}, {{5,3},{5,0,0}}, {{5,4},{5,0,1}},
};

Matrix multiply(const Matrix& a, const Matrix& b) {
    return {a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
            a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3]};
}

bool dominates(const Matrix& a, const Matrix& b) {
    for (int i=0; i<4; ++i) if (a[i] < b[i]) return false;
    return true;
}

std::array<Row,2> offsets(const Word& word, const std::array<Matrix,7>& matrices) {
    std::array<Row,2> result{};
    Matrix prefix{1,0,0,1};
    for (int symbol : word) {
        result[0][2*symbol] += prefix[0];
        result[0][2*symbol+1] += prefix[1];
        result[1][2*symbol] += prefix[2];
        result[1][2*symbol+1] += prefix[3];
        prefix = multiply(prefix, matrices[symbol]);
    }
    return result;
}

Rows inequality_rows(const std::array<Matrix,7>& matrices) {
    Rows rows{};
    for (int rule=0; rule<11; ++rule) {
        auto lhs = offsets(RULES[rule].lhs, matrices);
        auto rhs = offsets(RULES[rule].rhs, matrices);
        for (int component=0; component<2; ++component)
            for (int j=0; j<14; ++j)
                rows[2*rule+component][j] =
                    lhs[component][j] - rhs[component][j];
    }
    return rows;
}

bool certifies(const Rows& rows, const Template& certificate) {
    Row combined{};
    int strict_rhs = 0;
    for (auto [rule, component, weight] : certificate) {
        if (rule < 0 || rule >= 11 || component < 0 || component > 1 || weight < 0)
            return false;
        for (int j=0; j<14; ++j)
            combined[j] += weight * rows[2*rule+component][j];
        if (component == 0 && rule <= 1) strict_rhs += weight;
    }
    if (strict_rhs <= 0) return false;
    for (int value : combined) if (value > 0) return false;
    return true;
}

int affine_family_parameter(const Rows& rows, int a) {
    const Template base = {{0,0,a},{1,0,a},{10,0,1}};
    const Template slope = {{0,1,1},{1,1,1},{7,1,1}};
    long long lower = 1;
    long long upper = std::numeric_limits<long long>::max();
    for (int j=0; j<14; ++j) {
        long long constant = 0;
        long long coefficient = 0;
        for (auto [rule, component, weight] : base)
            constant += static_cast<long long>(weight) * rows[2*rule+component][j];
        for (auto [rule, component, weight] : slope)
            coefficient += static_cast<long long>(weight) * rows[2*rule+component][j];
        if (coefficient == 0) {
            if (constant > 0) return 0;
        } else if (coefficient > 0) {
            const long long numerator = -constant;
            const long long bound = numerator >= 0
                ? numerator / coefficient
                : -((-numerator + coefficient - 1) / coefficient);
            upper = std::min(upper, bound);
        } else {
            const long long divisor = -coefficient;
            const long long bound = constant >= 0
                ? (constant + divisor - 1) / divisor
                : -((-constant) / divisor);
            lower = std::max(lower, bound);
        }
    }
    if (lower > upper || lower > std::numeric_limits<int>::max()) return 0;
    return static_cast<int>(lower);
}

std::vector<Template> certificates() {
    return {
        {{1,0,1},{10,0,1}},
        {{1,0,1},{1,1,1},{10,0,1}},
        {{1,0,5},{1,1,6},{3,0,2},{3,1,2},{4,0,2},{4,1,2},{8,0,1},{10,0,2}},
        {{1,0,1},{1,1,2},{10,0,1}},
        {{0,0,2},{1,0,2},{1,1,6},{2,0,4},{3,1,4},{7,0,1},{10,0,2}},
        {{1,0,4},{1,1,8},{2,1,2},{3,0,2},{4,0,2},{4,1,2},{7,0,1},{8,0,1},{10,0,2}},
        {{0,0,2},{1,0,2},{1,1,8},{2,0,2},{3,1,4},{7,0,1},{10,0,2}},
        {{1,0,2},{1,1,3},{2,1,1},{3,0,1},{3,1,1},{4,1,2},{5,0,1},{10,0,1}},
        {{0,0,1},{1,0,13},{1,1,28},{2,1,6},{3,0,5},{4,0,5},{4,1,10},{8,0,2},{10,0,6}},
        {{1,0,2},{1,1,3},{2,1,2},{3,0,1},{4,1,1},{5,0,1},{5,1,1},{10,0,1}},
        {{0,0,6},{1,0,6},{1,1,30},{2,0,9},{3,1,18},{7,0,4},{10,0,6}},
        {{1,0,13},{1,1,30},{3,0,6},{3,1,3},{4,0,6},{5,1,12},{8,0,1},{10,0,6}},
        {{1,0,5},{1,1,10},{3,0,2},{3,1,3},{4,0,2},{4,1,4},{8,0,1},{10,0,2}},
        {{0,0,3},{1,0,21},{1,1,69},{3,0,9},{4,0,9},{5,1,18},{7,0,5},{10,0,12}},
        {{1,0,6},{1,1,18},{2,1,3},{3,0,3},{4,0,3},{4,1,6},{7,0,1},{8,0,1},{10,0,3}},
        {{0,0,2},{1,0,3},{1,1,1},{2,1,1},{3,0,1},{4,0,2},{4,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,3},{0,1,2},{1,0,3},{1,1,2},{3,0,1},{4,0,1},{4,1,1},{5,0,1},{9,0,1},{10,0,2}},
        {{0,0,1},{0,1,1},{1,0,1},{7,1,1},{10,0,1}},
        {{0,0,4},{1,0,6},{3,0,1},{3,1,1},{4,0,3},{4,1,1},{7,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,2},{1,0,3},{1,1,2},{2,1,2},{3,0,1},{4,0,2},{4,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,3},{0,1,4},{1,0,3},{1,1,4},{3,0,1},{4,0,1},{4,1,2},{5,0,1},{9,0,1},{10,0,2}},
        {{0,0,1},{0,1,1},{1,0,1},{7,1,2},{10,0,1}},
        {{0,0,1},{0,1,2},{1,0,1},{7,1,2},{10,0,1}},
        {{0,0,2},{1,0,2},{1,1,2},{3,1,1},{10,0,2}},
        {{0,0,2},{0,1,2},{1,0,2},{1,1,1},{7,1,1},{10,0,2}},
        {{0,0,6},{1,0,9},{3,0,1},{3,1,2},{4,0,4},{4,1,2},{7,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,6},{1,0,9},{3,0,1},{3,1,1},{4,0,4},{4,1,1},{7,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,10},{1,0,15},{3,0,1},{3,1,2},{4,0,6},{4,1,2},{7,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,3},{0,1,6},{1,0,5},{1,1,8},{3,0,1},{4,1,1},{5,0,1},{10,0,4}},
        {{0,0,2},{1,0,3},{1,1,3},{2,1,3},{3,0,1},{4,0,2},{4,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,3},{0,1,6},{1,0,3},{1,1,6},{3,0,1},{4,0,1},{4,1,3},{5,0,1},{9,0,1},{10,0,2}},
        {{0,0,1},{0,1,2},{1,0,1},{7,1,3},{10,0,1}},
        {{0,0,1},{0,1,3},{1,0,1},{7,1,3},{10,0,1}},
        {{0,0,2},{1,0,2},{1,1,3},{3,1,2},{7,1,1},{10,0,2}},
        {{0,0,8},{1,0,12},{3,0,1},{3,1,3},{4,0,5},{4,1,3},{7,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,14},{1,0,21},{3,0,1},{3,1,3},{4,0,8},{4,1,3},{7,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,8},{1,0,12},{3,0,1},{3,1,1},{4,0,5},{4,1,1},{7,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,14},{1,0,21},{3,0,1},{3,1,2},{4,0,8},{4,1,2},{7,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,20},{1,0,30},{3,0,1},{3,1,3},{4,0,11},{4,1,3},{7,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,1},{1,0,1},{1,1,3},{7,0,2},{10,0,1}},
        {{0,0,2},{0,1,7},{1,0,4},{1,1,9},{3,0,1},{4,1,1},{5,0,1},{10,0,3}},
        {{0,0,3},{0,1,3},{1,0,9},{1,1,17},{3,0,2},{3,1,6},{4,0,2},{4,1,2},{8,0,2},{10,0,5}},
        {{0,0,1},{0,1,1},{1,0,7},{1,1,11},{2,1,6},{3,0,2},{4,0,2},{4,1,2},{8,0,2},{10,0,3}},
        {{0,0,1},{0,1,1},{1,0,1},{1,1,3},{5,1,1},{10,0,1}},
        {{0,0,1},{0,1,3},{1,0,1},{1,1,1},{7,1,2},{10,0,1}},
        {{0,0,1},{0,1,2},{1,0,1},{1,1,1},{7,1,1},{10,0,1}},
        {{1,0,1},{1,1,3},{10,0,1}},
    };
}

std::vector<Template> upper_left_two_extensions() {
    return {
        {{0,0,2},{1,0,2},{10,0,1}},
        {{0,0,4},{1,0,6},{1,1,1},{2,1,1},{3,0,2},{4,0,4},{4,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,4},{1,0,6},{1,1,2},{2,1,2},{3,0,2},{4,0,4},{4,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,10},{0,1,4},{1,0,10},{1,1,4},{3,0,2},{4,0,2},{4,1,1},{5,0,2},{9,0,1},{10,0,4}},
        {{0,0,6},{0,1,4},{1,0,8},{1,1,4},{2,1,2},{3,0,2},{4,0,4},{4,1,2},{8,0,1},{9,0,1},{10,0,2}},
        {{0,0,2},{0,1,2},{1,0,2},{7,1,2},{10,0,1}},
        {{0,0,4},{1,0,4},{1,1,2},{3,1,1},{10,0,2}},
        {{0,0,2},{1,0,2},{1,1,1},{7,1,1},{10,0,1}},
        {{0,0,2},{0,1,2},{1,0,2},{1,1,1},{7,1,1},{10,0,1}},
        {{0,0,2},{1,0,2},{1,1,1},{10,0,1}},
        {{0,0,2},{1,0,2},{1,1,2},{10,0,1}},
        {{0,0,6},{1,0,9},{3,0,2},{3,1,1},{4,0,5},{4,1,1},{7,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,8},{1,0,12},{3,0,2},{3,1,2},{4,0,6},{4,1,2},{7,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,8},{1,0,12},{3,0,2},{3,1,1},{4,0,6},{4,1,1},{7,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,12},{1,0,18},{3,0,2},{3,1,2},{4,0,8},{4,1,2},{7,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,2},{0,1,2},{1,0,2},{1,1,2},{10,0,1}},
        {{0,0,1},{1,0,2},{1,1,1},{10,0,1}},
        {{0,0,1},{0,1,1},{1,0,2},{1,1,1},{10,0,1}},
        {{1,0,2},{10,0,1}},
        {{1,0,2},{1,1,2},{10,0,1}},
        {{0,0,4},{1,0,6},{1,1,3},{2,1,3},{3,0,2},{4,0,4},{4,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,22},{0,1,24},{1,0,22},{1,1,24},{3,0,6},{4,0,6},{4,1,9},{5,0,6},{9,0,3},{10,0,8}},
        {{0,0,2},{0,1,2},{1,0,2},{7,1,3},{10,0,1}},
        {{0,0,4},{1,0,4},{1,1,6},{3,1,3},{10,0,2}},
        {{0,0,13},{1,0,16},{1,1,24},{3,0,3},{3,1,9},{5,0,3},{10,0,8}},
        {{0,0,4},{0,1,6},{1,0,4},{1,1,3},{7,1,3},{10,0,2}},
        {{0,0,2},{1,0,2},{1,1,2},{7,1,1},{10,0,1}},
        {{0,0,2},{1,0,2},{1,1,3},{10,0,1}},
        {{0,0,10},{1,0,15},{3,0,2},{3,1,3},{4,0,7},{4,1,3},{7,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,16},{1,0,24},{3,0,2},{3,1,3},{4,0,10},{4,1,3},{7,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,10},{1,0,15},{3,0,2},{3,1,1},{4,0,7},{4,1,1},{7,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,16},{1,0,24},{3,0,2},{3,1,2},{4,0,10},{4,1,2},{7,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,22},{1,0,33},{3,0,2},{3,1,3},{4,0,13},{4,1,3},{7,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,7},{0,1,10},{1,0,9},{1,1,12},{3,0,1},{4,1,1},{5,0,1},{10,0,4}},
        {{0,0,2},{1,0,2},{1,1,4},{5,1,1},{10,0,1}},
        {{0,0,4},{0,1,4},{1,0,4},{1,1,6},{3,1,1},{10,0,2}},
        {{0,0,4},{0,1,4},{1,0,4},{1,1,6},{5,1,1},{10,0,2}},
        {{0,0,26},{1,0,30},{1,1,58},{3,0,4},{3,1,12},{5,0,4},{5,1,4},{10,0,15}},
        {{0,0,18},{0,1,18},{1,0,24},{1,1,32},{3,0,2},{3,1,3},{4,0,2},{5,1,2},{8,0,1},{10,0,10}},
        {{0,0,13},{0,1,13},{1,0,15},{1,1,21},{3,0,1},{3,1,3},{4,1,1},{5,0,1},{10,0,7}},
        {{0,0,2},{1,0,2},{1,1,4},{7,1,2},{10,0,1}},
        {{0,0,16},{0,1,16},{1,0,22},{1,1,29},{2,1,3},{3,0,2},{4,0,2},{5,1,2},{8,0,1},{10,0,9}},
        {{0,0,12},{0,1,12},{1,0,18},{1,1,23},{2,1,3},{3,0,2},{4,0,2},{4,1,2},{8,0,1},{10,0,7}},
        {{0,0,4},{1,0,4},{1,1,10},{3,1,1},{10,0,2}},
        {{0,0,1},{1,0,4},{1,1,6},{10,0,2}},
        {{0,0,3},{0,1,6},{1,0,4},{1,1,6},{10,0,2}},
        {{0,0,1},{1,0,6},{1,1,9},{10,0,3}},
        {{0,0,2},{1,0,2},{1,1,6},{10,0,1}},
        {{1,0,2},{1,1,3},{10,0,1}},
    };
}

std::vector<Template> upper_left_three_extensions() {
    return {
        {{0,0,3},{1,0,3},{10,0,1}},
        {{0,0,6},{1,0,9},{1,1,1},{2,1,1},{3,0,3},{4,0,6},{4,1,1},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,6},{1,0,9},{1,1,2},{2,1,2},{3,0,3},{4,0,6},{4,1,2},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,6},{1,0,9},{1,1,3},{2,1,3},{3,0,3},{4,0,6},{4,1,3},{8,0,1},{9,0,1},{10,0,1}},
        {{0,0,5},{0,1,2},{1,0,7},{1,1,2},{3,0,1},{5,0,1},{10,0,2}},
        {{0,0,12},{0,1,6},{1,0,12},{1,1,6},{3,0,3},{4,0,3},{4,1,2},{5,0,3},{9,0,1},{10,0,3}},
        {{0,0,9},{1,0,12},{2,1,3},{3,0,3},{4,0,6},{4,1,9},{6,1,6},{8,0,1},{9,0,1},{10,0,2}},
    };
}

// Return the first parameterized Farkas family that exactly certifies this
// assignment, or -1.  These constructors are arithmetic identities checked
// again by certifies(); no floating-point LP result is trusted here.
int structural_family(const Rows& rows,
                      const std::array<Matrix,7>& assignment) {
    const int a = assignment[5][0];
    const int b = assignment[5][1];
    const int f10 = assignment[0][2];
    const std::vector<Template> fixed_parameter_families = {
        {{1,0,a},{1,1,b},{10,0,1}},
        {{0,0,a},{1,0,a},{1,1,b},{3,1,b},{10,0,1}},
        {{0,0,a},{0,1,b},{1,0,a},{7,1,b},{10,0,1}},
    };
    for (std::size_t i=0; i<fixed_parameter_families.size(); ++i)
        if (certifies(rows, fixed_parameter_families[i]))
            return static_cast<int>(i);

    const int x = affine_family_parameter(rows, a);
    if (x > 0) {
        Template family = {
            {0,0,a},{0,1,x},{1,0,a},{1,1,x},{7,1,x},{10,0,1}
        };
        if (certifies(rows, family)) return 3;
    }

    const std::vector<Template> remaining_families = {
        {{0,0,2*(a+b*f10)},{1,0,3*(a+b*f10)},
         {3,0,a},{3,1,b},{4,0,2*a+b*f10},{4,1,b},{7,1,b},
         {8,0,1},{9,0,1},{10,0,1}},
        {{0,0,3*a},{1,0,3*a},{3,0,a},{4,0,a},{4,1,3*b},
         {5,0,a},{6,1,2*b},{9,0,1},{10,0,2}},
        {{0,0,a},{1,0,a},{1,1,b},{7,0,std::max(0,b-a)},{10,0,1}},
        {{1,0,a},{1,1,b},{3,0,(std::max(0,b-a)+3)/4},
         {4,1,(std::max(0,b-a)+3)/4},
         {5,0,(std::max(0,b-a)+3)/4},{10,0,1}},
    };
    for (std::size_t i=0; i<remaining_families.size(); ++i)
        if (certifies(rows, remaining_families[i]))
            return static_cast<int>(i) + 4;
    const int f01 = assignment[0][1];
    const int t01 = assignment[1][1];
    const std::vector<Template> frontier_families = {
        {{1,0,a},{1,1,b},{2,1,t01},{3,0,1},{4,1,f01},
         {5,0,1},{10,0,1}},
        {{1,0,std::max(1,b-1)},{1,1,b},{2,1,1},{3,0,1},{3,1,1},
         {4,1,std::max(1,b-1)},{5,0,1},{10,0,1}},
        {{1,0,b*(a+1)},{1,1,b*(f01+b)},{3,0,b},{3,1,b},
         {4,0,b},{4,1,b*f01},{8,0,1},{10,0,b}},
    };
    for (std::size_t i=0; i<frontier_families.size(); ++i)
        if (certifies(rows, frontier_families[i]))
            return static_cast<int>(i) + 8;

    // Family 12: fix the residual triangular support and eliminate its free
    // weights algebraically.  The resulting weights depend on matrix entries,
    // not on an enumeration ceiling.
    const int z = assignment[2][1], z11 = assignment[2][3];
    const int o = assignment[3][1], o11 = assignment[3][3];
    const int d11 = assignment[4][3];
    Template family = {
        {0,1,a*(o-f01*(1-o11))},
        {1,0,3*a},{1,1,b+a*f01+d11*(a*z+b*z11)},
        {3,0,a},{3,1,b},{4,0,a},{4,1,a*f01},
        {8,0,1},{10,0,1},
    };
    bool nonnegative = true;
    for (auto [rule, component, weight] : family)
        if (weight < 0) nonnegative = false;
    if (nonnegative && certifies(rows, family)) return 11;
    return -1;
}

int main(int argc, char** argv) {
    int upper_left_max = 1;
    bool diagnose_structural_residual = false;
    bool left_entry_four = false;
    std::string fixed_f_mode;
    for (int i=1; i<argc; ++i) {
        const std::string argument(argv[i]);
        if (argument == "--upper-left-two") upper_left_max = 2;
        else if (argument == "--upper-left-three") upper_left_max = 3;
        else if (argument == "--diagnose-structural-residual")
            diagnose_structural_residual = true;
        else if (argument == "--left-entry-four") left_entry_four = true;
        else if (argument == "--fixed-projection"
                 || argument == "--fixed-idempotent-upper"
                 || argument == "--fixed-idempotent-lower")
            fixed_f_mode = argument;
        else {
            std::cerr << "usage: verify_relative_cubic "
                         "[--upper-left-two|--upper-left-three] "
                         "[--diagnose-structural-residual] "
                         "[--left-entry-four]\n";
            return 2;
        }
    }
    if ((diagnose_structural_residual || left_entry_four) && upper_left_max != 3) {
        std::cerr << "usage: verify_relative_cubic "
                     "[--upper-left-two|--upper-left-three] "
                     "[--diagnose-structural-residual] "
                     "[--left-entry-four]\n";
        return 2;
    }
    Rows parameter_probe{};
    parameter_probe[0][0] = 13;
    parameter_probe[1][0] = -1;
    if (affine_family_parameter(parameter_probe, 1) != 13) {
        std::cerr << "exact affine parameter solver failed boundary probe\n";
        return 1;
    }
    std::vector<Matrix> matrices;
    for (int a=1; a<=upper_left_max; ++a)
        for (int p=0; p<=3; ++p)
            for (int q=0; q<=3; ++q)
                for (int d=0; d<=3; ++d)
                    matrices.push_back({a,p,q,d});
    const int count = static_cast<int>(matrices.size());
    std::vector<Matrix> left_matrices;
    const int left_entry_max = left_entry_four ? 4 : 3;
    for (int a=1; a<=upper_left_max; ++a)
        for (int p=0; p<=left_entry_max; ++p)
            for (int q=0; q<=left_entry_max; ++q)
                for (int d=0; d<=left_entry_max; ++d)
                    left_matrices.push_back({a,p,q,d});
    std::vector<std::vector<Matrix>> products(count, std::vector<Matrix>(count));
    for (int i=0; i<count; ++i)
        for (int j=0; j<count; ++j)
            products[i][j] = multiply(matrices[i], matrices[j]);

    std::vector<std::array<int,5>> cores;
    for (int f=0; f<count; ++f) for (int t=0; t<count; ++t)
    for (int z=0; z<count; ++z) {
        if (fixed_f_mode == "--fixed-projection"
            && matrices[f] != Matrix{1,0,0,0}) continue;
        if (fixed_f_mode == "--fixed-idempotent-upper"
            && matrices[f] != Matrix{1,1,0,0}) continue;
        if (fixed_f_mode == "--fixed-idempotent-lower"
            && matrices[f] != Matrix{1,0,1,0}) continue;
        if (!dominates(products[f][z], products[z][f])) continue;
        for (int o=0; o<count; ++o) {
            if (!dominates(products[f][o], products[z][t]) ||
                !dominates(products[t][z], products[o][t])) continue;
            for (int two=0; two<count; ++two)
                if (dominates(products[f][two], products[o][f]) &&
                    dominates(products[t][o], products[two][f]) &&
                    dominates(products[t][two], products[two][t]))
                    cores.push_back({f,t,z,o,two});
        }
    }

    auto templates = certificates();
    if (upper_left_max >= 2) {
        auto extensions = upper_left_two_extensions();
        templates.insert(templates.end(), extensions.begin(), extensions.end());
    }
    if (upper_left_max >= 3) {
        auto extensions = upper_left_three_extensions();
        templates.insert(templates.end(), extensions.begin(), extensions.end());
    }
    std::vector<std::uint64_t> coverage(templates.size());
    std::array<std::uint64_t,12> structural_coverage{};
    std::uint64_t survivors = 0;
    for (auto core : cores) {
        int f=core[0], t=core[1], z=core[2], o=core[3], two=core[4];
        for (const Matrix& left : left_matrices) {
            const Matrix left_f = multiply(left, matrices[f]);
            if (!dominates(multiply(left, matrices[z]), multiply(left, matrices[t])) ||
                !dominates(multiply(left, matrices[o]), multiply(left_f, matrices[f])) ||
                !dominates(multiply(left, matrices[two]), multiply(left_f, matrices[t])))
                continue;
            for (int right=0; right<count; ++right) {
                if (!dominates(products[f][right], matrices[right]) ||
                    !dominates(products[t][right], products[two][right])) continue;
                std::array<Matrix,7> assignment = {
                    matrices[f], matrices[t], matrices[z], matrices[o],
                    matrices[two], left, matrices[right]
                };
                auto rows = inequality_rows(assignment);
                ++survivors;
                bool covered = false;
                if (upper_left_max == 3 || !fixed_f_mode.empty()) {
                    int family = structural_family(rows, assignment);
                    if (family >= 0) {
                        ++structural_coverage[family];
                        covered = true;
                    }
                }
                for (std::size_t i=0; !covered && i<templates.size(); ++i) {
                    if (certifies(rows, templates[i])) {
                        if (diagnose_structural_residual) {
                            std::cerr << "residual template=" << i;
                            for (int symbol=0; symbol<7; ++symbol)
                                for (int entry=0; entry<4; ++entry)
                                    std::cerr << ' ' << assignment[symbol][entry];
                            std::cerr << '\n';
                        }
                        ++coverage[i];
                        covered = true;
                        break;
                    }
                }
                if (!covered) {
                    std::cerr << "uncovered coefficient assignment:";
                    for (int symbol=0; symbol<7; ++symbol)
                        for (int entry=0; entry<4; ++entry)
                            std::cerr << ' ' << assignment[symbol][entry];
                    std::cerr << '\n';
                    return 1;
                }
            }
        }
    }

    const std::vector<std::uint64_t> expected_basic = {
        3262148,1188800,1327820,706160,344992,11248,608800,404952,
        49624,69172,91380,28756,15364,320,80,63156,140,2488,320,
        27148,100,408,816,160,200,320,576,576,100,31924,52,109040,
        76088,156,320,576,832,832,832,1640,52,608,312,78680,8124,
        144,30528,
    };
    const std::vector<std::uint64_t> expected_extended = {
        6514396,2377600,2655640,1412320,689984,22496,1217600,8313184,
        99248,939440,182760,57512,30728,640,160,126312,280,4976,800,
        54296,200,816,1632,320,400,800,1344,1344,200,63848,104,
        218080,152176,312,800,1344,1664,1664,1664,3280,104,1216,624,
        157360,16248,288,61056,4826316,200040,158512,280,56920,243840,
        162656,42240,113976,40672,318368,800,800,1344,1344,165248,
        55896,51312,64384,281536,105512,200,172720,294168,3040,57672,
        320,30720,800,1344,1664,1664,1664,200,83960,12064,1296,808,
        880,368,680,384,384,24824,65064,14272,29848,6776,10440,
    };
    const std::vector<std::uint64_t> expected_full(103);
    const std::array<std::uint64_t,12> expected_structural = {
        52698288,14886420,3017712,255360,745632,26208,71532,1152,
        444192,12480,6132,4824,
    };
    const std::array<std::uint64_t,12> expected_left_four_structural = {
        82436820,36920364,7249752,677964,1553400,48000,223488,3144,
        1405860,31032,37836,44064,
    };
    if (!fixed_f_mode.empty()) {
        std::cout << "fixed_f_mode=" << fixed_f_mode
                  << " cores=" << cores.size()
                  << " survivors=" << survivors << " structural=";
        for (std::size_t index=0; index<structural_coverage.size(); ++index) {
            if (index) std::cout << ',';
            std::cout << structural_coverage[index];
        }
        std::cout << "\n";
        return 0;
    }
    const auto& expected = upper_left_max == 1 ? expected_basic
                         : upper_left_max == 2 ? expected_extended
                                               : expected_full;
    const std::size_t expected_cores = upper_left_max == 1 ? 47378
                                     : upper_left_max == 2 ? 170450
                                                           : 375570;
    const std::uint64_t expected_survivors = left_entry_four ? 130631724ULL
                                           : upper_left_max == 1 ? 8546864ULL
                                           : upper_left_max == 2 ? 33099480ULL
                                                                 : 72169932ULL;
    const auto& expected_structural_coverage = left_entry_four
        ? expected_left_four_structural : expected_structural;
    if (cores.size() != expected_cores || survivors != expected_survivors ||
        coverage != expected ||
        (upper_left_max == 3 &&
         structural_coverage != expected_structural_coverage)) {
        std::cerr << "enumeration or coverage mismatch\n";
        std::cerr << "cores=" << cores.size() << " survivors=" << survivors
                  << " templates=" << templates.size() << "\nstructural=";
        for (auto value : structural_coverage) std::cerr << value << ',';
        std::cerr << "\ncoverage=";
        for (auto value : coverage) std::cerr << value << ',';
        std::cerr << '\n';
        return 1;
    }
    std::uint64_t template_checksum = 1469598103934665603ULL;
    auto mix = [&template_checksum](std::uint64_t value) {
        template_checksum ^= value + 1;
        template_checksum *= 1099511628211ULL;
    };
    for (const auto& certificate : templates) {
        mix(certificate.size());
        for (auto [rule, component, weight] : certificate) {
            mix(rule); mix(component); mix(weight);
        }
    }
    const std::uint64_t raw_assignments = left_entry_four
        ? 18786186952704000ULL
        : upper_left_max == 1
        ? 4398046511104ULL
        : upper_left_max == 2 ? 562949953421312ULL
                              : 9618527719784448ULL;
    std::cout << "{\"raw_assignments\":" << raw_assignments << ","
              << "\"core_survivors\":" << cores.size() << ","
              << "\"full_survivors\":" << survivors << ","
              << "\"templates\":" << templates.size() << ","
              << "\"template_checksum\":" << template_checksum << ",";
    if (upper_left_max == 3) {
        std::cout << "\"structural_families\":12,"
                  << "\"structural_coverage\":[";
        for (std::size_t i=0; i<structural_coverage.size(); ++i) {
            if (i) std::cout << ',';
            std::cout << structural_coverage[i];
        }
        std::cout << "],";
    }
    std::cout
              << "\"uncovered\":0}\n";
}
