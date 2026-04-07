"""
Generate the final PDF report with proper Unicode math rendering.
Uses DejaVu TTF fonts for Greek letters and math symbols.

Usage:  python3 analysis/generate_report.py
"""
import os
from fpdf import FPDF

P   = "/hpc/home/rx67/turbine_project_Yuan"
FIG = os.path.join(P, "figures")
OUT = os.path.join(P, "report.pdf")

# DejaVu font paths (support full Unicode including Greek, math)
FONT_DIR = "/usr/share/fonts"
DJ_REGULAR = f"{FONT_DIR}/dejavu-sans-fonts/DejaVuSans.ttf"
DJ_BOLD    = f"{FONT_DIR}/dejavu-sans-fonts/DejaVuSans-Bold.ttf"
DJ_OBLIQUE = f"{FONT_DIR}/dejavu-sans-fonts/DejaVuSans-Oblique.ttf"
DJ_MONO    = f"{FONT_DIR}/dejavu-sans-mono-fonts/DejaVuSansMono.ttf"


class R(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'Letter')
        self.set_auto_page_break(True, 18)
        self.alias_nb_pages()
        self._s = 0; self._ss = 0

        # Register Unicode fonts
        self.add_font('DJ', '', DJ_REGULAR)
        self.add_font('DJ', 'B', DJ_BOLD)
        self.add_font('DJ', 'I', DJ_OBLIQUE)
        self.add_font('DJM', '', DJ_MONO)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font('DJ', 'I', 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, 'Turbine Blade Optimization \u2014 Research Report', align='C')
        self.ln(5)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-14)
        self.set_font('DJ', 'I', 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def sec(self, t):
        self._s += 1; self._ss = 0; self.ln(3)
        self.set_font('DJ', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, f'{self._s}. {t}', new_x='LMARGIN', new_y='NEXT')
        self.ln(1)

    def sub(self, t):
        self._ss += 1; self.ln(2)
        self.set_font('DJ', 'B', 10.5)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f'{self._s}.{self._ss} {t}', new_x='LMARGIN', new_y='NEXT')
        self.ln(0.5)

    def p(self, t):
        self.set_font('DJ', '', 9.8)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 4.6, t, align='J')
        self.ln(0.8)

    def eq(self, t):
        """Centered equation in monospace (supports Unicode)."""
        self.set_font('DJM', '', 9)
        self.set_text_color(0, 0, 80)
        self.cell(0, 5.5, t, align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0, 0, 0)
        self.ln(0.5)

    def fig(self, path, cap, w=130):
        if self.get_y() + 50 > self.h - 22:
            self.add_page()
        self.ln(1.5)
        self.image(path, x=(self.w - w) / 2, w=w)
        self.ln(1)
        self.set_font('DJ', 'I', 7.5)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 3.8, cap, align='C')
        self.set_text_color(0, 0, 0)
        self.ln(1.5)

    def tbl(self, hd, rows, ws=None):
        n = len(hd)
        if ws is None:
            ws = [(self.w - self.l_margin - self.r_margin) / n] * n
        self.ln(1)
        self.set_font('DJ', 'B', 8)
        self.set_fill_color(230, 235, 245)
        for i, h in enumerate(hd):
            self.cell(ws[i], 5, h, 1, align='C', fill=True)
        self.ln()
        self.set_font('DJ', '', 8)
        for row in rows:
            for i, v in enumerate(row):
                self.cell(ws[i], 4.8, str(v), 1, align='C')
            self.ln()
        self.ln(1.5)


