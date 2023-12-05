function Y = HIC(X)
% -------------------------------------------------------------------------
% Version: 1.0 (Released: March 2019)
% -------------------------------------------------------------------------
% This script calculates the Head Injury Criterion (HIC): Versace, J. A
% Review of the Severity Index. Warrendale: SAE International, 1971.
% -------------------------------------------------------------------------
% Administrative contact: Lee F. Gabler (lgabler@biocorellc.com)
% -------------------------------------------------------------------------
% Use of this software is subject to the terms of the software agreement 
% at http://biocorellc.com/software/.
% -------------------------------------------------------------------------
% Input variable:
% X: Timed head kinematics (nx4), where n is the # of time points.
%    Column 1: Time (s)
%    Column 2: X CG linear acceleration (g)
%    Column 3: Y CG linear acceleration (g)
%    Column 4: Z CG linear acceleration (g)
%    Data entered must be measured with respect to the local head
%    coordinate system defined by SAE J211. Do not enter column headers.
%
% Output variable: 
% Y: Data structure containing HIC metric output.
% ------------------------------------------------------------------------- 
%
% setup 
n = length(X); 
t = X(:,1);   % time (s)
a = X(:,2:4); % linear acceleration (g)
%
% calculate HIC
hic = 0;
hic_t = zeros(n,1);
V = zeros(n,1);
A = sum(a.*a,2).^(0.5);% resultant linear acceleration (g)
for i = 2:n
    V(i) = V(i-1)+0.5*(A(i)+A(i-1))*(t(i)-t(i-1));% velocity (g*s)
    for j = i-1:-1:1
        dt = t(i)-t(j);
        if dt<0.015% 15 ms limit
            h = dt*((V(i)-V(j))/dt)^2.5;
            if h>hic
                hic = h;
                hic_t(i) = hic;
                tmin = t(j);
                tmax = t(i); 
            end
        end
    end
    if hic_t(i)<hic_t(i-1)
        hic_t(i) = hic_t(i-1);
    end
end
%
% output
Y.t = t;         % time (s)
Y.hic_t1 = tmin; % HIC t1 (s)
Y.hic_t2 = tmax; % HIC t2 (s)  
Y.hic = hic;     % HIC metric
Y.hic_t = hic_t; % HIC metric over time (nx1)     
end






