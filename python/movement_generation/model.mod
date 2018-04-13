### PARAMS ###
param MaxBoards;
param MaxOpponents;
# [pair with lower number, pair with higher number, board set they do play against each other]
set played_boards within (1..MaxOpponents cross 1..MaxOpponents cross 1..MaxBoards);
# [pair with lower number, pair with higher number, board set they don't play against each other]
set eligible_comparisons within (1..MaxOpponents cross 1..MaxOpponents cross 1..MaxBoards);

### VARS ###
# 1 if p1 & p2 sit in the same direction on board set b.
var Comparison{eligible_comparisons} >= 0 integer <= 1;

# 1 if p sits in the North direction for board b.
var AbsolutePosition{p in 1..MaxOpponents, b in 1..MaxBoards} >=0 integer <=1;

# Helper variable used to set the Comparison relationship to Absolute Positions of the two pairs involved.
var Delta{p1 in 1..MaxOpponents, p2 in 1..MaxOpponents, b in 1..MaxBoards} >=0 integer <=1;

# Number of times p1 and p2 are compared.
var NumComparisons{p1 in 1..MaxOpponents, p2 in (p1+1)..MaxOpponents} >=0 integer;

# The difference between number of comparisons between p1 and p2 and p1 and p3.
var CompDiffUBLowP1{p1 in 1..MaxOpponents, p2 in (p1+1)..MaxOpponents, p3 in (p2 + 1)..MaxOpponents} >=0 integer;
var CompDiffUBMidP1{p1 in 2..MaxOpponents, p2 in 1..(p1-1), p3 in (p1 + 1)..MaxOpponents} >=0 integer;
var CompDiffUBHighP1{p1 in 3..MaxOpponents, p2 in 1..(p1-2), p3 in (p2 + 1)..(p1-1)} >=0 integer;

# For a pair p, sum of the number of comparisons between p, q for all q != p
var Alpha{1..MaxOpponents} >=0 integer;

### OBJECTIVE FUNCTION ####
minimize fairness: sum{p in 1..MaxOpponents} Alpha[p];

### CONSTRAINTS ###
# Extra constraints that set the relationship between comparisons in two opponents/boards pairs.
subject to hand_comparisons_stacked1{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = e and q1 = f and q2 = g}: Comparison[p1, q1, b] = 1 - Comparison[p1, q2, b];
subject to hand_comparisons_stacked2{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = e and q1 = f and q2 = g}: Comparison[p2, q1, b] = 1 - Comparison[p2, q2, b];
subject to hand_comparisons_stacked3{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = e and q1 = f and q2 = g}: Comparison[p1, q1, b] = 1 - Comparison[p2, q1, b];
subject to hand_comparisons_stacked4{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = e and q1 = f and q2 = g}: Comparison[p1, q2, b] = 1 - Comparison[p2, q2, b];
subject to hand_comparisons_interleaved1{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = f and q1 = e and q2 = g}: Comparison[p1, q1, b] = 1 - Comparison[p1, q2, b];
subject to hand_comparisons_interleaved2{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = f and q1 = e and q2 = g}: Comparison[q1, p2, b] = 1 - Comparison[p2, q2, b];
subject to hand_comparisons_interleaved3{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = f and q1 = e and q2 = g}: Comparison[p1, q1, b] = 1 - Comparison[q1, p2, b];
subject to hand_comparisons_interleaved4{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = f and q1 = e and q2 = g}: Comparison[p1, q2, b] = 1 - Comparison[p2, q2, b];
subject to hand_comparisons_squished1{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = g and q1 = e and q2 = f}: Comparison[p1, q1, b] = 1 - Comparison[p1, q2, b];
subject to hand_comparisons_squished2{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = g and q1 = e and q2 = f}: Comparison[q1, p2, b] = 1 - Comparison[q2, p2, b];
subject to hand_comparisons_squished3{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = g and q1 = e and q2 = f}: Comparison[p1, q1, b] = 1 - Comparison[q1, p2, b];
subject to hand_comparisons_squished4{(p1, p2, b) in played_boards, (q1, q2, c) in played_boards, d in 1..MaxOpponents, e in (d+1)..MaxOpponents, f in (e+1)..MaxOpponents, g in (f+1)..MaxOpponents : b = c and p1 = d and p2 = g and q1 = e and q2 = f}: Comparison[p1, q2, b] = 1 - Comparison[q2, p2, b];

