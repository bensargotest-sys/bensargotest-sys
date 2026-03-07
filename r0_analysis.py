import json
import numpy as np
from math import asin, sqrt
from scipy.stats import binomtest, beta, norm

# Load data
data_path = '/data/.openclaw/workspace/meld/research/systematic-results/r0-variance-gpqa_diamond-full-20260302-131948.json'
with open(data_path, 'r') as f:
    data = json.load(f)

results = data['results']
conditions = ['solo-gemini-flash', 'solo-grok-3', 'solo-grok-4.1-fast', 'meld-vote-trio', 'random']
n_questions = 50
n_runs = 3
n_total = n_questions * n_runs

def clopper_pearson_ci(k, n, alpha=0.05):
    if n == 0 or k < 0 or k > n:
        return 0.0, 1.0
    if k == 0:
        return 0.0, 1.0 - (alpha / 2)
    if k == n:
        return (alpha / 2), 1.0
    lower = beta.ppf(alpha / 2, k, n - k + 1)
    upper = beta.ppf(1 - alpha / 2, k + 1, n - k)
    return lower, upper

def compute_stats(corrects):
    k = sum(1 for c in corrects if c)
    n = len(corrects)
    p = k / n if n > 0 else 0
    ci_low, ci_high = clopper_pearson_ci(k, n)
    return p, (ci_low, ci_high), k, n

def cohens_h(p1, p2):
    if p1 <= 0 or p2 <= 0 or p1 >= 1 or p2 >= 1:
        return np.nan
    return 2 * (asin(np.sqrt(p1)) - asin(np.sqrt(p2)))

def mcnemar_test(correct_meld, correct_solo):
    b = sum(1 for m, s in zip(correct_meld, correct_solo) if not m and s)
    c = sum(1 for m, s in zip(correct_meld, correct_solo) if m and not s)
    discordant = b + c
    if discordant == 0:
        return 0.0, 1.0
    chi2 = (b - c) ** 2 / discordant
    pval = binomtest(c, discordant, p=0.5, alternative='two-sided').pvalue
    return chi2, pval

def power_calc(d, p1, p2, n, alpha=0.05):
    z_a = norm.ppf(1 - alpha / 2)
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    if se == 0:
        return 1.0
    z = d / se
    power = norm.cdf(-z_a - z) + 1 - norm.cdf(z_a - z)
    return power

def n_req_calc(d, p_bar, power=0.8, alpha=0.05):
    z_a = norm.ppf(1 - alpha / 2)
    z_b = norm.ppf(power)
    var = 2 * p_bar * (1 - p_bar)
    if d == 0 or var == 0:
        return float('inf')
    n = (z_a + z_b) ** 2 * var / d ** 2
    return n

# Function to get trials and domains
def get_trials(condition):
    cond_data = results.get(condition, [])
    trials = []
    domains = {}
    for q_idx in range(n_questions):
        if q_idx < len(cond_data):
            q_runs = cond_data[q_idx]
            if not q_runs:
                continue
            domain = q_runs[0].get('domain', 'Unknown')
            if domain not in domains:
                domains[domain] = {'corrects': [], 'n_q': 0}
            domains[domain]['n_q'] += 1
            for run_idx in range(min(n_runs, len(q_runs))):
                trial = q_runs[run_idx]
                is_correct = trial.get('correct', False)
                is_extracted = trial.get('extracted', '') != ''
                trials.append({
                    'correct': is_correct,
                    'extracted': is_extracted,
                    'domain': domain,
                    'q_idx': q_idx,
                    'run_idx': run_idx
                })
                domains[domain]['corrects'].append(is_correct)
        else:
            pass
    return trials, domains

# Compute stats
stats = {}
domain_stats = {}
for cond in conditions:
    trials, domains = get_trials(cond)
    corrects = [t['correct'] for t in trials]
    extracteds = [t['extracted'] for t in trials]
    p, ci, k, n = compute_stats(corrects)
    p_ext, _, k_ext, n_ext = compute_stats(extracteds)
    clean_corrects = [t['correct'] for t in trials if t['extracted']]
    p_clean, ci_clean, k_clean, n_clean = compute_stats(clean_corrects) if clean_corrects else (np.nan, (np.nan, np.nan), 0, 0)
    
    stats[cond] = {
        'overall_p': p,
        'overall_ci': ci,
        'ext_rate': p_ext,
        'clean_p': p_clean,
        'clean_ci': ci_clean,
        'n_correct': k,
        'n_extracted': n_clean
    }
    domain_stats[cond] = domains

