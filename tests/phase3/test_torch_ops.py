"""CPU correctness tests with synthetic events/untrained models, never research results."""
import ast,math,unittest
from pathlib import Path
import numpy as np
import torch
from scripts.phase3 import core,torch_ops as ops

torch.set_num_threads(2)
class TorchContractTests(unittest.TestCase):
 def setUp(self):
  self.events=core.Events((0,1,2),(0,0,0),(0,0,0),(0,0,0),(0.,5.,10.))
 def test_hard_frame_counts_and_nonzero_surrogate_can_coexist(self):
  t=torch.tensor(self.events.t,dtype=torch.float32,requires_grad=True)
  f=ops.frames(self.events,t)
  self.assertEqual(tuple(f.shape),(1,10,2,34,34))
  self.assertEqual(float(f[0,4,0,0,0]),1.)
  self.assertEqual(float(f.sum()),3.)
  grad,=torch.autograd.grad(f[0,4,0,0,0],t)
  self.assertAlmostEqual(float(grad[1]),-10/11,places=6)
  other=ops.frames(self.events,t.detach()+torch.tensor([0.,.001,0.]))
  self.assertTrue(torch.equal(f,other))
 def test_cap_does_not_reinterpret_event_count(self):
  e=core.Events(tuple(range(300)),(0,)*300,(0,)*300,(0,)*300,(0.,)*300)
  self.assertEqual(float(ops.frames(e,torch.tensor(e.t)).sum()),255.)
  self.assertEqual(len(e.ids),300)
 def test_canonical_recovered_adapter_agrees_exactly(self):
  # Execute only the pure recovered function AST, not its runner/import side effects.
  p=ops.SOURCE/'scripts/run_nmnist_attack_protocol_v2_canonical_seed42.py'
  tree=ast.parse(p.read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='canonical_frames_torch')
  ns={'torch':torch,'np':np};exec(compile(ast.Module([node],type_ignores=[]),str(p),'exec'),ns)
  t=torch.tensor([[0.,5.,10.],[0.,6.,10.]],dtype=torch.float32)
  raw={k:np.array(getattr(self.events,k)) for k in ['x','y','p','t']}
  self.assertTrue(torch.equal(ops.frames(self.events,t),ns[node.name](raw,t)))
 def test_full_qsnn_resets_between_calls_and_batch_permutation(self):
  torch.manual_seed(42);model=ops.build_model('qsnn').eval()
  a=ops.frames(self.events,torch.tensor(self.events.t));b=a.flip(1)
  with torch.no_grad():
   first=model(a);model(b);again=model(a)
   pair=model(torch.cat([a,b]));rev=model(torch.cat([b,a])).flip(0)
  self.assertTrue(torch.equal(first,again))
  self.assertTrue(torch.allclose(pair,rev,atol=1e-5,rtol=1e-5))
  self.assertFalse(any(m.training for m in model.modules()))
 def test_quantum_state_export_parity_and_smooth_gate_gradcheck(self):
  torch.manual_seed(3);model=ops.build_model('qsnn').eval()
  h=torch.tensor([[.1,.2,-.2,.3,.1,-.1,.05,-.15]])
  probs=model.quantum(h)
  state=model.quantum.forward_state(h)
  self.assertTrue(torch.allclose(state.abs().square(),probs,atol=1e-7))
  reference=ops.historical_models().QuantumHeadV2(n_blocks=2,learned_projection=True,two_axis_encoding=True,learned_measurement=True,topology='ring')
  reference.load_state_dict(model.quantum.state_dict())
  self.assertTrue(torch.allclose(reference(h),probs,atol=1e-7))
  base=torch.zeros((1,256),dtype=torch.complex128);base[:,0]=1
  f=lambda theta:model.quantum._ry(base,theta,0).abs().square()[:,0]
  self.assertTrue(torch.autograd.gradcheck(f,(torch.tensor([.37],dtype=torch.float64,requires_grad=True),),eps=1e-6,atol=1e-5))
 def test_literal_search_counts_and_validity(self):
  class Fixture(torch.nn.Module):
   def __init__(self):
    super().__init__();self.weight=torch.nn.Parameter(torch.linspace(0,1,10).reshape(1,10,1,1,1))
   def forward(self,x):
    v=(x*self.weight).sum((1,2,3,4));return torch.stack([v,-v],1)
  model=Fixture().eval()
  pgd,pc=ops.pgd(model,self.events,0,1.,steps=20,step_fraction=.2,seed=7,restarts=1,objective='ce')
  self.assertEqual(len(pgd),21);self.assertEqual(pc['search_forward_calls'],41);self.assertEqual(pc['backward_calls'],20)
  temp,tc=ops.temp(model,self.events,0,1.,requested_q=21,seed=7,chunk=64)
  self.assertEqual(len(temp),21);self.assertEqual(tc['search_forward_calls'],5);self.assertEqual(tc['search_forward_equivalents'],21)
  for c in list(pgd)+list(temp):self.assertTrue(core.validity(self.events,c.events,1.)['valid'])
 def test_no_entanglers_variant_keeps_nonlinear_probability_readout(self):
  model=ops.build_model('qsnn_no_entanglers',freeze_frontend=True)
  self.assertEqual(model.head.in_features,256)
  self.assertTrue(all(not p.requires_grad for p in model.extractor.parameters()))
  x=torch.zeros((1,256),dtype=torch.complex64);x[0,0]=1
  self.assertTrue(torch.equal(model.quantum._entangle(x,0),x))
  classical=ops.build_model('classical_head',freeze_frontend=True)
  self.assertEqual(sum(p.numel() for p in classical.head.parameters()),2977)

if __name__=='__main__':unittest.main()
