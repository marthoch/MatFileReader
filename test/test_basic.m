%% creat test file
data = {};

data.val001 = 1;
data.val002 = pi;

data.array = [1:0.5:10];

data.cel = {};
for i = [1:10]
    data.cel{end+1} = [1:10]*i;
end

data.cel2 = {};
for i = [1:10]
    ds = {};
    ds.i = i;
    ds.x = [1:10]*i;
    data.cel2{end+1} = ds; 
end

data.text = 'test';

save('test_basic.mat', 'data', '-v7.3')

% eof