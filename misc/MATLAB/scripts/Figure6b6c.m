D=load('../../Misc/14_sensorwhiteppr.txt');
B=min(D); %load('baseValues_14sensors.txt');
B=repmat(B,size(D,1),1);
D=10*log10(D./B);


S=D(1:750,[1:7 9:15]);
R=reshape(S',size(S,1)*size(S,2),1);

%Xvalues=[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 9]';
Xvalues=[0.5 1 1.5 2 2.5 3 3.5 4 4.5 5:10]';
X=repmat(Xvalues,1,size(S,2)*50);
X=reshape(X',size(S,1)*size(S,2),1);


%% Fit data to y=a/x^b+c
[f,gof]=fit(X,R,'power2','Lower',[-Inf -Inf -Inf],'Upper',[Inf Inf Inf])


%% Plot fitted curve and data
h=figure(1);
p=plot(f,X,R); hold on;
p(1).Color='Red';
set(gca,'XTickLabel',get(gca,'XTickLabel'),'fontsize',12);
set(xlabel('Distance (cm)'),'FontSize',20);
set(ylabel('10 log I/I_0 dB'),'FontSize',20);
%set(title('No PDMS, white paper'),'FontSize',14);
disp(sprintf('R-Square Value %f',gof.rsquare))
%saveas(h,'fit_whitepaper','png');

set(legend('Intensity (Raw)',sprintf('y=%0.2fx^{%2.2f} %0.2f',(f.a),f.b,f.c)),'FontSize',18);

%% Plot calculated distances from sensor readings
h=figure(2)
Xest=((R-f.c)/f.a).^(1/f.b);
Xerror=reshape(Xest-X,length(Xest)/length(Xvalues),length(Xvalues));
errorbar(Xvalues,mean(Xerror),std(Xerror)), hold on;

% set(title('Average error (No PDMS/white paper)'),'FontSize',14);
set(xlabel('distance (cm)'),'FontSize',14);
set(ylabel('Average error (cm)'),'FontSize',14);
%saveas(h,'error_whitepaper','png');


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PRINT PDMS VALUES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

D=load('../../Misc/14_sensorwhiteppr_PDMS.txt');
B=load('../../Misc/baseValues_14sensors.txt');
B=repmat(mean(B),size(D,1),1);
D=10*log10(D./B);


S=D(1:750,[1:7 9:15]);
R=reshape(S',size(S,1)*size(S,2),1);

%Xvalues=[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 9]';
Xvalues=[0.5 1 1.5 2 2.5 3 3.5 4 4.5 5:10]';
X=repmat(Xvalues,1,size(S,2)*50);
X=reshape(X',size(S,1)*size(S,2),1);


%% Fit data to y=a/x^b+c
[fpdms,gof]=fit(X,R,'power2','Lower',[-Inf -Inf -Inf],'Upper',[Inf Inf Inf])


%% Plot fitted curve and data
h=figure(1)
p=plot(fpdms,X,R)
p(2).Color='Blue';
set(xlabel('Distance (cm)'),'FontSize',20);
set(ylabel('10 log I/I_0 dB'),'FontSize',20);
%set(title('No PDMS, white paper'),'FontSize',14);
disp(sprintf('R-Square Value %f',gof.rsquare))
saveas(h,'Figure6b','png');
set(legend('Intensity (raw)',sprintf('y=%0.2fx^{%2.2f} %0.2f',(f.a),f.b,f.c),'Intensity (PDMS)',sprintf('y=%0.2fx^{%2.2f} %0.2f',(fpdms.a),fpdms.b,fpdms.c)),'FontSize',18)


%% Plot calculated distances from sensor readings
h=figure(2), hold on;
Xest=((R-fpdms.c)/fpdms.a).^(1/fpdms.b);
Xerror=reshape(Xest-X,length(Xest)/length(Xvalues),length(Xvalues));
errorbar(Xvalues,mean(Xerror),std(Xerror),'r'), hold on;

set(gca,'XTickLabel',get(gca,'XTickLabel'),'fontsize',12);
set(legend('Raw sensor','PDMS sensor'),'FontSize',18);
% set(title('Average error (No PDMS/white paper)'),'FontSize',14);
set(xlabel('Distance (cm)'),'FontSize',20);
set(ylabel('Average error (cm)'),'FontSize',20);
saveas(h,'Figure6c','png');

