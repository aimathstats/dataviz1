import streamlit as st # for streamlit
import io

import os
import sys
import json
import random
from ast import literal_eval
import numpy as np
import math
import torch
import torch.nn as nn
from torch.nn import functional as F
import time
from collections import defaultdict
from torch.utils.data.dataloader import DataLoader
from torch.utils.data import Dataset
import seaborn as sns
import matplotlib.pyplot as plt

# 例: ModuleDict を作る
modules = nn.ModuleDict({
    "linear1": nn.Linear(10, 20),
    "linear2": nn.Linear(20, 5),
})
# state_dict を保存
torch.save(modules.state_dict(), "modules.pth")

# 同じ構造の ModuleDict を用意してロード
modules2 = nn.ModuleDict({
    "linear1": nn.Linear(10, 20),
    "linear2": nn.Linear(20, 5),
})
modules2.load_state_dict(torch.load("modules.pth"))

# 例: ModuleDict（好きなモデルに置き換えてOK）
if "model" not in st.session_state:
    st.session_state.model = nn.ModuleDict({
        "linear1": nn.Linear(10, 20),
        "linear2": nn.Linear(20, 5),
    })
model = st.session_state.model

# ---- 1) state_dict をローカル保存（任意） ----
save_path = "model_state.pth"
if st.button("state_dict をローカルに保存"):
    torch.save(model.state_dict(), save_path)
    st.success(f"保存しました: {os.path.abspath(save_path)}")

# ---- 2) state_dict をダウンロード ----
buf = io.BytesIO()
torch.save(model.state_dict(), buf)
buf.seek(0)
st.download_button(
    label="state_dict をダウンロード (.pth)",
    data=buf,
    file_name="model_state.pth",
    mime="application/octet-stream",
)
# ----（おまけ）アップロードして復元 ----
up = st.file_uploader("state_dict をアップロードして読み込み", type=["pth"])
if up:
    state = torch.load(up, map_location="cpu")
    model.load_state_dict(state)
    st.success("ロード完了！")

########## for streamlit ##################
with st.sidebar:
    raw = st.text_input("4桁の数値", "9053", max_chars=4)
    d = ''.join(filter(str.isdigit, raw))[:4]
    idx_test = [[int(c) for c in d]] if len(d)==4 else None
    iters = st.radio("繰り返し数", [10, 500, 1500], index=0, horizontal=True)

#st.write("idx:", idx)
#st.write("繰り返し数:", iters)
############################################

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def setup_logging(config):
    """ monotonous bookkeeping """
    work_dir = config.system.work_dir
    # create the work directory if it doesn't already exist
    os.makedirs(work_dir, exist_ok=True)
    # log the args (if any)
    with open(os.path.join(work_dir, 'args.txt'), 'w') as f:
        f.write(' '.join(sys.argv))
    # log the config itself
    with open(os.path.join(work_dir, 'config.json'), 'w') as f:
        f.write(json.dumps(config.to_dict(), indent=4))

class CfgNode:
    ""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return self._str_helper(0)

    def _str_helper(self, indent):
        parts = []
        for k, v in self.__dict__.items():
            if isinstance(v, CfgNode):
                parts.append("%s:\n" % k)
                parts.append(v._str_helper(indent + 1))
            else:
                parts.append("%s: %s\n" % (k, v))
        parts = [' ' * (indent * 4) + p for p in parts]
        return "".join(parts)

    def to_dict(self):
        return { k: v.to_dict() if isinstance(v, CfgNode) else v for k, v in self.__dict__.items() }

    def merge_from_dict(self, d):
        self.__dict__.update(d)

    def merge_from_args(self, args):
        
        for arg in args:
            keyval = arg.split('=')
            assert len(keyval) == 2, "expecting each override arg to be of form --arg=value, got %s" % arg
            key, val = keyval # unpack
            try:
                val = literal_eval(val)
            except ValueError:
                pass
            assert key[:2] == '--'
            key = key[2:] # strip the '--'
            keys = key.split('.')
            obj = self
            for k in keys[:-1]:
                obj = getattr(obj, k)
            leaf_key = keys[-1]
            assert hasattr(obj, leaf_key), f"{key} is not an attribute that exists in the config"
            print("command line overwriting config attribute %s with %s" % (key, val))
            setattr(obj, leaf_key, val)

