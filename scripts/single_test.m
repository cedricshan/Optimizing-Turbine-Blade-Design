fprintf('=== Turbine Simulator Single Test ===\n');
fprintf('MATLAB %s | %s | %s\n', version, computer, datestr(now));

set(0, 'DefaultFigureVisible', 'off');

projdir = fullfile(fileparts(mfilename('fullpath')), '..');
addpath(projdir);
outdir = fullfile(projdir, 'sim_outputs');
if ~exist(outdir, 'dir'), mkdir(outdir); end

x1 = 250e9; x2 = 0.295; x3 = 1e-5; x4 = 10; x5 = 200; x6 = 2.9e5;
fprintf('Input: [%.2e, %.3f, %.2e, %.1f, %.1f, %.2e]\n', x1, x2, x3, x4, x5, x6);

figs_before = findall(0, 'Type', 'figure');
tic;
[stress, displ] = simulator(x1, x2, x3, x4, x5, x6);
elapsed = toc;

figs_new = setdiff(findall(0, 'Type', 'figure'), figs_before);
for j = 1:length(figs_new)
    saveas(figs_new(j), fullfile(outdir, sprintf('sim_fig_%02d.png', j)));
    savefig(figs_new(j), fullfile(outdir, sprintf('sim_fig_%02d.fig', j)));
end
if ~isempty(figs_new), close(figs_new); end

fprintf('Stress:       %.6e\n', stress);
fprintf('Displacement: %.6e\n', displ);
fprintf('Feasible:     %s\n', string(displ < 1.3e-3));
fprintf('Time:         %.1f s\n', elapsed);
fprintf('Saved %d figure(s) to %s\n', length(figs_new), outdir);
fprintf('=== Test PASSED ===\n');

exit;
