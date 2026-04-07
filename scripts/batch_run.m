% batch_run.m — Run one simulation based on SLURM_ARRAY_TASK_ID

task_id = str2double(getenv('SLURM_ARRAY_TASK_ID'));
if isnan(task_id)
    error('SLURM_ARRAY_TASK_ID not set. Submit via: sbatch --array=1-N slurm/batch_run.sh');
end

fprintf('=== Batch Run #%d | %s ===\n', task_id, datestr(now));
set(0, 'DefaultFigureVisible', 'off');

projdir = fullfile(fileparts(mfilename('fullpath')), '..');
addpath(projdir);
params = readtable(fullfile(projdir, 'inputs', 'params.csv'));
n_params = height(params);
if task_id > n_params
    fprintf('Skip task %d: params.csv has only %d row(s).\n', task_id, n_params);
    exit;
end
x = table2array(params(task_id, :));
fprintf('Input: [%.2e, %.3f, %.2e, %.1f, %.1f, %.2e]\n', x);

% Run simulator
figs_before = findall(0, 'Type', 'figure');
tic;
[stress, displ] = simulator(x(1), x(2), x(3), x(4), x(5), x(6));
elapsed = toc;

% Save figures
figdir = fullfile(projdir, 'sim_outputs', sprintf('run_%03d', task_id));
if ~exist(figdir, 'dir'), mkdir(figdir); end
figs_new = setdiff(findall(0, 'Type', 'figure'), figs_before);
for j = 1:length(figs_new)
    saveas(figs_new(j), fullfile(figdir, sprintf('fig_%02d.png', j)));
end
if ~isempty(figs_new), close(figs_new); end

% Save result
resdir = fullfile(projdir, 'results');
if ~exist(resdir, 'dir'), mkdir(resdir); end
T = table(task_id, x(1), x(2), x(3), x(4), x(5), x(6), stress, displ, elapsed, ...
    'VariableNames', {'run_id','x1','x2','x3','x4','x5','x6','stress','displacement','time_s'});
writetable(T, fullfile(resdir, sprintf('result_%03d.csv', task_id)));

fprintf('Stress: %.6e | Displ: %.6e | Feasible: %s | Time: %.1f s\n', ...
    stress, displ, string(displ < 1.3e-3), elapsed);
fprintf('=== Run #%d Complete ===\n', task_id);

exit;