class AdditionDataset(Dataset):
    def get_default_config():
        C = CfgNode()
        C.ndigit = 2
        return C

    def __init__(self, config, split):
        self.config = config
        self.split = split # train/test
        ndigit = self.config.ndigit
        assert ndigit <= 3, "the lines below would be very memory inefficient, in future maybe refactor to support"
        num = (10**ndigit)**2 # total number of possible addition problems with ndigit numbers
        rng = torch.Generator()
        rng.manual_seed(1337)
        perm = torch.randperm(num, generator=rng)
        num_test = min(int(num*0.2), 500) # 20% of the whole dataset, or only up to 500
        self.ixes = perm[:num_test] if split == 'test' else perm[num_test:]

    def get_vocab_size(self):
        return 10 # digits 0..9
    def get_block_size(self):
        return 3*self.config.ndigit + 1 - 1
    def __len__(self):
        return self.ixes.nelement()

    def __getitem__(self, idx):
        ndigit = self.config.ndigit
        idx = self.ixes[idx].item() #using ixes in instantiation
        nd = 10**ndigit #100
        a = idx // nd
        b = idx %  nd
        c = a + b
        astr = f'%0{ndigit}d' % a
        bstr = f'%0{ndigit}d' % b
        cstr = (f'%0{ndigit+1}d' % c)[::-1] # reverse c to make addition easier
        render = astr + bstr + cstr
        dix = [int(s) for s in render] # convert each character to its token index
        x = torch.tensor(dix[:-1], dtype=torch.long)
        y = torch.tensor(dix[1:], dtype=torch.long) # predict the next token in the sequence
        y[:ndigit*2-1] = -1 # we will only train in the output locations. -1 will mask loss to zero
        return x, y

def heat(mat, title: str):
    #mat = tok_emb
    #mat = F.softmax(mat)
    mat_ = mat.to('cpu').detach().numpy().copy()[0,:,:]
    #mat_ = mat_ / np.std(mat_, axis=1).reshape((mat_.shape[0],1))
    #mat_ = mat_ / np.sum(mat_, axis=1).reshape((mat_.shape[0],1))
    #mat_ = (mat_ - np.sum(mat_, axis=1).reshape((mat_.shape[0],1))) / np.std(mat_, axis=1).reshape((mat_.shape[0],1))
    plt.figure()
    #sns.heatmap(mat_, cmap='coolwarm') # Blues, Oranges, coolwarm
    sns.heatmap(mat_, cmap='Blues') # Blues, Oranges, coolwarm
    plt.title(title)

class SelfAttention(nn.Module):
    def __init__(self, config1):
        super().__init__()
        assert config1.n_embd % config1.n_head == 0
        self.c_attn = nn.Linear(config1.n_embd, 3 * config1.n_embd)
        self.c_proj = nn.Linear(config1.n_embd, config1.n_embd)
        self.attn_dropout = nn.Dropout(config1.attn_pdrop)
        self.resid_dropout = nn.Dropout(config1.resid_pdrop)
        self.register_buffer("bias", torch.tril(torch.ones(config1.block_size, config1.block_size))
                                     .view(1, 1, config1.block_size, config1.block_size))
        self.n_head = config1.n_head # 3
        self.n_embd = config1.n_embd # 48        
        self.attnmat = None # additional code

    def forward(self, x): # input x : 4 * 48
        B, T, C = x.size() # (1, 4, 48) or (64, 4, 48) : batch size, sequence length, embedding dimensionality (n_embd)

        q, k ,v  = self.c_attn(x).split(self.n_embd, dim=2) # linear model in q,k,v
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1))) # QK/sqrt(16), three 4 * 4 attention matrix
        att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf')) # always masked in decoder-only transformer
        att = F.softmax(att, dim=-1) # attention matrix
        self.attnmat = att.detach().clone() # store attention matrix for heatmap (additional code)        
        att = self.attn_dropout(att)
        y = att @ v    # (B, nh, T, T) x (B, nh, T, hs) -> (B, nh, T, hs) # attention heads
        y = y.transpose(1, 2).contiguous().view(B, T, C) # re-assemble all head outputs side by side
        #y.size() # (1, 4, 48)
        #y = self.c_proj(y)
        y = self.resid_dropout(self.c_proj(y))
        return y # output y : 4 * 48 (the same as imput)

