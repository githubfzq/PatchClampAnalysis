%����GFP�ļ��в���
cd GFP
%����ÿ��ͼƬ
for n=1:size(gfp_trees,2)
    gfp_f=figure('Color','w');
    gfp_tree_lines=plot_tree(gfp_trees{n},[],[],[],[],'-2l');
    gfpcolor=[40 110 80]/256;
    for m=1:size(gfp_tree_lines,1)
        gfp_tree_lines(m).Color=gfpcolor;
    end
    gfp_ax(n)=gca;
    gfp_ax(n).XAxis.Visible='off';gfp_ax(n).YAxis.Visible='off';
    gfp_tt=title(gfp_trees{n}.name,'Interpreter','none');
    savefig(gfp_f,[gfp_trees{n}.name,'.fig']);
    saveas(gfp_f,[gfp_trees{n}.name,'.png']);
    gfp_tt.Visible='off';
end
cd ..
%�ϲ�9��ͼΪ3��3����
fmix=figure('Color','w');
ax_mix=copyobj(gfp_ax,fmix);
for n=1:9
    subplot(3,3,n,ax_mix(n));
end
savefig(fmix,'GFP neuron samples.fig');
saveas(fmix,'GFP neuron samples.png');
close all

%����GFP_nearby�ļ��в���
cd GFP_nearby
%����ÿ��ͼƬ,��ɫ��Ϊ��ɫ
for n=1:size(near_trees,2)
    near_f=figure('Color','w');
    near_tree_lines=plot_tree(near_trees{n},[],[],[],[],'-2l');
    for m=1:size(near_tree_lines,1)
        near_tree_lines(m).Color='r';
    end
    near_ax(n)=gca;
    near_ax(n).XAxis.Visible='off';near_ax(n).YAxis.Visible='off';
    near_tt=title(near_trees{n}.name,'Interpreter','none');
    savefig(near_f,[near_trees{n}.name,'.fig']);
    saveas(near_f,[near_trees{n}.name,'.png']);
    near_tt.Visible='off';
end
cd ..
%�ϲ�9��ͼΪ3��3����
fmix=figure('Color','w');
ax_mix=copyobj(near_ax,fmix);
for n=1:6
    subplot(2,3,n,ax_mix(n));
end
savefig(fmix,'GFP_nearby neuron samples.fig');
saveas(fmix,'GFP_nearby neuron samples.png');
close all