# Paired comparisons
meld_cond = 'meld-vote-trio'
if meld_cond in results:
    meld_trials, _ = get_trials(meld_cond)
    solo_conds = [c for c in ['solo-gemini-flash', 'solo-grok-3', 'solo-grok-4.1-fast'] if c in results]
    
    comparisons = {}
    for solo in solo_conds:
        solo_trials, _ = get_trials(solo)
        min_len = min(len(meld_trials), len(solo_trials))
        correct_meld = [meld_trials[i]['correct'] for i in range(min_len)]
        correct_solo = [solo_trials[i]['correct'] for i in range(min_len)]
        extracted_meld = [meld_trials[i]['extracted'] for i in range(min_len)]
        extracted_solo = [solo_trials[i]['extracted'] for i in range(min_len)]
        
        chi2, pval = mcnemar_test(correct_meld, correct_solo)
        h = cohens_h(stats[meld_cond]['overall_p'], stats[solo]['overall_p'])
        
        paired_idx = [i for i in range(min_len) if extracted_meld[i] and extracted_solo[i]]
        n_paired = len(paired_idx)
        if n_paired > 0:
            cm_clean = [correct_meld[i] for i in paired_idx]
            cs_clean = [correct_solo[i] for i in paired_idx]
            chi2_clean, pval_clean = mcnemar_test(cm_clean, cs_clean)
            p_m_clean = sum(cm_clean) / n_paired
            p_s_clean = sum(cs_clean) / n_paired
            h_clean = cohens_h(p_m_clean, p_s_clean)
        else:
            chi2_clean, pval_clean, h_clean = np.nan, np.nan, np.nan
        
        comparisons[solo] = {
            'overall': {'chi2': chi2, 'pvalue': pval, 'h': h},
            'clean': {'chi2': chi2_clean, 'pvalue': pval_clean, 'h': h_clean, 'n_paired': n_paired}
        }

    # Agreement
    agree_correct = 0
    agree_total = 0
    disagree_correct = 0
    disagree_total = 0
    cond_data = results[meld_cond]
    for q_idx in range(min(n_questions, len(cond_data))):
        q_runs = cond_data[q_idx]
        for run_idx in range(min(n_runs, len(q_runs))):
            trial = q_runs[run_idx]
            inds = trial.get('individuals', [])
            if len(inds) >= 3:
                exts = [ind.get('extracted', '') for ind in inds[:3]]
                all_extracted = all(e != '' for e in exts)
                all_agree = all(e == exts[0] for e in exts)
                if all_agree and all_extracted:
                    agree_total += 1
                    if trial['correct']:
                        agree_correct += 1
                elif all_extracted:
                    disagree_total += 1
                    if trial['correct']:
                        disagree_correct += 1

    acc_agree = agree_correct / agree_total if agree_total > 0 else np.nan
    acc_disagree = disagree_correct / disagree_total if disagree_total > 0 else np.nan

    agreement_stats = {
        'acc_agree': acc_agree,
        'n_agree': agree_total,
        'acc_disagree': acc_disagree,
        'n_disagree': disagree_total
    }

    # Domain for MELD
    meld_domains = domain_stats[meld_cond]
    domain_acc = {d: sum(dom['corrects']) / len(dom['corrects']) for d, dom in meld_domains.items() if dom['corrects']}

    # Power
    p_meld = stats[meld_cond]['overall_p']
    p_grok3 = stats.get('solo-grok-3', {'overall_p': 0.25})['overall_p']
    d = p_meld - p_grok3
    p_bar = (p_meld + p_grok3) / 2
    observed_power = power_calc(d, p_meld, p_grok3, n_total)
    n_req = n_req_calc(d, p_bar)

    power_analysis = {
        'd': d,
        'observed_power': observed_power,
        'n_req': n_req
    }
else:
    comparisons = {}
    agreement_stats = {}
    domain_acc = {}
    power_analysis = {}
    acc_agree = np.nan
    acc_disagree = np.nan

# Generate MD
md_content = '# R0 Statistical Analysis\n\n## Overall Accuracy (Extraction Fails = Wrong)\n\n'
for cond in conditions:
    if cond in stats:
        p = stats[cond]['overall_p']
        ci = stats[cond]['overall_ci']
        md_content += f'- **{cond}**: {p*100:.1f}% (95% CI: {ci[0]*100:.1f}%–{ci[1]*100:.1f}%)\n'

md_content += '\n## Extraction Rates\n\n'
for cond in conditions:
    if cond in stats:
        p_ext = stats[cond]['ext_rate']
        md_content += f'- **{cond}**: {p_ext*100:.1f}%\n'