class Block(nn.Module):
    def __init__(self, config1):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config1.n_embd)
        self.attn = SelfAttention(config1) # instantiation of self-attention function
        self.ln_2 = nn.LayerNorm(config1.n_embd)
        self.mlp = nn.ModuleDict(dict(
            c_fc    = nn.Linear(config1.n_embd, 4 * config1.n_embd),
            act     = nn.ReLU(),
            c_proj  = nn.Linear(4 * config1.n_embd, config1.n_embd),
            dropout = nn.Dropout(config1.resid_pdrop),
        ))
        m = self.mlp
        #self.mlpf = lambda x: m.c_proj(m.act(m.c_fc(x))) # MLP forward
        self.mlpf = lambda x: m.dropout(m.c_proj(m.act(m.c_fc(x)))) # MLP forward
        self.attnmat = None # additional

    def forward(self, x):
        x = x + self.attn(x) # using instance of SelfAttention.forward(input)
        x = x + self.mlpf(x)
        #x = x + self.attn(self.ln_1(x)) # using instance of SelfAttention.forward(input)
        #x = x + self.mlpf(self.ln_2(x))
        self.attnmat = self.attn.attnmat # additional code
        return x

class GPT(nn.Module):
    def get_default_config():
        C = CfgNode()
        C.model_type = 'gpt'
        C.n_layer = None
        C.n_head = None
        C.n_embd =  None
        C.vocab_size = None
        C.block_size = None
        C.embd_pdrop = 0.1
        C.resid_pdrop = 0.1
        C.attn_pdrop = 0.1
        return C

    def __init__(self, config1):
        super().__init__()
        self.config1 = config1 # additinal code
        
        assert config1.vocab_size is not None
        assert config1.block_size is not None
        self.block_size = config1.block_size # 6
        type_given = config1.model_type is not None
        params_given = all([config1.n_layer is not None, config1.n_head is not None, config1.n_embd is not None])
        assert type_given ^ params_given # exactly one of these (XOR)
        if type_given:
            config1.merge_from_dict({
                'gpt2':         dict(n_layer=12, n_head=12, n_embd=768),  # 124M params
                'gpt-nano':     dict(n_layer=3, n_head=3, n_embd=48), # 85680 params
                'gpt-supernano4':dict(n_layer=1, n_head=1, n_embd=48),
                'gpt-supernano5':dict(n_layer=2, n_head=2, n_embd=10),
                #'gpt-supernano7':dict(n_layer=2, n_head=2, n_embd=4),
            }[config1.model_type])
        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(config1.vocab_size, config1.n_embd), # 10, 48 (4 * 48 matrix)
            wpe = nn.Embedding(config1.block_size, config1.n_embd), # 6, 48  (4 * 48 matrix)
            drop = nn.Dropout(config1.embd_pdrop),
            h = nn.ModuleList([Block(config1) for _ in range(config1.n_layer)]), # 3 layers of Block (calls instance of Block class)
            ln_f = nn.LayerNorm(config1.n_embd), # 48
        ))
        self.lm_head = nn.Linear(config1.n_embd, config1.vocab_size, bias=False) # 48, 10 (4 * 10 matrix)
        self.apply(self._init_weights) # initialize the weights and biases in the model
        for pn, p in self.named_parameters():
            if pn.endswith('c_proj.weight'):
                torch.nn.init.normal_(p, mean=0.0, std=0.02/math.sqrt(2 * config1.n_layer))
        n_params = sum(p.numel() for p in self.transformer.parameters())
        print("number of parameters: %.f" % (n_params,)) # without the parameter of lm_head (the last layer): vacoab_size * n_embd
    
    def _init_weights(self, module): # initial weights based on random normal variable N(0, 0.02)
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)

    def configure_optimizers(self, train_config): # Note that input config is for TRAIN
        decay = set()
        no_decay = set()
        whitelist_weight_modules = (torch.nn.Linear, )
        blacklist_weight_modules = (torch.nn.LayerNorm, torch.nn.Embedding)
        for mn, m in self.named_modules():
            for pn, p in m.named_parameters():
                fpn = '%s.%s' % (mn, pn) if mn else pn # full param name
                if pn.endswith('bias'):
                    no_decay.add(fpn)
                elif pn.endswith('weight') and isinstance(m, whitelist_weight_modules):
                    decay.add(fpn)
                elif pn.endswith('weight') and isinstance(m, blacklist_weight_modules):
                    no_decay.add(fpn)
        param_dict = {pn: p for pn, p in self.named_parameters()}
        inter_params = decay & no_decay
        union_params = decay | no_decay
        assert len(inter_params) == 0, "parameters %s made it into both decay/no_decay sets!" % (str(inter_params), )
        assert len(param_dict.keys() - union_params) == 0, "parameters %s were not separated into either decay/no_decay set!" \
                                                    % (str(param_dict.keys() - union_params), )
        optim_groups = [
            {"params": [param_dict[pn] for pn in sorted(list(decay))], "weight_decay": train_config.weight_decay},
            {"params": [param_dict[pn] for pn in sorted(list(no_decay))], "weight_decay": 0.0},
        ]
        optimizer = torch.optim.AdamW(optim_groups, lr=train_config.learning_rate, betas=train_config.betas)
        return optimizer

    def forward(self, idx, targets=None, heat_=False): # main function of GPT (in training, evaluation and generation)
        config1 = self.config1
        device = idx.device #"cpu"
        b, t = idx.size() # b=1, t=sequence length (4 or 6)
        #assert t <= self.block_size, f"Cannot forward sequence of length {t}, block size is only {self.block_size}"
        pos = torch.arange(0, t, dtype=torch.long, device=device).unsqueeze(0) # shape (1, t)
        #pos.data # [[0, 1, 2, 3]] or [[0, 1, 2, 3, 4, 5]]

        tok_emb = self.transformer.wte(idx) # token embeddings of shape (b, t, n_embd)
        pos_emb = self.transformer.wpe(pos) # position embeddings of shape (1, t, n_embd)
        #tok_emb.size(), pos_emb.size() # (4 * 48) or (6 * 48)        

        # main model part
        #x = tok_emb + pos_emb
        x = self.transformer.drop(tok_emb + pos_emb)
        for block in self.transformer.h:
            x = block(x)        
        #x = self.transformer.ln_f(x)
        logits = self.lm_head(x)
        
        if heat_: # heatmap option when heat_=True
            #heat(tok_emb,'token embedding')
            #heat(pos_emb,'position embedding')            
            #x = tok_emb + pos_emb
            x = self.transformer.drop(tok_emb + pos_emb)
            heat(x,'token + position embedding')
            for block in self.transformer.h:
                x = block(x) # using instance of Block.forward(x)
                #print(block.attnmat)
                plt.figure()
                #for j in range(config.model.n_head):
                for j in range(config1.n_head):
                    plt.subplot(2,2,j+1)
                    mat = block.attnmat[:,j,:,:]
                    mat_ = mat.to('cpu').detach().numpy().copy()[0,:,:]
                    sns.heatmap(mat_, cmap='Oranges')
                    plt.title('attention matrix')
                    #heat(block.attnmat[:,j,:,:],'attention matrix')
                heat(x,'transformer-block output')
            #x = self.transformer.ln_f(x)
            #heat(x,'layer-norm')
            logits = self.lm_head(x)
            heat(logits,'logits output (lm_head)')
        
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-1)
        #logits.data
        return logits, loss

    def generate(self, idx, max_new_tokens, temperature=1.0, do_sample=False, top_k=None): # for evaluation
        #usage: d1d2d3 = model.generate(d1d2, ndigit+1, do_sample=False)
        for _ in range(max_new_tokens):
            #idx_cond = idx if idx.size(1) <= self.block_size else idx[:, -self.block_size:]
            #logits, _ = self(idx_cond) # model.forward(idx)
            logits, _ = model(idx)
            logits = logits[:, -1, :] / temperature # using last row
            #if top_k is not None:
            #    v, _ = torch.topk(logits, top_k)
            #    logits[logits < v[:, [-1]]] = -float('Inf')
            probs = F.softmax(logits, dim=-1)
            #if do_sample:
            #    idx_next = torch.multinomial(probs, num_samples=1)
            #else:
            #    _, idx_next = torch.topk(probs, k=1, dim=-1)
            _, idx_next = torch.topk(probs, k=1, dim=-1)
            idx = torch.cat((idx, idx_next), dim=1)
            #print(idx.data) # eg: [[9,0,5,3,3]]
        return idx # outputs the appended with a prediction

