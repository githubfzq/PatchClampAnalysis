fj=Miji;
fj.run("Sholl Analysis (Tracings)...", ...
    "traces/(e)swc=[J:/神经元追踪备份/trace/GFP+/(GFP+)slice_1_red neuron1.swc]"...
    +" image=[]"...
    +" load center=[Start of main path]"...
    +" radius=0"+" enclosing=1"+" _primary=[]"...
    +" infer linear polynomial=[Best fitting degree]"...
    +" linear-norm semi-log log-log"...
    +" normalizer=Area/Volume"+" directory=[]")

% fj.run("Sholl Analysis (Tracings)...", "traces/(e)swc=[J:/神经元追踪备份/trace/GFP+/(GFP+)slice_1_red neuron1.swc] image=[J:/神经元追踪备份/trace/GFP+/(GFP+)slice_1_red neuron1.swc] load center=[Start of main path] radius=0 enclosing=1 #_primary=[] infer linear polynomial=[Best fitting degree] linear-norm semi-log log-log normalizer=Area/Volume directory=[]");