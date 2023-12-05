function Y = DAMAGE(X)
% -------------------------------------------------------------------------
% Version: 1.0 (Released: March 2019)
% -------------------------------------------------------------------------
% This script calculates the Diffuse Axonal, Multi-Axis, General Evaluation 
% (DAMAGE) metric: Gabler, L.F., Crandall, J.R. & Panzer, M.B. Ann Biomed 
% Eng, 2018. https://doi.org/10.1007/s10439-018-02179-9.
% -------------------------------------------------------------------------
% Administrative contact: Lee F. Gabler (lgabler@biocorellc.com)
% Research contact: Matthew B. Panzer (panzer@virginia.edu)
% -------------------------------------------------------------------------
% Use of this software is subject to the terms of the software agreement 
% at http://biocorellc.com/software/.
% -------------------------------------------------------------------------
% Input variable:
% X: Timed head kinematics (nx4), where n is the # of time points.
%    Column 1: Time (s)
%    Column 2: X angular acceleration (rad/s/s)
%    Column 3: Y angular acceleration (rad/s/s)
%    Column 4: Z angular acceleration (rad/s/s)
%    Data entered must be measured with respect to the local head
%    coordinate system defined by SAE J211. Do not enter column headers.
%
% Output variable: 
% Y: Data structure containing DAMAGE metric output.
% -------------------------------------------------------------------------
%
% setup
n = length(X);
t = X(:,1);     % time (s)
alp = X(:,2:4); % angular acceleration (rad/s/s)
%
% calculate DAMAGE
B = 2.9903;                                 % (1/m) scale factor
F = [alp(:,1:2),-alp(:,3)];                 % excitation
dmg_i = B*rk4ode(n,t,F);                    % components of DAMAGE
dmg_t = cummax(sum(dmg_i.*dmg_i,2).^(0.5)); % DAMAGE over time
[dmg,~] = max(dmg_t);                       % DAMAGE metric
%
% output
Y.t = t;            % time (s)
Y.damage = dmg;     % DAMAGE metric
Y.damage_i = dmg_i; % DAMAGE components (nx3)
Y.damage_t = dmg_t; % DAMAGE metric over time (nx1)            
end

function x = rk4ode(n,t,F)
% Solve for system displacements of the DAMAGE multibody model using
% Runge-Kutta 4th order method (RK4).
%
% multibody parameters
m = eye(3);                  % mass (kg)
kxx = 32142; kyy = 23493; kzz = 16935; kxy = 0; kyz = 0; kxz = 1636.3;
k = [kxx+kxy+kxz,-kxy,-kxz;  % stiffness matrix (N/m)
     -kxy,kxy+kyy+kyz,-kyz;
     -kxz,-kyz,kxz+kyz+kzz];   
a1 = 5.9148*10^-3;           % damping constant (s)
c = a1*k;                    % proportional damping (Ns/m)
%
% RK4 method
x = zeros(n,3);   % displacements
dx = zeros(n,3);  % velocities
d2x = zeros(n,3); % accelerations
for i = 2:n
    h = t(i)-t(i-1); % time step
    k1x = dx(i-1,:);
    k1v = f(x(i-1,:),dx(i-1,:),F(i-1,:),m,c,k);  
    k2x = dx(i-1,:)+k1v*(0.5*h);
    k2v = f(x(i-1,:)+k1x*(0.5*h),dx(i-1,:)+k1v*(0.5*h),0.5*(F(i-1,:)+F(i,:)),m,c,k);
    k3x = dx(i-1,:)+k2v*(0.5*h);
    k3v = f(x(i-1,:)+k2x*(0.5*h),dx(i-1,:)+k2v*(0.5*h),0.5*(F(i-1,:)+F(i,:)),m,c,k);   
    k4x = dx(i-1,:)+k3v*h;
    k4v = f(x(i-1,:)+k3x*h,dx(i-1,:)+k3v*h,F(i,:),m,c,k);
    kx = (k1x+2*k2x+2*k3x+k4x)/6;
    kv = (k1v+2*k2v+2*k3v+k4v)/6;
    d2x(i,:) = kv;
    dx(i,:) = dx(i-1,:)+kv*h;
    x(i,:) = x(i-1,:)+kx*h;
end
end

function d2x = f(x,dx,F,m,c,k)
% Differential equations for DAMAGE multibody model
d2x(1,1) = (F(1)-c(1,1)*dx(1)-c(1,2)*dx(2)-c(1,3)*dx(3)-k(1,1)*x(1)-k(1,2)*x(2)-k(1,3)*x(3))/m(1,1);
d2x(1,2) = (F(2)-c(2,1)*dx(1)-c(2,2)*dx(2)-c(2,3)*dx(3)-k(2,1)*x(1)-k(2,2)*x(2)-k(2,3)*x(3))/m(2,2);
d2x(1,3) = (F(3)-c(3,1)*dx(1)-c(3,2)*dx(2)-c(3,3)*dx(3)-k(3,1)*x(1)-k(3,2)*x(2)-k(3,3)*x(3))/m(3,3);
end