class Trainer:
    def get_default_config():
        C = CfgNode()
        C.device = 'cpu'
        C.num_workers = 0
        C.max_iters = None
        C.batch_size = 64
        C.learning_rate = 5e-3
        C.betas = (0.9, 0.95)
        C.weight_decay = 0.1 # only applied on matmul weights
        C.grad_norm_clip = 1.0
        return C # output is config

    def __init__(self, config, model, train_dataset):
        self.config = config
        self.model = model
        self.optimizer = None
        self.train_dataset = train_dataset
        self.callbacks = defaultdict(list) # for callback during training
        self.device = config.device
        self.model = self.model.to(self.device)
        self.iter_num = 0
        self.iter_time = 0.0
        self.iter_dt = 0.0

    def add_callback(self, onevent: str, callback):
        self.callbacks[onevent].append(callback)

    def set_callback(self, onevent: str, callback): # outputs information during training
        # onevent = 'on_batch_end'
        # callback = batch_end_callback function
        self.callbacks[onevent] = [callback]

    def trigger_callbacks(self, onevent: str):
        # onevent = 'on_batch_end'
        for callback in self.callbacks.get(onevent, []):
            callback(self)

    def run(self): # main training loop (Backpropagation)
        model, config = self.model, self.config
        self.optimizer = model.configure_optimizers(config)
        train_loader = DataLoader(
            self.train_dataset,
            sampler=torch.utils.data.RandomSampler(self.train_dataset, replacement=True, num_samples=int(1e10)),
            shuffle=False,
            pin_memory=True,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
        )
        model.train()
        self.iter_num = 0 # counter of iteration
        self.iter_time = time.time()
        data_iter = iter(train_loader)
        while True:
            try:
                batch = next(data_iter)
            except StopIteration:
                data_iter = iter(train_loader)
                batch = next(data_iter)
            batch = [t.to(self.device) for t in batch]
            x, y = batch

            logits, self.loss = model(x, y)

            model.zero_grad(set_to_none=True) # initialize to zero 
            self.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_norm_clip)
            self.optimizer.step()

            self.trigger_callbacks('on_batch_end')
            self.iter_num += 1
            tnow = time.time()
            self.iter_dt = tnow - self.iter_time
            self.iter_time = tnow
            if config.max_iters is not None and self.iter_num >= config.max_iters: # stop at count >= 2000 (default)
                break