md_content += '\n## Accuracy on Clean Extractions\n\n'
for cond in conditions:
    if cond in stats:
        p_clean = stats[cond]['clean_p']
        if not np.isnan(p_clean):
            ci_clean = stats[cond]['clean_ci']
            n_ext = stats[cond]['n_extracted']
            md_content += f'- **{cond}**: {p_clean*100:.1f}% (95% CI: {ci_clean[0]*100:.1f}%–{ci_clean[1]*100:.1f}%, n={n_ext})\n'
        else:
            md_content += f'- **{cond}**: N/A\n'

if comparisons:
    md_content += '\n## Paired Comparisons MELD vs Solos (McNemar\'s Test)\n\n'
    for solo in solo_conds:
        if solo in comparisons:
            md_content += f'### vs {solo}\n\n'
            overall = comparisons[solo]['overall']
            h_str = f"{overall['h']:.3f}" if not np.isnan(overall['h']) else 'N/A'
            md_content += f"**Overall:** χ² = {overall['chi2']:.3f}, p = {overall['pvalue']:.4f}, Cohen\\'s h = {h_str}\n\n"
            clean = comparisons[solo]['clean']
            if clean['n_paired'] > 0:
                h_clean_str = f"{clean['h']:.3f}" if not np.isnan(clean['h']) else 'N/A'
                md_content += f"**Clean (n={clean['n_paired']})**: χ² = {clean['chi2']:.3f}, p = {clean['pvalue']:.4f}, Cohen\\'s h = {h_clean_str}\n\n"
            else:
                md_content += "**Clean:** No paired data\n\n"

if domain_acc:
    md_content += '\n## Per-Domain Breakdown (MELD)\n\n'
    for d in sorted(domain_acc):
        p = domain_acc[d]
        n_q = meld_domains[d]['n_q']
        n_trials = n_q * n_runs
        md_content += f'- **{d}** (n_q={n_q}, n_trials={n_trials}): {p*100:.1f}%\n'

if agreement_stats:
    md_content += '\n## Agreement-Accuracy in MELD Trio\n\n'
    if agreement_stats['n_agree'] > 0:
        md_content += f'- Agree (n={agreement_stats["n_agree"]}): {agreement_stats["acc_agree"]*100:.1f}%\n'
    if agreement_stats['n_disagree'] > 0:
        md_content += f'- Disagree (n={agreement_stats["n_disagree"]}): {agreement_stats["acc_disagree"]*100:.1f}%\n'

if power_analysis:
    md_content += '\n## Power Analysis (vs Best Solo)\n\n'
    d = power_analysis['d']
    md_content += f'- Effect size: +{d*100:.1f} pp\n'
    md_content += f'- Power at n=150: {power_analysis["observed_power"]*100:.1f}%\n'
    n_req = power_analysis['n_req']
    n_q_req = n_req / n_runs if n_req < float('inf') else float('inf')
    md_content += f'- N required for 80% power: {n_req:.0f} trials (~{n_q_req:.0f} questions)\n'

md_content += '\n## Interpretation\n\n'
if 'solo-grok-3' in comparisons:
    pval = comparisons['solo-grok-3']['overall']['pvalue']
    if pval < 0.05:
        md_content += '- MELD significantly outperforms best solo (p < 0.05).\n'
    else:
        md_content += f'- MELD advantage not significant (p = {pval:.4f}).\n'
else:
    md_content += '- Unable to perform significance test.\n'

if agreement_stats and agreement_stats['n_agree'] > 0 and agreement_stats['n_disagree'] > 0:
    if acc_agree > acc_disagree:
        md_content += '- Accuracy higher when models agree.\n'
    else:
        md_content += '- No positive correlation between agreement and accuracy.\n'

if power_analysis:
    if power_analysis['observed_power'] >= 0.8:
        md_content += '- Sample size sufficient for detection.\n'
    else:
        md_content += f'- Sample size underpowered ({power_analysis["observed_power"]*100:.1f}%).\n'

if meld_cond in stats and 'solo-grok-3' in stats:
    if stats[meld_cond]['clean_p'] > stats['solo-grok-3']['clean_p']:
        md_content += '- Advantage persists on clean extractions.\n'
    else:
        md_content += '- Advantage largely due to better extraction.\n'

# Write
md_path = '/data/.openclaw/workspace/meld/research/R0-STATISTICAL-ANALYSIS.md'
with open(md_path, 'w') as f:
    f.write(md_content)

print("Analysis complete.")
print(md_content)