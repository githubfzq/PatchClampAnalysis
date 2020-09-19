%������Ϊplot_standard_neuron
tr=[green_tr,red_tr];
gfpcolor=[40 110 80]/256;
colr={gfpcolor,'r'};
for op=[1,2]
    %������ת�ǶȲ�����Ԫ������ת�任
    euc_dist=eucl_tree(tr(op));
    cor=[tr(op).X,tr(op).Y,tr(op).Z];
    maxdist=cor(euc_dist==max(euc_dist),:);
    triangle=maxdist-cor(1,:);
    angle=atan(triangle(2)/triangle(1))*180/pi;
    rot=rot_tree(tr(op),[0 0 270+angle]);
    %ƽ�ư�����ԭ��
    cor_rot=[rot.X,rot.Y,rot.Z];
    tran=tran_tree(rot,-cor_rot(1,:,:));
    %��ͼ
    subplot(1,2,op)
    ax(op)=gca;
    ln=plot_tree(tran,[],[],[],[],'-2l');
    arrayfun(@(l) set(l,'Color',colr{op}),ln);
    xyax=get(gca,{'XAxis','YAxis'});
    cellfun(@(a) set(a,'Visible','off'),xyax);
end
%����������
ax(2).Position(1)=ax(1).Position(1)+ax(1).Position(3); %����
ax(2).Position([3,4])=ax(1).Position([3,4]).*[range(ax(2).XLim),range(ax(2).YLim)]...
    ./[range(ax(1).XLim),range(ax(1).YLim)];%�����ڶ���������߶�Ϊ��һ����С
scal=axes('Position',[ax(2).Position(1)+ax(2).Position(3),ax(2).Position(2),...
    200*ax(1).Position([3,4])./[range(ax(1).XLim),range(ax(1).YLim)]]);%��ӱ�����
scal.XAxis.TickLabels={'';'200\mum';''};
scal.YAxis.TickLabels={'';'200\mum';''};
scal.LineWidth=1;
scal.Position(1)=scal.Position(1)-scal.Position(3);
scal.YAxisLocation='right';
set(gcf,'Color','w');