#### main code (adder.py)
def get_config(): # config for all steps (model, learning)
    C = CfgNode()
    C.system = CfgNode()
    C.system.seed = 3407
    C.system.work_dir = './out/adder'
    
    C.data = AdditionDataset.get_default_config()

    C.model = GPT.get_default_config()
    C.model.model_type = 'gpt-nano'
    C.model.model_type = 'gpt-supernano4'
    #C.model.model_type = 'gpt-supernano5'

    C.trainer = Trainer.get_default_config()
    
    # for gpt-nano ((3,3,48), #param = 85680)
    C.trainer.max_iters = 6000 # needs 1500 for 95% if target is reversed. If non-reverse needs 3500 for 80%.
    C.trainer.learning_rate = 5e-4 # the model we're using is so small that we can go a bit faster
        
    # for gpt-supernano4 (original, (1,1,48), #param = 29136) # 97%
    #C.trainer.max_iters = 500 # 5000
    C.trainer.max_iters = iters
    C.trainer.learning_rate = 5e-4
    return C

config = get_config()
config.trainer.max_iters = iters
st.write("繰り返し数:", config.trainer.max_iters)
#config.merge_from_args(sys.argv[1:])
#print(config)
setup_logging(config)
set_seed(config.system.seed)

train_dataset = AdditionDataset(config.data, split='train')
test_dataset  = AdditionDataset(config.data, split='test')

config.model.vocab_size = train_dataset.get_vocab_size() # 10
config.model.block_size = train_dataset.get_block_size() # 6
model = GPT(config.model)

trainer = Trainer(config.trainer, model, train_dataset)

def eval_split(trainer, split, max_batches=None):
    dataset = {'train':train_dataset, 'test':test_dataset}[split]
    ndigit = config.data.ndigit
    results = []
    mistakes_printed_already = 0
    factors = torch.tensor([[10**i for i in range(ndigit+1)][::-1]]).to(trainer.device)
    loader = DataLoader(dataset, batch_size=100, num_workers=0, drop_last=False)
    for b, (x, y) in enumerate(loader):
        x = x.to(trainer.device)
        d1d2 = x[:, :ndigit*2]
        d1d2d3 = model.generate(d1d2, ndigit+1, do_sample=False) # using greedy argmax, not sampling
        d3 = d1d2d3[:, -(ndigit+1):]
        d3 = d3.flip(1) # reverse the digits to their "normal" order
        d1i = (d1d2[:,:ndigit] * factors[:,1:]).sum(1)
        d2i = (d1d2[:,ndigit:ndigit*2] * factors[:,1:]).sum(1)
        d3i_pred = (d3 * factors).sum(1)
        d3i_gt = d1i + d2i # manually calculate the ground truth
        correct = (d3i_pred == d3i_gt).cpu() # Software 1.0 vs. Software 2.0 fight RIGHT on this line haha
        for i in range(x.size(0)):
            results.append(int(correct[i]))
            if not correct[i] and mistakes_printed_already < 3: # only print up to 5 mistakes to get a sense
                mistakes_printed_already += 1
                print("GPT claims that %d + %d = %d but gt is %d" % (d1i[i], d2i[i], d3i_pred[i], d3i_gt[i]))
        if max_batches is not None and b+1 >= max_batches:
            break
    rt = torch.tensor(results, dtype=torch.float)
    print("%s final score: %d/%d = %.2f%% correct" % (split, rt.sum(), len(results), 100*rt.mean()))
    return rt.sum()
