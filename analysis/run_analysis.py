"""
Turbine Blade Optimization -- Complete Analysis & Figure Generation
===================================================================
Runs on the final 300-run dataset (100 LHD + 150 sequential + 27 robust + 23 validation).
Generates all figures for the report.

Usage:  python3 analysis/run_analysis.py
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.model_selection import KFold
from scipy import stats
import os, warnings
warnings.filterwarnings('ignore')

# ── Constants ────────────────────────────────────────────────────────────────
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(PROJECT, "figures"); os.makedirs(FIG, exist_ok=True)
VARS   = ['x1','x2','x3','x4','x5','x6']
LABELS = ["Young's Mod.","Poisson's Ratio","CTE","Therm. Cond.",
          "Cooling Temp","Pressure Load"]
LB = np.array([200e9, 0.1, 5e-6, 5., 50., 1e5])
UB = np.array([300e9, 0.49, 1.5e-5, 15., 350., 4.8e5])
D_STAR = 1.3e-3
N_LHD, N_SEQ, N_ROB, N_VAL = 100, 150, 27, 23
encode = lambda x: (np.asarray(x)-LB)/(UB-LB)

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(PROJECT, "data", "all_results.csv"))
assert len(df) == 300, f"Expected 300 runs, got {len(df)}"
X = encode(df[VARS].values); ys = df['stress'].values; yd = df['displacement'].values
feas = yd < D_STAR
X0, s0, d0 = X[:N_LHD], ys[:N_LHD], yd[:N_LHD]; feas0 = d0 < D_STAR
print(f"Loaded 300 runs: {N_LHD} LHD + {N_SEQ} seq + {N_ROB} robust + {N_VAL} valid\n")

# ═════════════════════════════════════════════════════════════════════════════
# 1. EDA
# ═════════════════════════════════════════════════════════════════════════════
print("="*60+"\n1. EDA\n"+"="*60)
print(f"  Stress:   [{s0.min():.3e}, {s0.max():.3e}]  mean={s0.mean():.3e}")
print(f"  Displ:    [{d0.min():.3e}, {d0.max():.3e}]  mean={d0.mean():.3e}")
print(f"  Feasible: {feas0.sum()}/100 ({feas0.mean():.0%})")
print(f"  corr(stress,displ) = {np.corrcoef(s0,d0)[0,1]:.3f}")

fig,ax = plt.subplots(1,2,figsize=(11,4))
ax[0].hist(s0,20,edgecolor='k',color='steelblue',alpha=.7)
ax[0].set_xlabel('Stress (Pa)'); ax[0].set_ylabel('Count')
ax[1].hist(d0,20,edgecolor='k',color='darkorange',alpha=.7)
ax[1].axvline(D_STAR,c='red',ls='--',lw=2,label=f'd*={D_STAR:.1e}')
ax[1].set_xlabel('Displacement (m)'); ax[1].set_ylabel('Count')
ax[1].legend()
plt.tight_layout(); plt.savefig(f'{FIG}/fig1_distributions.png',dpi=150); plt.close()

fig,axes = plt.subplots(2,6,figsize=(22,7))
for j in range(6):
    for r,(y,nm) in enumerate([(s0,'Stress'),(d0,'Displacement')]):
        a=axes[r,j]
        a.scatter(X0[~feas0,j],y[~feas0],s=12,alpha=.5,c='red',label='Infeasible')
        a.scatter(X0[feas0,j],y[feas0],s=12,alpha=.5,c='steelblue',label='Feasible')
        a.set_xlabel(VARS[j]);
        if j==0: a.set_ylabel(nm)
        if r==1: a.axhline(D_STAR,c='red',ls='--',lw=1)
        if j==5 and r==0: a.legend(fontsize=7)
plt.tight_layout(); plt.savefig(f'{FIG}/fig2_scatter.png',dpi=150); plt.close()

# ═════════════════════════════════════════════════════════════════════════════
# 2. GP MODEL + DIAGNOSTICS
# ═════════════════════════════════════════════════════════════════════════════
print("\n"+"="*60+"\n2. GP MODELS (trained on 100 LHD)\n"+"="*60)

kern = ConstantKernel(1.,(1e-3,1e3))*Matern(
    length_scale=np.ones(6)*.5,length_scale_bounds=(1e-2,10.),nu=2.5
)+WhiteKernel(1e-6,(1e-10,1e-2))

gp_s = GaussianProcessRegressor(kernel=kern,n_restarts_optimizer=20,
                                 normalize_y=True,random_state=42)
gp_d = GaussianProcessRegressor(kernel=kern,n_restarts_optimizer=20,
                                 normalize_y=True,random_state=42)
gp_s.fit(X0,s0); gp_d.fit(X0,d0)
print(f"  Stress  kernel: {gp_s.kernel_}")
print(f"  Displ.  kernel: {gp_d.kernel_}")

# 10-fold CV
print("\n  10-fold CV (re-fit each fold):")
cv = {}
for lab,y in [('Stress',s0),('Displacement',d0)]:
    pr=np.zeros(N_LHD); st=np.zeros(N_LHD)
    for tr,te in KFold(10,shuffle=True,random_state=42).split(X0):
        g=GaussianProcessRegressor(kernel=kern,n_restarts_optimizer=10,
                                    normalize_y=True,random_state=42)
        g.fit(X0[tr],y[tr]); m,s2=g.predict(X0[te],return_std=True)
        pr[te]=m; st[te]=s2
    res=y-pr; r2=1-res.dot(res)/((y-y.mean())**2).sum()
    rmse=np.sqrt((res**2).mean()); mape=np.mean(np.abs(res/y))*100
    sres=res/np.maximum(st,1e-10); cov95=np.mean(np.abs(sres)<1.96)
    print(f"    {lab:14s}: R2={r2:.4f}  RMSE={rmse:.3e}  MAPE={mape:.2f}%  95%-cov={cov95:.0%}")
    cv[lab]=dict(pr=pr,st=st,y=y,r2=r2,rmse=rmse,mape=mape,sres=sres,cov95=cov95)

# Fig 3: CV predicted vs actual
fig,axes=plt.subplots(1,2,figsize=(11,5))
for i,(nm,d) in enumerate(cv.items()):
    a=axes[i]; a.scatter(d['y'],d['pr'],s=18,alpha=.6,c='steelblue')
    lo,hi=min(d['y'].min(),d['pr'].min()),max(d['y'].max(),d['pr'].max())
    m=(hi-lo)*.05; a.plot([lo-m,hi+m],[lo-m,hi+m],'r--',lw=1.5)
    a.set_xlabel(f'Actual {nm}'); a.set_ylabel(f'Predicted {nm}')
    a.set_aspect('equal')
plt.tight_layout(); plt.savefig(f'{FIG}/fig3_cv.png',dpi=150); plt.close()

# Fig 4: QQ plot
fig,axes=plt.subplots(1,2,figsize=(11,5))
for i,(nm,d) in enumerate(cv.items()):
    a=axes[i]; sr=np.sort(d['sres']); n=len(sr)
    th=stats.norm.ppf((np.arange(1,n+1)-.5)/n)
    a.scatter(th,sr,s=18,alpha=.6,c='steelblue')
    a.plot([-3,3],[-3,3],'r--',lw=1.5)
    a.set_xlabel('Theoretical Quantiles'); a.set_ylabel('Standardized Residuals')
    pass
    a.set_xlim(-3.5,3.5); a.set_ylim(-3.5,3.5)
plt.tight_layout(); plt.savefig(f'{FIG}/fig4_qq.png',dpi=150); plt.close()

# ═════════════════════════════════════════════════════════════════════════════
# 3. SENSITIVITY (ARD length-scale)
# ═════════════════════════════════════════════════════════════════════════════
print("\n"+"="*60+"\n3. SENSITIVITY (ARD length-scale)\n"+"="*60)
for lab,gp in [('Stress',gp_s),('Displacement',gp_d)]:
    ls=gp.kernel_.k1.k2.length_scale
    imp=1./ls; imp_n=imp/imp.sum()
    print(f"\n  {lab} GP length-scales & importance:")
    print(f"  {'Var':>4s}  {'theta':>8s}  {'1/theta':>8s}  {'rel.imp':>8s}")
    for j in range(6):
        print(f"  {VARS[j]:>4s}  {ls[j]:>8.3f}  {imp[j]:>8.4f}  {imp_n[j]:>8.3f}")

# Fig 5: sensitivity bar chart (ARD)
fig,axes=plt.subplots(1,2,figsize=(12,4.5))
colors=['steelblue']*4+['darkorange']*2
for i,(lab,gp) in enumerate([('Stress',gp_s),('Displacement',gp_d)]):
    ls=gp.kernel_.k1.k2.length_scale; imp=1./ls; imp_n=imp/imp.sum()
    a=axes[i]; a.bar(VARS,imp_n,color=colors,edgecolor='k',alpha=.8)
    a.set_ylabel('Relative Importance (1/length-scale)')
    a.set_ylim(0,max(imp_n)*1.3)
    for k,v in enumerate(imp_n): a.text(k,v+.008,f'{v:.3f}',ha='center',fontsize=9)
plt.tight_layout(); plt.savefig(f'{FIG}/fig5_sensitivity.png',dpi=150); plt.close()

# Fig 6: main effects
fig,axes=plt.subplots(2,6,figsize=(22,7)); ng=200; ctr=np.full(6,.5)
for j in range(6):
    zg=np.tile(ctr,(ng,1)); zg[:,j]=np.linspace(0,1,ng)
    for r,(gp,nm) in enumerate([(gp_s,'Stress'),(gp_d,'Displacement')]):
        mu,sig=gp.predict(zg,return_std=True); a=axes[r,j]
        a.plot(zg[:,j],mu,'b-',lw=2)
        a.fill_between(zg[:,j],mu-2*sig,mu+2*sig,alpha=.2,color='steelblue')
        a.set_xlabel(VARS[j])
        if j==0: a.set_ylabel(nm)
        if r==1: a.axhline(D_STAR,c='red',ls='--',lw=1)
plt.tight_layout(); plt.savefig(f'{FIG}/fig6_main_effects.png',dpi=150); plt.close()

# ═════════════════════════════════════════════════════════════════════════════
# 4. OPTIMIZATION CONVERGENCE
# ═════════════════════════════════════════════════════════════════════════════
print("\n"+"="*60+"\n4. CONVERGENCE\n"+"="*60)
bc=np.full(N_LHD+N_SEQ,np.nan); cb=np.inf
for i in range(N_LHD+N_SEQ):
    if feas[i] and ys[i]<cb: cb=ys[i]
    if cb<np.inf: bc[i]=cb
print(f"  After LHD (100):   {bc[99]:.4e}")
print(f"  After Seq (250):   {bc[249]:.4e}")
print(f"  Improvement:       {(1-bc[249]/bc[99])*100:.1f}%")

fig,ax=plt.subplots(1,2,figsize=(12,4.5))
c=np.where(feas[:250],'steelblue','red')
ax[0].scatter(range(250),ys[:250],s=8,alpha=.4,c=c)
v=~np.isnan(bc); ax[0].plot(np.where(v)[0],bc[v],'g-',lw=2,label='Best feasible')
ax[0].axvline(100,c='gray',ls='--',alpha=.5,label='End of LHD')
ax[0].set_xlabel('Run'); ax[0].set_ylabel('Stress'); ax[0].legend(fontsize=8)
pass
ax[1].scatter(range(250),yd[:250],s=8,alpha=.4,c=c)
ax[1].axhline(D_STAR,c='red',ls='--',lw=1.5,label=f'd*={D_STAR:.1e}')
ax[1].axvline(100,c='gray',ls='--',alpha=.5)
ax[1].set_xlabel('Run'); ax[1].set_ylabel('Displacement'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(f'{FIG}/fig7_convergence.png',dpi=150); plt.close()

# ═════════════════════════════════════════════════════════════════════════════
# 5. ROBUST ANALYSIS (27 runs: 3 candidates x 9 grid)
# ═════════════════════════════════════════════════════════════════════════════
print("\n"+"="*60+"\n5. ROBUST ANALYSIS (3x3 grid)\n"+"="*60)
rob = df.iloc[N_LHD+N_SEQ : N_LHD+N_SEQ+N_ROB]
for c in range(3):
    ch = rob.iloc[c*9:(c+1)*9]
    s=ch['stress'].values; d=ch['displacement'].values
    print(f"  Candidate {c+1}: E[s]={s.mean():.4e}  std={s.std():.4e}  "
          f"CV={s.std()/s.mean()*100:.2f}%  max_d={d.max():.4e}  feas={(d<D_STAR).all()}")

# Fig 8: robust comparison
fig,axes=plt.subplots(1,2,figsize=(11,4.5))
labels_c=['C1','C2','C3']
box_s=[rob.iloc[c*9:(c+1)*9]['stress'].values for c in range(3)]
box_d=[rob.iloc[c*9:(c+1)*9]['displacement'].values for c in range(3)]
bp=axes[0].boxplot(box_s,labels=labels_c,patch_artist=True)
for b,col in zip(bp['boxes'],['steelblue','darkorange','green']): b.set_facecolor(col)
axes[0].set_ylabel('Stress (Pa)')
bp2=axes[1].boxplot(box_d,labels=labels_c,patch_artist=True)
for b,col in zip(bp2['boxes'],['steelblue','darkorange','green']): b.set_facecolor(col)
axes[1].axhline(D_STAR,c='red',ls='--',lw=1.5,label=f'd*={D_STAR:.1e}')
axes[1].set_ylabel('Displacement (m)'); axes[1].legend()
plt.tight_layout(); plt.savefig(f'{FIG}/fig8_robust.png',dpi=150); plt.close()

# ═════════════════════════════════════════════════════════════════════════════
# 6. FINAL VALIDATION (23 runs)
# ═════════════════════════════════════════════════════════════════════════════
print("\n"+"="*60+"\n6. FINAL VALIDATION\n"+"="*60)
val = df.tail(N_VAL)
val_op = val.head(20); val_mat = val.tail(3)
s_v=val_op['stress'].values; d_v=val_op['displacement'].values
print(f"  Operational (20): E[s]={s_v.mean():.4e}  std={s_v.std():.4e}  "
      f"CV={s_v.std()/s_v.mean()*100:.2f}%  max_d={d_v.max():.4e}  feas={(d_v<D_STAR).all()}")
print(f"  Material nearby (3):")
for _,r in val_mat.iterrows():
    print(f"    stress={r['stress']:.4e}  disp={r['displacement']:.4e}")
print(f"  Safety margin: {(1-d_v.max()/D_STAR)*100:.1f}%")

fig,ax=plt.subplots(1,2,figsize=(11,4.5))
ax[0].hist(s_v,12,edgecolor='k',color='steelblue',alpha=.7)
ax[0].axvline(s_v.mean(),c='green',lw=2,label=f'Mean={s_v.mean():.3e}')
ax[0].set_xlabel('Stress'); ax[0].set_ylabel('Count')
ax[0].legend(fontsize=8)
ax[1].hist(d_v,12,edgecolor='k',color='darkorange',alpha=.7)
ax[1].axvline(D_STAR,c='red',ls='--',lw=2,label=f'd*={D_STAR:.1e}')
ax[1].set_xlabel('Displacement'); ax[1].set_ylabel('Count')
ax[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(f'{FIG}/fig9_validation.png',dpi=150); plt.close()

# Budget pie
fig,ax=plt.subplots(figsize=(6,4))
ax.bar(['Initial\nLHD','Sequential\nEIC','Robust\n3x3 Grid','Final\nValidation'],
       [100,150,27,23],color=['steelblue','darkorange','green','purple'],edgecolor='k',alpha=.8)
for k,v in enumerate([100,150,27,23]): ax.text(k,v+3,str(v),ha='center',fontweight='bold')
ax.set_ylabel('Runs')
plt.tight_layout(); plt.savefig(f'{FIG}/fig10_budget.png',dpi=150); plt.close()

print("\n"+"="*60+"\nAll figures saved to figures/\n"+"="*60)
