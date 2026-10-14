"""Hand-checked synthetic fixtures; these are not N-MNIST experiment records."""
import math,tempfile,unittest
from pathlib import Path
from scripts.phase3 import core

class ContractTests(unittest.TestCase):
 def setUp(self):
  self.clean=core.Events(ids=(10,11,12),x=(0,1,1),y=(0,1,1),p=(0,1,0),t=(0.,5.,10.))
 def candidate(self,i,t,logits):return core.Candidate(i,self.clean.with_times(t),tuple(logits))
 def test_validity_rejects_identity_coordinate_count_bounds_order_and_nan(self):
  # A validator omitting any raw-event invariant must fail one of these cases.
  for changed in [core.Events((10,11,99),self.clean.x,self.clean.y,self.clean.p,self.clean.t),core.Events(self.clean.ids,(1,1,1),self.clean.y,self.clean.p,self.clean.t),core.Events((10,11),(0,1),(0,1),(0,1),(0.,5.)),self.clean.with_times((0,7,10)),self.clean.with_times((0,5,-1)),self.clean.with_times((0,math.nan,10))]:
   self.assertFalse(core.validity(self.clean,changed,1)['valid'])
  self.assertTrue(core.validity(self.clean,self.clean.with_times((0,6,10)),1)['valid'])
 def test_projection_enforces_intervals_order_and_window(self):
  t=core.feasible((2,3,20),self.clean.t,1)
  self.assertEqual(t,(1.,4.,10.))
  self.assertTrue(core.validity(self.clean,self.clean.with_times(t),1)['valid'])
 def test_maximum_ce_can_miss_success_on_identical_candidates(self):
  # A: true probability .4, competitors .35/.25 -> correct, higher CE.
  # B: true probability .45, competing .5/.05 -> wrong, lower CE.
  a=self.candidate(0,self.clean.t,[math.log(.4),math.log(.35),math.log(.25)])
  b=self.candidate(1,(0,6,10),[math.log(.45),math.log(.5),math.log(.05)])
  result=core.select(self.clean,[a,b],0,1,'ce')
  self.assertEqual(result['legacy_output'],0)
  self.assertEqual(result['success_priority_output'],1)
  self.assertEqual(result['first_success_candidate'],1)
  self.assertTrue(result['any_valid_success']);self.assertFalse(result['legacy_success'])
  self.assertEqual(result['best_so_far'],[False,True])
 def test_invalid_misclassification_never_counts(self):
  clean=self.candidate(0,self.clean.t,[2.,0.])
  invalid=self.candidate(1,(0,8,10),[0.,5.])
  out=core.select(self.clean,[clean,invalid],0,1,'ce')
  self.assertFalse(out['any_valid_success']);self.assertEqual(out['success_priority_output'],0)
 def test_zero_margin_tie_uses_actual_argmax(self):
  c=self.candidate(0,self.clean.t,[1.,1.,0.])
  self.assertTrue(core.select(self.clean,[c],1,1,'margin')['any_valid_success'])
  self.assertFalse(core.select(self.clean,[c],0,1,'margin')['any_valid_success'])
 def test_missing_or_failed_record_does_not_become_survivor(self):
  good={'example_id':1,'status':'completed','clean_correct':True,'any_valid_success':False}
  for records in [[good],[good,{'example_id':2,'status':'failed'}]]:
   out=core.aggregate(records,[1,2])
   self.assertIsNone(out['asr']);self.assertEqual(out['planned_denominator'],2)
   self.assertEqual(out['missing_or_failed'],[2])
  out=core.aggregate([good,dict(good,example_id=2,any_valid_success=True)],[1,2])
  self.assertEqual(out['asr'],.5)
  with self.assertRaises(ValueError):core.aggregate([good,good],[1,2])
 def test_stratified_manifest_reproducible_shortage_not_duplicated(self):
  rows=[{'example_id':i,'label':i//3} for i in range(6)]
  chosen=core.stratified_manifest(rows,5,17,classes=2)
  self.assertEqual(chosen,core.stratified_manifest(list(reversed(rows)),5,17,classes=2))
  self.assertEqual(len(set(x['example_id'] for x in chosen)),5)
  shortage=core.stratified_manifest(rows,10,17,classes=2)
  self.assertEqual(len(shortage),6)
 def test_state_metrics_reject_non_normalized_states(self):
  m=core.state_metrics([1+0j,0j],[0j,1+0j],[1,0],[0,1])
  self.assertEqual(m['squared_fidelity'],0);self.assertEqual(m['trace_distance'],1)
  self.assertEqual(m['total_variation'],1)
  with self.assertRaises(ValueError):core.state_metrics([2+0j,0j],[1+0j,0j],[1,0],[1,0])
 def test_schedule_consumption_and_best_so_far_are_monotone(self):
  self.assertEqual(core.temp_schedule(21),(13,4,2,21))
  self.assertEqual(core.temp_schedule(41),(13,4,7,41))
  self.assertEqual(core.temp_schedule(400),(150,4,62,398))
  candidates=[self.candidate(0,self.clean.t,[2,0]),self.candidate(1,self.clean.t,[0,2]),self.candidate(2,self.clean.t,[2,0])]
  self.assertEqual(core.select(self.clean,candidates,0,1,'ce')['best_so_far'],[False,True,True])
 def test_state_margin_bound_checks_every_competitor(self):
  out=core.margin_bound([.8,.2],[.7,.3],[[1.,0.],[0.,1.]],[0.,0.],0,.2)
  self.assertTrue(out['all_bounds_hold']);self.assertTrue(out['sufficient_positive'])
  self.assertAlmostEqual(out['rows'][0]['lower_bound'],.2)

if __name__=='__main__':unittest.main()