top_score = 0
def batch_end_callback(trainer):
    global top_score
    if trainer.iter_num % 100 == 0:
        print(f"iter_dt {trainer.iter_dt * 1000:.2f}ms; iter {trainer.iter_num}: train loss {trainer.loss.item():.5f}")
    if trainer.iter_num % 100 == 0:
        train_max_batches = {1: None, 2: None, 3: 5}[config.data.ndigit] # if ndigit=2 we can afford the whole train set, ow no
        model.eval()
        with torch.no_grad():
            train_score = eval_split(trainer, 'train', max_batches=train_max_batches)
            test_score  = eval_split(trainer, 'test',  max_batches=None)   
        score = train_score + test_score
        if score > top_score:
            top_score = score
            print(f"saving model with new top score of {score}")
            ckpt_path = os.path.join(config.system.work_dir, "model.pt")
            torch.save(model.state_dict(), ckpt_path)
        model.train()

trainer.set_callback('on_batch_end', batch_end_callback)
trainer.run()

model.eval();
with torch.no_grad():
    train_score = eval_split(trainer, 'train', max_batches=50)
    test_score  = eval_split(trainer, 'test',  max_batches=50)

# performance illustration (run a input through the model)
d1d2 = torch.tensor([[9,0,5,3]]) # prompt
d1d2 = torch.tensor([[9,0,5,7]]) # prompt
ndigit = config.data.ndigit
factors = torch.tensor([[10**i for i in range(ndigit+1)][::-1]]).to(trainer.device) # [100, 10, 1]
with torch.no_grad():
    d1d2d3 = model.generate(d1d2, ndigit+1, do_sample=False) # prediction by GPT with prompt (input sequence)
    d3 = d1d2d3[:, -(ndigit+1):]
    d3 = d3.flip(1) # reverse the digits
#d1d2, d1d2d3 # raw predited value by our (pretrained) GPT (thi includes input seq)
d1i = (d1d2[:,:ndigit] * factors[:,1:]).sum(1)
d2i = (d1d2[:,ndigit:ndigit*2] * factors[:,1:]).sum(1)
d3i_pred = (d3 * factors).sum(1)
d3i_gt = d1i + d2i
print("%d + %d = %d but true is %d" % (d1i, d2i, d3i_pred, d3i_gt))


######### visualization of GPT and learning process #########
# at the learning is finished (main instance is "model")
# for generation using forward function:
set_seed(config.system.seed)
idx = [[9,0,5,3]]
idx = [[0,0,0,1]]
#logits, loss = model(torch.tensor(idx).to('cpu'), heat_=True)


#### detailed example
# note that this is a model WITHOUT layer-normalization
# eg. 90 + 53 = 143: this is from [9,0,5,3] to reversed [3,4,1], then 3 is correct answer
# with minGPT-supernano4 (layer=1, head=1, emb=48)

# attention part
set_seed(config.system.seed)
#idx = torch.tensor([[9,0,5,3]]).to('cpu')
idx = torch.tensor(idx_test).to('cpu')
plt.rcdefaults()

b, t = idx.size() # b=1, t=sequence length (4 or 6)
pos = torch.arange(0, t, dtype=torch.long, device='cpu').unsqueeze(0)
tok_emb = model.transformer.wte(idx)
pos_emb = model.transformer.wpe(pos)
x = tok_emb + pos_emb
x_ = x.detach().clone().numpy()
tok_ = tok_emb.detach().clone().numpy()
#heat(x,'token + position')

x = model.transformer.drop(x)
x1 = x.detach().clone().numpy()
heat(x,'token + position')

B, T, C = x.size() # (1, 4, 48) or (64, 4, 48) : batch size, sequence length, embedding dimensionality (n_embd)
#model.transformer.h[0].attn.c_attn(x)
a3 = model.transformer.h[0].attn.c_attn.weight
a4 = model.transformer.h[0].attn.c_attn.bias
#x @ a3.T + a4.T  # This equals .c_attn(x)
a3_, a4_ = a3.T.detach().clone().numpy(), a4.T.detach().clone().numpy()
plt.figure(); sns.heatmap(a3_, cmap='Purples'); plt.title('attn.c_attn.weight')

