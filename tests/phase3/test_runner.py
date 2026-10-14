import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from scripts.phase3 import core,runner

class RunnerTests(unittest.TestCase):
 def test_blocked_pilot_writes_no_synthetic_result(self):
  with tempfile.TemporaryDirectory() as d:
   cfg={'stage':'validation','run_id':'test-blocked','model':{'checkpoint':None},'data':{'manifest':None}}
   out=runner.pilot(cfg,Path(d))
   self.assertEqual(out['status'],'blocked_resource');self.assertIsNone(out['asr'])
   self.assertEqual(out['experimental_result_count'],0)
   self.assertFalse((Path(d)/'per_example.jsonl').exists())
 def test_cpu_attack_audit_and_resume_with_real_file_io_fixtures(self):
  # Unit integration only: an explicitly synthetic checkpoint+events, never stored in Reports results.
  import numpy as np,torch
  from scripts.phase3 import protocol,torch_ops
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);model=torch_ops.build_model('snn').eval()
   events=core.Events((0,1,2),(0,0,0),(0,0,0),(0,0,0),(0.,5.,10.))
   with torch.no_grad():label=int(model(torch_ops.frames(events,torch.tensor(events.t))).argmax(1))
   ck=root/'model.pt';torch.save({'seed':42,'model_state':model.state_dict()},ck)
   metadata={'model_id':'synthetic_fixture_only','variant':'snn','training_seed':42,'frontend_seed':None,'source_commit':'unit_test',
    'preprocessing':{'bins':10,'window':'clean_endpoints_inclusive','cap':255,'frontend_scale':8,'sensor_size':[34,34]}}
   meta=root/'metadata.json';core.atomic_json(meta,metadata)
   event_path=root/'events.npz';np.savez(event_path,ids=np.array(events.ids),x=np.array(events.x),y=np.array(events.y),p=np.array(events.p),t=np.array(events.t),label=label)
   manifest=root/'manifest.csv';manifest.write_text('example_id,label,dataset_split,events_path,events_sha256\nfixture,'+str(label)+',validation,'+str(event_path)+','+core.file_hash(event_path)+'\n')
   cfg={'stage':'validation','run_id':'test-only','model':{'checkpoint':str(ck),'checkpoint_sha256':core.file_hash(ck),'metadata':str(meta),'metadata_sha256':core.file_hash(meta),'training_seed':42,'variant':'snn'},
    'data':{'manifest':str(manifest),'manifest_sha256':core.file_hash(manifest),'expected_n':1},'device':'cpu','attack':{'name':'PGD','objective':'ce','steps':1,'step_fraction':.2,'restarts':1,'seed':7,'epsilon_fraction':.05,'chunk':1},'full_trace_ids':[]}
   out=runner.attack(cfg,root/'run')
   self.assertEqual(out['status'],'completed');self.assertEqual(out['completed_count'],1)
   row=json.loads((root/'run/per_example.jsonl').read_text())
   self.assertEqual(row['candidate_count'],2);self.assertEqual(row['forward_count'],3);self.assertEqual(row['backward_count'],1)
   self.assertGreaterEqual(row['verification_forward_calls'],3)
   first_hash=core.file_hash(root/'run/per_example.jsonl')
   again=runner.attack(cfg,root/'run')
   self.assertEqual(first_hash,core.file_hash(root/'run/per_example.jsonl'))
   self.assertEqual(again['completed_count'],1)
   clean=runner.clean_eval(cfg,root/'clean')
   self.assertEqual(clean.get('checkpoint_sha256'),cfg['model']['checkpoint_sha256'])
   self.assertTrue((root/'clean/config.json').is_file())
   with self.assertRaises(ValueError):runner.clean_eval({**cfg,'extra_note':'changed'},root/'clean')

class SharedEvaluationTests(unittest.TestCase):
 def test_selection_effect_uses_same_verified_logits(self):
  import math
  e=core.Events((0,1),(0,0),(0,0),(0,0),(0.,10.))
  a=core.Candidate(0,e,tuple(map(math.log,[.45,.44,.11])))
  b=core.Candidate(1,e,tuple(map(math.log,[.4500001,.4500002,.0999997])))
  vb=core.Candidate(1,e,tuple(map(math.log,[.4499999,.4500002,.0999999])))
  out=runner.selection_audit(e,[a,b],[a,vb],0,1,'ce')
  self.assertEqual(out['search_legacy_output'],0)
  self.assertEqual(out['legacy_output'],1)
  self.assertFalse(out['legacy_missed_success'])
  self.assertTrue(out['reevaluation_changed_selection'])

if __name__=='__main__':unittest.main()