def build():
    pdf = R()
    pdf.set_left_margin(20); pdf.set_right_margin(20); pdf.set_top_margin(15)

    # ── Greek/math shortcuts ─────────────────────────────────────────
    mu = '\u03bc'; sigma = '\u03c3'; theta = '\u03b8'
    Phi = '\u03a6'; phi = '\u03c6'; xi = '\u03be'
    ep = '\u03b5'; alpha = '\u03b1'; delta = '\u03b4'
    sq5 = '\u221a5'; leq = '\u2264'; geq = '\u2265'
    pm = '\u00b1'; rarr = '\u2192'; cdot = '\u00b7'
    sup2 = '\u00b2'; minus1 = '\u207b\u00b9'

    # ══════════ TITLE ═══════════════════════════════════════════════
    pdf.add_page(); pdf.ln(18)
    pdf.set_font('DJ', 'B', 16)
    pdf.multi_cell(0, 8,
        "Optimizing Turbine Blade Design:\n"
        "A Data-Driven Approach Using Gaussian Process\n"
        "Surrogates and Bayesian Optimization", align='C')
    pdf.ln(5)
    pdf.set_font('DJ', '', 10.5)
    pdf.cell(0, 6, 'STA 643 \u2014 Design and Analysis of Experiments',
             align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)
    pdf.cell(0, 6, 'April 2026', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    # Abstract
    pdf.set_font('DJ', 'B', 10)
    pdf.cell(0, 5, 'Abstract', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('DJ', 'I', 9)
    pdf.multi_cell(0, 4.2,
        "We present a framework for optimizing gas turbine blade material properties and "
        "cooling conditions to minimize maximum von Mises stress, subject to a displacement "
        f"feasibility constraint (d < 1.3{cdot}10{minus1}{sup2}{sup2} m) and operational uncertainties on cooling "
        f"temperature ({pm}2\u00b0C) and pressure load ({pm}10\u2074 Pa). Using all 300 permitted "
        "finite-element simulator evaluations \u2014 allocated as 100 initial Latin Hypercube "
        "Design, 150 sequential Expected Improvement with Constraints, 27 robust grid "
        "validation (3 candidates \u00d7 3\u00d73 perturbation grid), and 23 final validation "
        f"runs \u2014 we achieve a 41% reduction in maximum stress. The GP surrogate models "
        f"attain 10-fold cross-validated R{sup2} > 0.994. ARD length-scale analysis identifies "
        "CTE (Coefficient of Thermal Expansion) as the dominant factor. The recommended "
        "design maintains 100% displacement feasibility under operational uncertainty "
        "with a 45% safety margin.", align='J')

    # ══════════ 1. INTRODUCTION ═════════════════════════════════════
    pdf.add_page()
    pdf.sec('Introduction')

    pdf.sub('Background and Motivation')
    pdf.p(
        "Gas turbine engines convert high-temperature, high-pressure combustion gases into "
        "mechanical energy for aircraft propulsion and power generation. The turbine blades "
        "within these engines operate under extreme conditions: inlet temperatures can exceed "
        "1,500\u00b0C, well above the melting point of most metal alloys. This creates severe "
        "thermal and mechanical loads that induce stress and deformation in the blades. "
        "Prolonged exposure accelerates engine degradation, making turbine blade design a "
        "critical engineering challenge.")
    pdf.p(
        "Physical prototyping is expensive and time-consuming, so we use a finite-element "
        "method (FEM) computer simulator that predicts the von Mises stress distribution and "
        "displacement across the blade surface. The simulator accepts six input variables and "
        "returns two scalar outputs: maximum stress and maximum displacement.")

    pdf.tbl(['Variable', 'Description', 'Range', 'Type'],
        [['x\u2081', "Young's Modulus", '[2\u00d710\u2079, 3\u00d710\u2079] Pa', 'Material'],
         ['x\u2082', "Poisson's Ratio", '[0.1, 0.49]', 'Material'],
         ['x\u2083', 'CTE', f'[5\u00d710\u207b\u2076, 1.5\u00d710\u207b\u2075] K{minus1}', 'Material'],
         ['x\u2084', 'Thermal Conductivity', '[5, 15] W/m/K', 'Material'],
         ['x\u2085', 'Cooling Air Temp', f'[50, 350] \u00b0C', f'Oper. ({pm}2\u00b0C)'],
         ['x\u2086', 'Pressure Load', f'[10\u2075, 4.8\u00d710\u2075] Pa', f'Oper. ({pm}10\u2074)']],
        ws=[18, 48, 52, 49])

    pdf.sub('Problem Formulation')
    pdf.p(
        f"Let x_d = (x\u2081, x\u2082, x\u2083, x\u2084) denote the material parameters that can "
        f"be precisely controlled, and x\u2085*, x\u2086* denote the nominal operational set-points. "
        "The operational inputs are subject to uncontrollable perturbations:")
    pdf.eq(f"x\u2085_actual = x\u2085* + {ep}\u2085,    {ep}\u2085 ~ Uniform(\u22122, +2)")
    pdf.eq(f"x\u2086_actual = x\u2086* + {ep}\u2086,    {ep}\u2086 ~ Uniform(\u221210\u2074, +10\u2074)")
    pdf.p("The constrained robust optimization problem is:")
    pdf.eq(f"minimize      E[stress(x_d, x\u2085* + {ep}\u2085, x\u2086* + {ep}\u2086)]")
    pdf.eq(f"subject to    Pr[displacement(x_d, x\u2085* + {ep}\u2085, x\u2086* + {ep}\u2086) < d*] {geq} 1 \u2212 {alpha}")
    pdf.p(
        f"where d* = 1.3\u00d710\u207b\u00b3 m is the displacement failure threshold. The "
        "computational budget is limited to 300 simulator evaluations, each taking ~80 seconds. "
        "This necessitates a sample-efficient strategy combining initial exploration, "
        "surrogate-guided optimization, and robustness validation.")

    # ══════════ 2. METHODOLOGY ═════════════════════════════════════
    pdf.sec('Methodology')

    pdf.sub('Phase 1: Initial Space-Filling Design (100 runs)')
    pdf.p(
        "We generated a 100-point maximin Latin Hypercube Design (LHD) in [0,1]\u2076, "
        f"where each input is scaled via z\u1d62 = (x\u1d62 \u2212 L\u1d62) / (U\u1d62 \u2212 L\u1d62). "
        "The LHD ensures that each input's marginal distribution is uniform: the [0,1] "
        "interval is partitioned into n = 100 equal strata with exactly one point per stratum. "
        "The maximin criterion further optimizes the arrangement by maximizing the minimum "
        "pairwise Euclidean distance among all points, ensuring no large unexplored regions. "
        "We selected the best LHD from 50 random candidates, achieving a minimum pairwise "
        "distance of 0.261. With 100 points in 6 dimensions (~17 per variable), this design "
        "provides ample data for fitting a smooth surrogate model.")

    pdf.sub('Phase 2: Gaussian Process Surrogate Model')
    pdf.p(
        "We fit independent Gaussian Process (GP) models for stress and displacement. "
        "A GP defines a distribution over functions: given observed data, it provides a "
        f"posterior mean {mu}(z) (best prediction) and posterior variance {sigma}{sup2}(z) "
        "(uncertainty) at any untested point. Formally:")
    pdf.eq(f"y(z) ~ GP( {mu},  k(z, z\u2032) )")
    pdf.p(
        f"where {mu} is a constant mean and k(z, z\u2032) is the covariance kernel. We use "
        f"the Mat\u00e9rn-5/2 kernel with Automatic Relevance Determination (ARD), which assigns "
        f"a separate length-scale parameter {theta}\u2c7c to each input dimension:")
    pdf.eq(f"k(z, z\u2032) = {sigma}{sup2} \u00b7 (1 + {sq5}\u00b7r + 5r{sup2}/3) \u00b7 exp(\u2212{sq5}\u00b7r)")
    pdf.eq(f"r = \u221a[ \u03a3\u2c7c (z\u2c7c \u2212 z\u2032\u2c7c){sup2} / {theta}\u2c7c{sup2} ]")
    pdf.p(
        f"A short {theta}\u2c7c means the output changes rapidly with input j (high sensitivity); "
        f"a long {theta}\u2c7c indicates little effect. The Mat\u00e9rn-5/2 kernel produces "
        "twice-differentiable functions \u2014 smooth but not infinitely so \u2014 appropriate for "
        f"FEM simulations. A nugget term ({sigma}\u2099{sup2} ~ 10\u207b\u2076) is added for "
        "numerical stability. Since the simulator is deterministic, the GP interpolates "
        "exactly through observed data.")
    pdf.p(
        f"All hyperparameters \u2014 signal variance {sigma}{sup2}, length-scales "
        f"{theta}\u2081,...,{theta}\u2086, and nugget {sigma}\u2099{sup2} \u2014 are estimated "
        "by maximizing the log marginal likelihood:")
    pi_sym = '\u03c0'
    pdf.eq(f"log p(y|Z) = \u2212\u00bd y\u1d40 K\u207b\u00b9 y  \u2212  \u00bd log|K|  \u2212  n/2 \u00b7 log(2{pi_sym})")
    pdf.p(
        f"where K is the n\u00d7n covariance matrix with K\u1d62\u2c7c = k(z\u1d62, z\u2c7c) + "
        f"{sigma}\u2099{sup2} \u00b7 {delta}\u1d62\u2c7c. We use 20 random restarts to avoid local "
        "optima. Model accuracy is assessed via 10-fold cross-validation with hyperparameters "
        "re-estimated in each fold to prevent information leakage.")

    pdf.tbl([f'Response', f'CV R{sup2}', 'RMSE', 'MAPE', '95% Cov.'],
        [['Stress', '0.9956', '1.82\u00d710\u2077', '1.33%', '92%'],
         ['Displacement', '0.9942', '2.79\u00d710\u207b\u2075', '1.06%', '91%']],
        ws=[35, 30, 35, 25, 42])

    pdf.fig(os.path.join(FIG, 'fig3_cv.png'),
        'Figure 1. 10-fold CV: predicted vs actual for stress (left) and displacement (right).', w=130)
    pdf.fig(os.path.join(FIG, 'fig4_qq.png'),
        'Figure 2. QQ plots of standardized CV residuals. Linear patterns confirm well-calibrated uncertainty.', w=130)

    pdf.sub('Phase 3: Sequential Constrained Optimization (150 runs)')
    pdf.p("We sequentially select new evaluation points by maximizing the Expected "
           "Improvement with Constraints (EIC) acquisition function:")
    pdf.eq(f"EIC(z) = EI(z) \u00b7 Pr[displacement(z) < d*]")
    pdf.p(f"The Expected Improvement for stress minimization is:")
    pdf.eq(f"EI(z) = (f* \u2212 {mu}\u209b(z)) \u00b7 {Phi}(u) + {sigma}\u209b(z) \u00b7 {phi}(u)")
    pdf.eq(f"u = (f* \u2212 {mu}\u209b(z)) / {sigma}\u209b(z)")
    pdf.p(
        f"where f* is the best feasible stress found so far, {mu}\u209b(z) and {sigma}\u209b(z) are "
        f"the GP posterior mean and standard deviation, and {Phi}, {phi} are the standard "
        "normal CDF and PDF. The EI is large when either (a) the predicted stress is much "
        "better than f* (exploitation), or (b) the prediction uncertainty is large (exploration). "
        "The constraint probability is:")
    pdf.eq(f"Pr[disp(z) < d*] = {Phi}( (d* \u2212 {mu}\u1d48(z)) / {sigma}\u1d48(z) )")
    pdf.p(
        "Multiplying EI by this probability ensures we only pursue designs that are both "
        "promising and likely feasible. We generate batches of 15\u201320 points per iteration "
        "using a diversified strategy: EIC is evaluated on 80,000 random candidates, and top "
        "points are selected with a minimum-distance penalty. After each batch, the GP models "
        "are re-fitted. Over 150 sequential runs, the best feasible stress improved from "
        f"4.46\u00d710\u2078 to 2.64\u00d710\u2078 Pa.")

    pdf.sub('Phase 4: Robust Validation (27 runs)')
    pdf.p(
        "We select 3 top candidates (diverse in coded space) and evaluate each on a 3\u00d73 "
        "factorial grid of operational perturbations:")
    pdf.eq(f"x\u2085 \u2208 {{ x\u2085* \u2212 2,  x\u2085*,  x\u2085* + 2 }}      (3 levels)")
    pdf.eq(f"x\u2086 \u2208 {{ x\u2086* \u2212 10\u2074,  x\u2086*,  x\u2086* + 10\u2074 }}  (3 levels)")
    pdf.p("This yields 9 runs per candidate (27 total), covering the extreme corners of "
           "the operational tolerance region. The candidate with the lowest mean stress, "
           "smallest variability, and 100% constraint satisfaction is selected.")

    pdf.sub('Phase 5: Final Validation (23 runs)')
    pdf.p("The remaining 23 runs provide final verification: 20 random (x\u2085, x\u2086) "
           "perturbations via a 2D LHD within the operational tolerance, plus 3 material "
           "property perturbations to confirm local optimality.")

    # ══════════ 3. RESULTS ═════════════════════════════════════════
    pdf.sec('Results')

    pdf.sub('Exploratory Analysis')
    pdf.p(
        f"The initial 100 simulations reveal that stress spans a nearly 4\u00d7 range "
        f"[4.46\u00d710\u2078, 1.71\u00d710\u2079 Pa], and only 43% of designs satisfy the "
        "displacement constraint. Stress and displacement are strongly positively correlated "
        "(r = 0.80), meaning that optimizing for low stress naturally helps satisfy the "
        "displacement constraint.")

    pdf.fig(os.path.join(FIG, 'fig1_distributions.png'),
        'Figure 3. Distributions of stress (a) and displacement (b) from the initial 100-run LHD. '
        'Red dashed line: d* = 1.3\u00d710\u207b\u00b3.', w=125)

    pdf.sub('Sensitivity Analysis')
    pdf.p(
        f"The ARD length-scale parameters {theta}\u2c7c provide an interpretable variable importance "
        f"measure. Shorter {theta}\u2c7c means the GP output changes more rapidly with input j. "
        f"Relative importance is (1/{theta}\u2c7c) / \u03a3\u2096(1/{theta}\u2096).")

    pdf.tbl([f'Variable', f'Stress {theta}', 'Stress Imp.', f'Displ. {theta}', 'Displ. Imp.'],
        [[f'x\u2081 (Young\'s)', '5.38', '0.177', '10.00', '0.070'],
         [f'x\u2082 (Poisson\'s)', '5.57', '0.171', '1.60', '0.440'],
         [f'x\u2083 (CTE)', '3.16', '0.301', '5.05', '0.139'],
         [f'x\u2084 (Therm.Cond.)', '10.00', '0.095', '6.74', '0.104'],
         [f'x\u2085 (Cooling)', '6.63', '0.143', '10.00', '0.070'],
         [f'x\u2086 (Pressure)', '8.38', '0.114', '3.97', '0.177']],
        ws=[38, 28, 27, 28, 46])

    pdf.p(
        f"For stress, x\u2083 (CTE) has the shortest length-scale ({theta}\u2083 = 3.16), making it "
        "the most influential variable (30.1%), followed by x\u2081 (17.7%) and x\u2082 (17.1%). "
        "Raw Pearson correlations confirm this: |r(x\u2083, stress)| = 0.87, far exceeding all "
        "others (< 0.39). For displacement, x\u2082 shows a short length-scale (1.60) due to a "
        "local nonlinearity, but the dominant global driver remains x\u2083 (|r| = 0.90).")

    pdf.fig(os.path.join(FIG, 'fig5_sensitivity.png'),
        f'Figure 4. Variable importance from ARD (1/{theta}, normalized). Blue: material; orange: operational.', w=130)
    pdf.fig(os.path.join(FIG, 'fig6_main_effects.png'),
        f'Figure 5. Main effects: GP prediction as each input varies, others at center. '
        f'Shaded: {pm}2{sigma}. Red dashed: d*.', w=145)

    pdf.sub('Optimization Convergence')
    pdf.tbl(['Stage', 'Cumul. Runs', 'Best Stress', 'Improv.'],
        [['Initial LHD', '100', f'4.461\u00d710\u2078', '\u2014'],
         ['+ Batch 1 (+20)', '120', f'2.868\u00d710\u2078', '35.7%'],
         ['+ Batch 2 (+20)', '140', f'2.736\u00d710\u2078', '38.7%'],
         ['+ Batches 3\u20138 (+110)', '250', f'2.636\u00d710\u2078', '40.9%']],
        ws=[45, 32, 40, 50])
    pdf.p("The first 20 sequential runs achieved the largest improvement (35.7%), as the "
           "GP rapidly identified the low-CTE corner. Subsequent batches refined with diminishing "
           "returns, indicating convergence.")

    pdf.fig(os.path.join(FIG, 'fig7_convergence.png'),
        'Figure 6. Convergence: (a) stress (blue=feasible, red=infeasible; green=best). '
        '(b) displacement with d*. Gray dashed: end of LHD.', w=130)

    pdf.sub('Recommended Design')
    pdf.tbl(['Parameter', 'Optimal Value', 'Unit', 'Note'],
        [[f'x\u2081: Young\'s Mod.', f'2.000\u00d710\u00b9\u00b9', 'Pa', 'Lower bound'],
         [f'x\u2082: Poisson\'s Ratio', '0.477', '\u2014', 'Near upper bound'],
         [f'x\u2083: CTE', f'5.000\u00d710\u207b\u2076', f'K{minus1}', 'Lower bound'],
         [f'x\u2084: Therm. Cond.', '5.0', 'W/m/K', 'Lower bound'],
         [f'x\u2085: Cooling Temp', '50.0', '\u00b0C', 'Lower bound'],
         [f'x\u2086: Pressure Load', f'4.049\u00d710\u2075', 'Pa', 'Mid-upper']],
        ws=[42, 32, 22, 71])

    pdf.p("The optimizer pushes CTE to its minimum, consistent with the sensitivity analysis. "
           "Young's Modulus is at its lower bound (softer material absorbs deformation without "
           "high stress), and cooling temperature is at the minimum (maximum cooling). "
           "Poisson's Ratio is near its upper bound (0.477), allowing lateral expansion "
           "that relieves stress concentrations. Three variables at their bounds suggests "
           "that expanding the design ranges could yield further improvements.")

    # Insert optimal_design.png
    pdf.fig(os.path.join(FIG, 'optimal_design.png'),
        'Figure 7. Simulated von Mises stress profile for the recommended blade design. '
        'The color map shows stress intensity across the blade surface; the predominantly '
        f'blue coloring confirms uniformly low stress (~2.6\u00d710\u2078 Pa).', w=120)

    pdf.sub('Robustness Under Operational Uncertainty')
    pdf.p("The 3\u00d73 factorial grid tests each candidate at 9 extreme combinations "
           "of operational perturbations:")
    pdf.tbl(['Candidate', f'E[stress]', f'Std[stress]', 'CV', 'Max disp.', 'Feasible?'],
        [['C1 (best)', f'2.650\u00d710\u2078', f'9.47\u00d710\u2075', '0.36%', f'7.10\u00d710\u207b\u2074', '9/9'],
         ['C2', f'2.697\u00d710\u2078', f'1.32\u00d710\u2076', '0.49%', f'6.57\u00d710\u207b\u2074', '9/9'],
         ['C3', f'2.685\u00d710\u2078', f'1.80\u00d710\u2076', '0.67%', f'6.75\u00d710\u207b\u2074', '9/9']],
        ws=[28, 30, 28, 17, 30, 34])
    pdf.p("All three candidates achieve 100% feasibility. Candidate 1 has the lowest mean "
           "stress and smallest variability (CV = 0.36%).")

    pdf.fig(os.path.join(FIG, 'fig8_robust.png'),
        'Figure 8. Robust comparison: stress (a) and displacement (b) boxplots for 3 candidates, '
        f'each on a 3\u00d73 grid of (x\u2085, x\u2086) perturbations.', w=120)

    pdf.sub('Final Validation')
    pdf.tbl(['Metric', 'Value'],
        [[f'E[stress] (20 runs)', f'2.644\u00d710\u2078 Pa'],
         ['Std[stress]', f'7.04\u00d710\u2075 Pa'],
         ['CV[stress]', '0.27%'],
         ['Max displacement', f'7.10\u00d710\u207b\u2074 m'],
         ['P(feasible)', '20/20 = 100%'],
         ['Safety margin vs d*', '45.4%'],
         [f'Material nearby (3 runs)', f'All > 2.78\u00d710\u2078 Pa']],
        ws=[80, 87])
    pdf.p("All 20 perturbation runs satisfy the constraint, with worst-case displacement "
           "45% below d*. The 3 material perturbation runs all produce higher stress, "
           "confirming a local optimum.")

    pdf.fig(os.path.join(FIG, 'fig9_validation.png'),
        'Figure 9. Final validation: stress (a) and displacement (b) under 20 random perturbations.', w=120)

    # ══════════ 4. DISCUSSION ═════════════════════════════════════
    pdf.sec('Discussion')

    pdf.sub('Engineering Recommendations')
    pdf.p("Three recommendations emerge: (1) prioritize alloys with the lowest CTE \u2014 "
           "it is the dominant factor (|r| = 0.87 for stress, 0.90 for displacement, "
           f"shortest {theta} = 3.16); (2) operate the cooling system at the lowest achievable "
           f"temperature; (3) current operational tolerances ({pm}2\u00b0C, {pm}10\u2074 Pa) "
           "are safely within the design's robustness envelope (CV < 1%, 100% feasibility).")

    pdf.sub('Budget Allocation')
    pdf.p("All 300 runs used: 100 initial (33%), 150 sequential (50%), 27 robust grid (9%), "
           "23 final validation (8%). The two-stage validation \u2014 structured 3\u00d73 grid then "
           "random perturbations \u2014 provides layered evidence of robustness.")
    pdf.fig(os.path.join(FIG, 'fig10_budget.png'), 'Figure 10. Budget allocation.', w=85)

    pdf.sub('Computational Infrastructure')
    pdf.p("Each FEM simulation takes ~80 seconds, making sequential execution of 300 runs "
           "prohibitively slow (~6.7 hours). To accelerate data generation, we built a "
           "three-stage SLURM pipeline on the Duke Computing Cluster:")
    pdf.p("(1) Input generation: a MATLAB script produces the design matrix (LHD or EIC "
           "candidates) and writes it to a shared CSV file. "
           "(2) Parallel simulation: a SLURM array job dispatches up to 40 concurrent tasks, "
           "each reading one row from the CSV, calling the FEM simulator, and writing its "
           "result to an individual output file. "
           "(3) Result collection: a final job merges all individual outputs into a single "
           "summary CSV.")
    pdf.p("The pipeline is orchestrated by a single shell script (submit_all.sh) that "
           "chains the three stages via SLURM job dependencies (--dependency=afterok), "
           "ensuring correct execution order. With 40-way parallelism, a batch of 100 "
           "simulations completes in ~4 minutes wall-clock time (vs. ~2.2 hours sequential), "
           "a ~33\u00d7 speedup. This infrastructure enabled rapid iteration through the "
           "sequential optimization loop.")

    pdf.sub('Strengths and Limitations')
    pdf.p("Strengths: (1) maximin LHD provides excellent coverage; (2) GP validated via "
           "10-fold CV with honest re-fitting; (3) EIC balances exploitation and exploration "
           "while respecting constraints; (4) 3\u00d73 factorial grid systematically tests all "
           "extreme corners of operational uncertainty.")
    pdf.p("Limitations: (1) three variables hit their bounds, suggesting expanded ranges "
           f"(especially CTE below 5\u00d710\u207b\u2076) could improve performance; "
           "(2) GP accuracy degrades in the boundary region where the optimum lies; "
           "(3) our robust optimization is two-stage (optimize then validate), which is "
           "simpler but less principled than a fully integrated robust EIC.")

    # ══════════ 5. CONCLUSION ═════════════════════════════════════
    pdf.sec('Conclusion')
    pdf.p("Through a four-phase framework \u2014 maximin LHD, GP surrogate modeling, "
           "sequential EIC, and staged robustness validation \u2014 we identified a turbine blade "
           "design that reduces maximum stress by 41%. The recommended design achieves 100% "
           "displacement feasibility under all tested operational perturbations (3\u00d73 grid + "
           "20 random runs) with a 45% safety margin. CTE is the dominant design factor, and "
           "prioritizing low-CTE alloys is the single most impactful engineering action. "
           f"All 300 simulator evaluations were utilized, with the GP (CV R{sup2} > 0.994) "
           "enabling efficient convergence in 150 sequential runs.")

    # ══════════ APPENDIX ═════════════════════════════════════════
    pdf.add_page(); pdf._s = 0
    pdf.set_font('DJ', 'B', 13)
    pdf.cell(0, 7, 'Appendix', new_x='LMARGIN', new_y='NEXT'); pdf.ln(2)

    pdf.set_font('DJ', 'B', 10)
    pdf.cell(0, 5, 'A. Detailed Budget', new_x='LMARGIN', new_y='NEXT'); pdf.ln(1)
    pdf.tbl(['Phase', 'Runs', 'Cumul.', 'Description'],
        [['Initial LHD', '100', '100', 'Space-filling exploration'],
         ['Seq. Batches 1\u20132', '40', '140', 'First EIC batches'],
         ['Seq. Batches 3\u20138', '110', '250', 'Continued optimization'],
         ['Robust 3\u00d73 Grid', '27', '277', '3 candidates \u00d7 9 perturbations'],
         ['Final Validation', '23', '300', '20 random + 3 material']],
        ws=[40, 18, 22, 87])

    pdf.set_font('DJ', 'B', 10)
    pdf.cell(0, 5, 'B. Input\u2013Response Scatter Plots', new_x='LMARGIN', new_y='NEXT'); pdf.ln(1)
    pdf.fig(os.path.join(FIG, 'fig2_scatter.png'),
        'Figure A1. Each input vs. responses (100 LHD). Blue = feasible; red = infeasible.', w=150)

    pdf.set_font('DJ', 'B', 10)
    pdf.cell(0, 5, 'C. Software', new_x='LMARGIN', new_y='NEXT'); pdf.ln(1)
    pdf.p("Simulator: MATLAB R2022b (simulator.p). Analysis: Python 3.9 (NumPy, SciPy, "
          "scikit-learn, Matplotlib, Pandas). GP: sklearn GaussianProcessRegressor with "
          f"Mat\u00e9rn-5/2 + ARD. Compute: Duke Computing Cluster (SLURM, 40-way parallel). "
          "~80 sec per simulation.")

    pdf.output(OUT)
    print(f'Report saved: {OUT}  ({pdf.page_no()} pages)')


if __name__ == '__main__':
    build()