q3 = a3.T[:,0:48]; k3 = a3.T[:,48:96]; v3 = a3.T[:,96:144]
q3_, k3_, v3_ = q3.detach().clone().numpy(), k3.detach().clone().numpy(), v3.detach().clone().numpy()
plt.figure(); sns.heatmap(q3_, cmap='Purples'); plt.title('query.weight')
plt.figure(); sns.heatmap(k3_, cmap='Purples'); plt.title('key.weight')
plt.figure(); sns.heatmap(v3_, cmap='Purples'); plt.title('value.weight')

q, k, v = model.transformer.h[0].attn.c_attn(x).split(model.transformer.h[0].attn.n_embd, dim=2)        
q_, k_, v_ = q.detach().clone().numpy(), k.detach().clone().numpy(), v.detach().clone().numpy()
heat(q,'query')
heat(k,'key')
heat(v,'value')
q2 = q.view(B, T, model.transformer.h[0].attn.n_head, C // model.transformer.h[0].attn.n_head).transpose(1, 2) # (B, nh, T, hs) = (1, 3, 4, 16)
k2 = k.view(B, T, model.transformer.h[0].attn.n_head, C // model.transformer.h[0].attn.n_head).transpose(1, 2) # (B, nh, T, hs) = (1, 3, 4, 16)
v2 = v.view(B, T, model.transformer.h[0].attn.n_head, C // model.transformer.h[0].attn.n_head).transpose(1, 2) # (B, nh, T, hs) = (1, 3, 4, 16)

att = (q2 @ k2.transpose(-2, -1)) * (1.0 / math.sqrt(k2.size(-1))) # QK/sqrt(16)
att_ = att.detach().clone().numpy()[0,0,:,:]
att = att.masked_fill(model.transformer.h[0].attn.bias[:,:,:T,:T] == 0, float('-inf'))
att = F.softmax(att, dim=-1)
att_2 = att.detach().clone().numpy()[0,0,:,:]
plt.figure(); sns.heatmap(att_2, cmap='Oranges'); plt.title('(masked) self-attention matrix')
att = model.transformer.h[0].attn.attn_dropout(att)
att_3 = att.detach().clone().numpy()[0,0,:,:]

y = att @ v2
y = y.transpose(1, 2).contiguous().view(B, T, C) # re-assemble all head outputs side by side
y_ = y.detach().clone().numpy()
heat(y,'multi-head attention output (weight-ave. of V)')

#model.transformer.h[0].attn.c_proj(y)        
a5 = model.transformer.h[0].attn.c_proj.weight
a6 = model.transformer.h[0].attn.c_proj.bias
#y @ a5.T + a6.T
a5_, a6_ = a5.T.detach().clone().numpy(), a6.T.detach().clone().numpy()
y2 = model.transformer.h[0].attn.resid_dropout(model.transformer.h[0].attn.c_proj(y))
y_2 = y2.detach().clone().numpy()
plt.figure(); sns.heatmap(a5_, cmap='Purples'); plt.title('attn.c_proj.weight')
heat(y2,'final attention output')

# mlp (feedforward NN) part
x2 = x + y2   # x = x + attn(x)
x2_ = x2.detach().clone().numpy()
heat(x2,'x + attention(x)')
#model.transformer.h[0].mlp.c_fc(x2)
a7 = model.transformer.h[0].mlp.c_fc.weight
a8 = model.transformer.h[0].mlp.c_fc.bias
#x2 @ a7.T + a8.T
a7_, a8_ = a7.T.detach().clone().numpy(), a8.T.detach().clone().numpy()
plt.figure(); sns.heatmap(a7_, cmap='Purples'); plt.title('mlp.c_fc.weight')

x4 = model.transformer.h[0].mlp.act(model.transformer.h[0].mlp.c_fc(x2))
x4_ = x4.detach().clone().numpy()
heat(x4,'ReLU activated')
#model.transformer.h[0].mlp.c_proj(x4)
a9 = model.transformer.h[0].mlp.c_proj.weight
a10 = model.transformer.h[0].mlp.c_proj.bias
#x4 @ a9.T + a10.T
a9_, a10_ = a9.T.detach().clone().numpy(), a10.T.detach().clone().numpy()
plt.figure(); sns.heatmap(a9_, cmap='Purples'); plt.title('mlp.c_proj.weight')

x5 = model.transformer.h[0].mlp.dropout(model.transformer.h[0].mlp.c_proj(x4))
x5_ = x5.detach().clone().numpy()
heat(x5, 'mlp (FF) output')

x6 = x2 + x5 # x = x + mlpf(x)
x6_ = x6.detach().clone().numpy()
heat(x6, 'transformer-block output (x + mlp(x))')

# final part from transformer block output to logits output
logits = model.lm_head(x6)
a11 = model.lm_head.weight
#x6 @ a11.T
a11_ = a11.T.detach().clone().numpy()
plt.figure(); sns.heatmap(a11_, cmap='Purples'); plt.title('lm_head.weight')
heat(logits,'logits output')
#print(logits)
logits_ = logits.detach().clone().numpy()


##### for streamlit
fig1, ax = plt.subplots()
mat_ = x.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('token + position')
#st.pyplot(fig1)

fig2, ax = plt.subplots()
sns.heatmap(a3_, ax=ax, cmap='Purples')
plt.title('attn.c_attn.weight')
#st.pyplot(fig2)

fig3, ax = plt.subplots()
sns.heatmap(q3_, cmap='Purples')
plt.title('query.weight')
#st.pyplot(fig3)
fig4, ax = plt.subplots()
sns.heatmap(k3_, cmap='Purples')
plt.title('key.weight')
#st.pyplot(fig4)
fig5, ax = plt.subplots()
sns.heatmap(v3_, cmap='Purples')
plt.title('value.weight')
#st.pyplot(fig5)

fig6, ax = plt.subplots()
mat_ = q.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('query')
#st.pyplot(fig6)

fig7, ax = plt.subplots()
mat_ = k.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('key')
#st.pyplot(fig7)

fig8, ax = plt.subplots()
mat_ = v.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('value')
#st.pyplot(fig8)

fig9, ax = plt.subplots()
sns.heatmap(att_2, cmap='Oranges')
plt.title('self-attention matrix')
#st.pyplot(fig9)

fig10, ax = plt.subplots()
mat_ = y.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('multi-head attention output (weight-ave of value)')
#st.pyplot(fig10)

fig11, ax = plt.subplots()
sns.heatmap(a5_, cmap='Purples')
plt.title('attn.c_proj.weight')
#st.pyplot(fig11)

fig12, ax = plt.subplots()
mat_ = y2.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('final attention output')
#st.pyplot(fig12)

fig13, ax = plt.subplots()
mat_ = x2.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('x + attention(x)')
#st.pyplot(fig13)

fig14, ax = plt.subplots()
sns.heatmap(a7_, ax=ax, cmap='Purples')
plt.title('mlp.c_fc.weight')
#st.pyplot(fig14)

fig15, ax = plt.subplots()
mat_ = x4.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('ReLU activated')
#st.pyplot(fig15)

fig16, ax = plt.subplots()
sns.heatmap(a9_, ax=ax, cmap='Purples')
plt.title('mlp.c_proj.weight')
#st.pyplot(fig16)

fig17, ax = plt.subplots()
mat_ = x5.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('mlp output')
#st.pyplot(fig17)

fig18, ax = plt.subplots()
mat_ = x6.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('transformer-block output')
#st.pyplot(fig18)

fig19, ax = plt.subplots()
sns.heatmap(a11_, ax=ax, cmap="Purples")
plt.title('lm_head.weight')
#st.pyplot(fig19)

fig20, ax = plt.subplots()
mat_ = logits.to('cpu').detach().numpy().copy()[0,:,:]
sns.heatmap(mat_, ax=ax, cmap='Blues') # Blues, Oranges, coolwarm
plt.title('logits output')
#st.pyplot(fig20)

st.subheader("Attention: input, embedding, QKV")
cols = st.columns(5)
cols[0].pyplot(fig1); #cols[0].caption("input")   # ← 下にラベル
cols[1].pyplot(fig2)
cols[2].pyplot(fig6)
cols[3].pyplot(fig7)
cols[4].pyplot(fig8)

st.subheader("Attention 2: weghited V")
cols = st.columns(4)
cols[0].pyplot(fig9)
cols[1].pyplot(fig10)
cols[2].pyplot(fig11)
cols[3].pyplot(fig12)

st.subheader("NN part")
cols = st.columns(5)
cols[0].pyplot(fig13)
cols[1].pyplot(fig14)
cols[2].pyplot(fig15)
cols[3].pyplot(fig16)
cols[4].pyplot(fig17)

st.subheader("Output: identification")
cols = st.columns(3)
cols[0].pyplot(fig18)
cols[1].pyplot(fig19)
cols[2].pyplot(fig20)

st.write(idx)
st.write(idx_test)