subject to hand_opposites {(p1, p2, b) in played_boards}: AbsolutePosition[p1, b] = 1 - AbsolutePosition[p2, b];

# Constraints to define Comparison/AbsolutePosition relationships
subject to x_less_than_y {(p1, p2, b) in eligible_comparisons}: AbsolutePosition[p1, b] - AbsolutePosition[p2, b] <= (1 - Comparison[p1, p2, b]);
subject to neg_y_less_than_x {(p1, p2, b) in eligible_comparisons}: AbsolutePosition[p1, b] - AbsolutePosition[p2, b] >= (Comparison[p1, p2, b] - 1);
subject to delta_left {(p1, p2, b) in eligible_comparisons}: (1 - Comparison[p1, p2, b]) - 2 * Delta[p1, p2, b] <= AbsolutePosition[p1, b] - AbsolutePosition[p2, b];
subject to delta_right {(p1, p2, b) in eligible_comparisons}: (Comparison[p1, p2, b] - 1) + 2 * (1 - Delta[p1, p2, b]) >= AbsolutePosition[p1, b] - AbsolutePosition[p2, b];

subject to num_comparisons {p1 in 1..MaxOpponents, p2 in (p1+1)..MaxOpponents} : NumComparisons[p1, p2] = sum{(q1, q2, n) in eligible_comparisons : q1 = p1 and q2 = p2} Comparison[p1, p2, n];

# Constraints to define the minimization parameter
subject to beta_minimizationLowP1 {p1 in 1..MaxOpponents, p2 in (p1+1)..MaxOpponents, p3 in (p2 + 1)..MaxOpponents}: 
    NumComparisons[p1, p2] - NumComparisons[p1, p3] <= CompDiffUBLowP1[p1, p2, p3];
subject to beta_minimizationMidP1 {p1 in 2..MaxOpponents, p2 in 1..(p1-1), p3 in (p1 + 1)..MaxOpponents}: 
    NumComparisons[p2, p1] - NumComparisons[p1, p3] <= CompDiffUBMidP1[p1, p2, p3];
subject to beta_minimizationHighP1 {p1 in 3..MaxOpponents, p2 in 1..(p1-2), p3 in (p2 + 1)..(p1-1)}: 
    NumComparisons[p2, p1] - NumComparisons[p3, p1] <= CompDiffUBHighP1[p1, p2, p3];

subject to beta_minimizationLowP12 {p1 in 1..MaxOpponents, p2 in (p1+1)..MaxOpponents, p3 in (p2 + 1)..MaxOpponents}: 
    NumComparisons[p1, p3] - NumComparisons[p1, p2] <= CompDiffUBLowP1[p1, p2, p3];
subject to beta_minimizationMidP12 {p1 in 2..MaxOpponents, p2 in 1..(p1-1), p3 in (p1 + 1)..MaxOpponents}: 
    NumComparisons[p1, p3] - NumComparisons[p2, p1] <= CompDiffUBMidP1[p1, p2, p3];
subject to beta_minimizationHighP12 {p1 in 3..MaxOpponents, p2 in 1..(p1-2), p3 in (p2 + 1)..(p1-1)}: 
    NumComparisons[p3, p1] - NumComparisons[p2, p1] <= CompDiffUBHighP1[p1, p2, p3];


subject to alpha_beta {p1 in 1..MaxOpponents}: Alpha[p1] = sum{p2 in (p1+1)..MaxOpponents, p3 in (p2 + 1)..MaxOpponents} CompDiffUBLowP1[p1, p2, p3] + 
                                                           sum{p2 in 1..(p1-1), p3 in (p1 + 1)..MaxOpponents} CompDiffUBMidP1[p1, p2, p3] +
                                                           sum{p2 in 1..(p1-2), p3 in (p2 + 1)..(p1-1)} CompDiffUBHighP1[p1, p2, p3] ;

