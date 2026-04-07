% collect_results.m — Gather all batch results into summary.csv

projdir = fullfile(fileparts(mfilename('fullpath')), '..');
resdir = fullfile(projdir, 'results');
files = dir(fullfile(resdir, 'result_*.csv'));

if isempty(files)
    error('No result files found in %s', resdir);
end

T = [];
for i = 1:length(files)
    T = [T; readtable(fullfile(resdir, files(i).name))];
end
T = sortrows(T, 'run_id');

outfile = fullfile(resdir, 'summary.csv');
writetable(T, outfile);

fprintf('\n=== Results Summary (%d / %d runs collected) ===\n', height(T), max(T.run_id));
fprintf('%-5s %14s %14s %8s %7s\n', 'Run', 'Stress', 'Displacement', 'Feasible', 'Time');
fprintf('%s\n', repmat('-', 1, 52));
for i = 1:height(T)
    fprintf('%-5d %14.6e %14.6e %8s %6.1fs\n', ...
        T.run_id(i), T.stress(i), T.displacement(i), ...
        string(T.displacement(i) < 1.3e-3), T.time_s(i));
end

n_feasible = sum(T.displacement < 1.3e-3);
fprintf('\nFeasible: %d / %d\n', n_feasible, height(T));

if n_feasible > 0
    feas = T(T.displacement < 1.3e-3, :);
    [~, idx] = min(feas.stress);
    fprintf('Best feasible stress: %.6e (Run #%d)\n', feas.stress(idx), feas.run_id(idx));
    fprintf('  x = [%.2e, %.3f, %.2e, %.1f, %.1f, %.2e]\n', ...
        feas.x1(idx), feas.x2(idx), feas.x3(idx), feas.x4(idx), feas.x5(idx), feas.x6(idx));
end

fprintf('\nSaved -> %s\n', outfile);

exit;
