errfig1=errorbar(r,mean_inter_gfp,err_inter_gfp);
hold on;errfig2=errorbar(r,mean_inter_near,err_inter_near);hold off;
errfig1.Marker='.';errfig1.MarkerSize=10;
errfig2.Marker='.';errfig2.MarkerSize=10;
errfig1.Color=[0 0.5 0.5];errfig2.Color='red';
fig=gcf;fig.Color='white';fig.Resize='off';
fig.Name='Sholl analysis';
ax=gca;ax.Box='off';
ax.XAxisLocation='origin';
ax.XAxis.Label.Position(2)=ax.YAxis.Limits(1);
ax.XLabel.String='Distance from the soma(\mum)';
ax.YLabel.String='# of Intersections';
lg=legend('GFP+','GFP+ near');
lg.Box='off';