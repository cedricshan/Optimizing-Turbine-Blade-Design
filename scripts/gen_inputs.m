% gen_inputs.m — Generate LHS parameter sets for batch simulation
%
% Parameter ranges from project spec:
%   x1: Young's Modulus          [200e9,  300e9]  Pa
%   x2: Poisson's Ratio          [0.1,    0.49]
%   x3: CTE                      [5e-6,   1.5e-5] K^-1
%   x4: Thermal Conductivity     [5,      15]     W/m/K
%   x5: Cooling Air Temperature  [50,     350]    °C
%   x6: Pressure Load            [1.0e5,  4.8e5]  Pa

% Phase 1 default: n ≈ 10p–15p for p=6 → 80 runs, maximin LHD (project plan).
n = 80;
envn = getenv('TURBINE_N_RUNS');
if ~isempty(envn)
    n = str2double(envn);
end
if isnan(n) || n < 1
    n = 80;
end
rng(42);

lb = [200e9,  0.1,   5e-6,  5,   50,  1.0e5];
ub = [300e9,  0.49,  1.5e-5, 15, 350,  4.8e5];

% Prefer maximin LHS for space-filling; fall back to plain LHS / manual.
X = [];
try
    X = lhsdesign(n, 6, 'Criterion', 'maximin', 'Iterations', 1000);
    fprintf('Generated maximin LHS: n=%d, p=6.\n', n);
catch ME
    fprintf('maximin lhsdesign failed (%s), trying default lhsdesign.\n', ME.message);
    try
        X = lhsdesign(n, 6);
    catch ME2
        fprintf('lhsdesign failed (%s), using manual LHS.\n', ME2.message);
    end
end
if isempty(X)
    X = zeros(n, 6);
    for j = 1:6
        X(:, j) = (randperm(n)' - 1 + rand(n, 1)) / n;
    end
    fprintf('Note: manual LHS fallback.\n');
end

for j = 1:6
    X(:, j) = lb(j) + X(:, j) .* (ub(j) - lb(j));
end

projdir = fullfile(fileparts(mfilename('fullpath')), '..');
outfile = fullfile(projdir, 'inputs', 'params.csv');

T = array2table(X, 'VariableNames', {'x1','x2','x3','x4','x5','x6'});
writetable(T, outfile);

fprintf('Generated %d parameter sets -> %s\n', n, outfile);
disp(T(1:5, :));

exit;
