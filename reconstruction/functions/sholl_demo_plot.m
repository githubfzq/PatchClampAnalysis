<<<<<<< Updated upstream
sholl_tree(gfp_trees{1},20,'-s');
%����ͬ��Բ�ܼ��ȣ�ÿ5��ͬ��Բֻ����һ���������뾶=50������Ч��
f=gcf;h=findobj(f,'Type','Line');
circle=h([4:end]);
circle_hide=circle(setdiff(1:end,1:5:end));
arrayfun(@(x) set(x,'Visible','off'),circle_hide);
%�ı��עλ��
lg=f.Children(1);
lg.Position(1)=1-lg.Position(3);
lg.Box='off';
%ȥ������
ax=f.Children(3);
=======
sholl_tree(gfp_trees{1},20,'-s');
%����ͬ��Բ�ܼ��ȣ�ÿ5��ͬ��Բֻ����һ���������뾶=50������Ч��
f=gcf;h=findobj(f,'Type','Line');
circle=h([4:end]);
circle_hide=circle(setdiff(1:end,1:5:end));
arrayfun(@(x) set(x,'Visible','off'),circle_hide);
%�ı��עλ��
lg=f.Children(1);
lg.Position(1)=1-lg.Position(3);
lg.Box='off';
%ȥ������
ax=f.Children(3);
>>>>>>> Stashed changes
ax.XGrid='off';ax.YGrid='off';