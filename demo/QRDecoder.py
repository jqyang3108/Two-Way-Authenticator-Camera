import decode,detection

path = 'samples/second.png'
test1 = 'samples/first.png'
test2 = 'samples/second.png'
test3 = 'samples/third.png'
test4 = 'qrdecode.png'
savename = 'qrdecode.png'
detection.main(path,savename)
decode.main(savename)
