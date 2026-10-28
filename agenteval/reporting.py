import math
import statistics
from collections import Counter


def wilson(k,n):
    if not n:return [0,0]
    z=1.96;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(center-half,4),round(center+half,4)]


def summarize(rows):
    groups={}
    for condition in sorted({r['condition'] for r in rows}):
        selected=[r for r in rows if r['condition']==condition];n=len(selected)
        calls=sum(len(r['calls']) for r in selected)
        errors=Counter(e for r in selected for e in r['errors'])
        seconds=sorted(r['seconds'] for r in selected)
        groups[condition]={
            'tasks':n,'success_rate':sum(r['success'] for r in selected)/n,
            'success_95ci':wilson(sum(r['success'] for r in selected),n),
            'answer_accuracy':sum(r['correct'] for r in selected)/n,
            'policy_compliance':sum(r['policy_compliant'] for r in selected)/n,
            'invalid_tool_call_rate':(errors['unknown_tool']+errors['tool_error'])/calls if calls else None,
            'protocol_errors':errors['protocol_error'],
            'mean_seconds':statistics.mean(seconds),'p95_seconds':seconds[math.ceil(.95*n)-1],
            'mean_generated_tokens':statistics.mean(r['tokens'] for r in selected),
            'failures':dict(Counter(r['failure'] for r in selected if r['failure'])),
            'categories':{c:{'n':sum(r['category']==c for r in selected),'successes':sum(r['success'] for r in selected if r['category']==c)} for c in sorted({r['category'] for r in selected})}}
    return groups


def markdown(metadata,summary):
    label='SCRIPTED HARNESS SMOKE TEST — NOT MODEL RESULTS' if metadata['backend']=='scripted_smoke' else 'LOCAL MODEL EXPERIMENT'
    lines=['# AgentEval Lab report', '',label,'',f"Model: `{metadata['model']}` | split: {metadata['split']} | dataset SHA-256: `{metadata['dataset_sha256']}`",'', '| Condition | Tasks | Success | Accuracy | 95% interval | Mean seconds |', '|---|---:|---:|---:|---|---:|']
    for name,s in summary.items():
        lines.append(f"| {name} | {s['tasks']} | {s['success_rate']:.1%} | {s['answer_accuracy']:.1%} | {s['success_95ci']} | {s['mean_seconds']:.3f} |")
    lines+=['','Success requires the right answer, successful use of required tools and no prohibited-tool attempt.','', 'Conditions share greedy decoding, dataset and step limits. Structured adds a checklist; feedback adds recovery after invalid actions. Feedback may use more inference: compare tokens and latency as well as success.','', 'Wilson intervals are descriptive task-level intervals. Tasks share templates and fixtures, so independence is weak; these are not population-level confidence claims.','', 'Limitations: synthetic data; small template-based task set; no standard external benchmark; direct prompt-injection probes only; no training or fine-tuning; no general safety or research-performance claim.']
    return '\n'.join(lines)+'\n'
