function varargout=imaris_filament_to_swc(filename)

% ��ʽ��
% tree_loaded=imaris_filament_to_swc(filename)
%
% ��Imaris��ѡ���ع��õ�Filament
%
% ���������
% filename: ��Ҫ������swc��ʽ�ļ���
% 
% ���������
% tree_loaded: ���ص��������ı���������tree����
%
% Written by FanZuquan on July,16,2018
%
global trees

javaaddpath("C:\Program Files\Bitplane\Imaris x64 9.0.1\XT\matlab\ImarisLib.jar");
vImarisLib=ImarisLib;
aImarisApplication=vImarisLib.GetApplication(0);
vFactory=aImarisApplication.GetFactory;
vFila=vFactory.ToFilaments(aImarisApplication.GetSurpassSelection);
% vPosi=vFila.GetPositionsXYZ(0);
% vRadi=vFila.GetRadii(0);
% vEdge=vFila.GetEdges(0);vEdge=vEdge+1;
BeginVerInd=vFila.GetBeginningVertexIndex(0);
% vEdge(vEdge(:,2)==BeginVerInd,1)=-1;

vFilaList=vFila.GetFilamentsList(0); %list��mEdge/mPositionsXYZ/mType/mRadii����
edg=[-2 0;vFilaList.mEdges]+1; %����һ��[-1 beginpoint=1]
swc_tr=[cast(edg(:,2),'single'),cast(vFilaList.mTypes,'single'),...
    vFilaList.mPositionsXYZ,vFilaList.mRadii,cast(edg(:,1),'single')];
swc_tr=sortrows(swc_tr);

fileID=fopen(filename,'w+');
fprintf(fileID,'%5d %1d %5.10f %5.10f %5.10f %5.10f %5d\n',swc_tr');
fclose(fileID);
old_tr=load_tree(filename);
[tree_loaded,~]=redirect_tree(old_tr,BeginVerInd+1); % set new root to BeginVerInd from Imaris
swc_tree(tree_loaded,filename);

if nargout==1
    varargout{1}=tree_loaded;
else
    trees {length (trees) + 1} =tree_loaded;
end
