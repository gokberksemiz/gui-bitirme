function [xmea,ymea,speedmea,xas] = guismooth(x,y,speed,M)

x=x';
y=y';
speed=speed';

x=cell2mat(x);
y=cell2mat(y);
speed=cell2mat(speed);

for i = 1: length (speed)
    
    if speed(i) > 3
        speed(i)= 3;
    elseif speed(i) < 0
        speed(i)=-speed(i);        
    end
end


xa=x;
ya=y;

x=x';
y=y';
speed=speed';
%M=50;
M=str2double(M);
xmea=movmean(x,M);
xmea(1)=x(1);
xmea(end)=x(end);
ymea=movmean(y,M);
ymea(1)=y(1);
ymea(end)=y(end);
speedmea=lowpass(speed,1/4);
speedmea=round(speedmea,5,"significant");
for i = 1: length (speedmea)
   
    if speedmea(i) < 0
        speedmea(i)=-speedmea(i);        
    end

end

xmea=int16(round(xmea));
ymea=int16(round(ymea));

xas=xmea';
end


