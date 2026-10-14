import json,tempfile,unittest
from pathlib import Path
from scripts.phase3 import core,protocol

class ProtocolTests(unittest.TestCase):
 def test_missing_assets_are_blocked_with_null_metrics(self):
  p=protocol.preflight({'stage':'validation','model':{'checkpoint':None},'data':{'manifest':None}})
  self.assertEqual(p['status'],'blocked_resource')
  self.assertIsNone(p['clean_prediction']);self.assertIsNone(p['estimated_campaign_seconds'])
  self.assertTrue(any('checkpoint' in x for x in p['blockers']))
 def test_test_evaluation_requires_frozen_exact_config(self):
  with tempfile.TemporaryDirectory() as d:
   lock=Path(d)/'lock.json';core.atomic_json(lock,{'status':'draft'})
   cfg={'stage':'official_test','preregistration':str(lock)}
   with self.assertRaises(ValueError):protocol.require_test_lock(cfg)
   core.atomic_json(lock,{'status':'frozen','final_config_sha256':'wrong','source_fingerprint':'wrong'})
   with self.assertRaises(ValueError):protocol.require_test_lock(cfg)
 def test_resume_rejects_tampered_artifact(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'candidate.jsonl';a.write_text('real record\n')
   r={'status':'completed','config_sha256':'cfg','source_fingerprint':'src','input_sha256':'input','checkpoint_sha256':'ckpt','artifacts':{str(a):core.file_hash(a)}}
   self.assertTrue(protocol.can_resume(r,'cfg','src','input','ckpt'))
   a.write_text('truncated')
   self.assertFalse(protocol.can_resume(r,'cfg','src','input','ckpt'))
 def test_manifest_rejects_duplicate_ids_and_test_leakage(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'manifest.csv';p.write_text('example_id,label,dataset_split,events_path,events_sha256\n1,0,official_test,a.npz,abc\n')
   with self.assertRaises(ValueError):protocol.read_manifest(p,'validation')
   p.write_text('example_id,label,dataset_split,events_path,events_sha256\n1,0,validation,a.npz,abc\n1,0,validation,b.npz,def\n')
   with self.assertRaises(ValueError):protocol.read_manifest(p,'validation')
 def test_clean_test_gate_rejects_partial_dataset(self):
  with self.assertRaises(ValueError):protocol.require_complete_clean_test([{'example_id':i} for i in range(100)],'official_test')
 def test_unsafe_run_id_is_rejected(self):
  with self.assertRaises(ValueError):protocol.run_directory('../outside')

class ReviewGateTests(unittest.TestCase):
 def test_temp_cannot_claim_ce_search(self):
  with self.assertRaises(ValueError):protocol.validate_attack_config({'attack':{'name':'TEMP','objective':'ce','requested_Q':21}})
 def test_resume_identity_rejects_environment_or_config_change(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);cfg={'run_id':'fixture'};env={'torch':'2.5.1','cuda_available':False,'cpu_model':'fixture','ram_available_bytes':100}
   protocol.bind_run(p,cfg,env)
   protocol.bind_run(p,cfg,{**env,'ram_available_bytes':50})
   with self.assertRaises(ValueError):protocol.bind_run(p,cfg,{**env,'torch':'2.9.1'})
   with self.assertRaises(ValueError):protocol.bind_run(p,{**cfg,'steps':50},env)

if __name__=='__main__':unittest.main()
