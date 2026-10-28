"""Read-only local dashboard; never substitutes sample data for uploaded results."""
import json
from pathlib import Path
import streamlit as st
from agenteval.reporting import summarize

st.set_page_config(page_title='AgentEval Lab',page_icon='🔬',layout='wide')
st.title('AgentEval Lab')
st.caption('Small language model tool-use reliability · experiment inspector')
runs=sorted([p for p in Path('results').glob('*') if (p/'summary.json').is_file()],reverse=True)
if not runs:
    st.info('No completed runs. Run python -m agenteval --backend smoke to verify the harness, or use --backend hf for model evaluation.')
    st.stop()
run=st.sidebar.selectbox('Experiment',runs,format_func=lambda p:p.name)
meta=json.loads((run/'metadata.json').read_text())
rows=[json.loads(s) for s in (run/'traces.jsonl').read_text().splitlines() if s]
if meta['backend']=='scripted_smoke':st.warning('SCRIPTED SMOKE TEST — these are software checks, not LLM benchmark results.')
else:st.success('Actual local model run: '+meta['model'])
st.code(f"Model: {meta['model']}\nRevision: {meta['model_revision']}\nSplit: {meta['split']}\nDataset: {meta['dataset_sha256']}")
summary=summarize(rows)
st.subheader('Controlled comparison')
st.dataframe([{'condition':k,**{m:v for m,v in s.items() if m not in ('categories','failures')}} for k,s in summary.items()],width='stretch')
st.bar_chart({k:v['success_rate'] for k,v in summary.items()})
st.caption('Success includes correct answer, required tool execution and no prohibited-tool attempt. Rates apply only to this synthetic benchmark.')
st.subheader('Inspect a trace')
condition=st.selectbox('Condition',list(summary))
category=st.selectbox('Category',['All']+sorted({r['category'] for r in rows}))
filtered=[r for r in rows if r['condition']==condition and (category=='All' or r['category']==category)]
failures=st.checkbox('Failures only')
if failures:filtered=[r for r in filtered if not r['success']]
if filtered:
    row=st.selectbox('Task',filtered,format_func=lambda r:r['task_id'])
    st.write({'expected':row['expected'],'answer':row['final'],'success':row['success'],'failure':row['failure']})
    for event in row['trace']:
        with st.expander(f"Step {event['step']} · {event.get('tool','final/protocol')} ",expanded=True):st.json(event)
else:st.info('No tasks match this filter.')
report_path=run/'report.md'
report_text=report_path.read_text() if report_path.exists() else json.dumps(summary,indent=2)
st.download_button('Download report',report_text,file_name='agenteval-report.md')
with st.expander('Reproducibility metadata'):st.json(meta)

st.subheader('Fresh study: model and policy comparison')
matrix=[]
for label in ('small','large'):
    folder=Path('results')/f'v3-{label}-test'
    if (folder/'summary.json').exists():
        metadata=json.loads((folder/'metadata.json').read_text())
        scores=json.loads((folder/'summary.json').read_text())
        for policy,scoreset in scores.items():
            matrix.append({'model':metadata['model'],'policy':policy,'successes':round(scoreset['success_rate']*scoreset['tasks']),'tasks':scoreset['tasks'],'success_rate':scoreset['success_rate'],'mean_tokens':scoreset['mean_generated_tokens'],'mean_seconds':scoreset['mean_seconds']})
if matrix:
    st.dataframe(matrix,width='stretch')
    st.caption('Fresh in-domain test: 15 tasks per model-policy pair. Same maximum budgets; realized costs differ. Earlier test scores use different data and should be compared separately.')
else:
    st.info('Run python run_study3.py to populate the fresh two-model comparison.')
if Path('EXPERIMENT_RESULTS.md').exists():
    st.download_button('Download experiment report',Path('EXPERIMENT_RESULTS.md').read_text(),file_name='AgentEval_Results.md')
